"""Doubling ladder for the NBS TN 688 Yagis, with complex far fields.

    python dbl.py            # appends results/dbl.jsonl

Two ladders, each roughly doubling the per-element segment count:

  odd  (9, 19, 37, 75, 151): NEC-2 deck, feed at the centre SEGMENT.
       nec2c, NEC-4.2, bs2, sinusoidal; nec2c/bs2/sin also with EK.
       Reduced-kernel lanes stop at REDUCED_MAX (segment/radius ~2.5).
  even (10, 20, 40, 80, 160): NEC-5-dialect deck, feed at the centre KNOT
       (EX 0 tag n/2 2), no added segment. NEC-5, razor-2p (EK on: NEC-5
       is permanently extended-kernel).

Every row carries the cuts in dB AND the complex far field on the same
directions, normalised so |e|^2 is the linear gain: e = E * sqrt(G/|E|^2),
i.e. E / sqrt(P_in) up to a constant. That is linear in the currents at a
fixed input power, so it can be Richardson-extrapolated per direction where
dB (a near-cancellation at the rear) cannot. Printout engines give
E_theta/E_phi magnitude and phase; momwire gives the Cartesian radiation
vector M_perp. Components are only compared within one engine.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbs
import run

ODD = (9, 19, 37, 75, 151)
EVEN = (10, 20, 40, 80, 160)
REDUCED_MAX = 37
OUT = run.OUT / "dbl.jsonl"


def printout_fields(text):
    """{(theta, phi): [Re Eth, Im Eth, Re Eph, Im Eph]} from every
    RADIATION PATTERNS row (magnitude, phase in degrees: last four tokens)."""
    out = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if "RADIATION PATTERNS" not in lines[i]:
            i += 1
            continue
        j, started = i + 1, False
        while j < len(lines):
            t = lines[j].split()
            try:
                if len(t) < 11:
                    raise ValueError
                th, ph = float(t[0]), float(t[1])
                mt, pt, mp, pp = (float(x) for x in t[-4:])
            except ValueError:
                if started:
                    break
                j += 1
                continue
            started = True
            et = mt * np.exp(1j * np.deg2rad(pt))
            ep = mp * np.exp(1j * np.deg2rad(pp))
            out[(round(th, 3), round(ph % 360.0, 3))] = [et.real, et.imag, ep.real, ep.imag]
            j += 1
        i = j
    return out


def lane_printout(runner, deck):
    text = runner(deck)
    z, gains = nbs.parse_nec2_printout(text)
    return z, gains, printout_fields(text)


def lane_nec5(deck):
    from antennaknobs.engines import nec5 as n5
    from antennaknobs.engines.nec5 import NEC5Engine

    eng = NEC5Engine(
        builder_from(deck, "nec5"), nec5_exe=run.NEC5, timeout=1200,
        capture_dir=str(run.HERE / "nec5-captures"),
    )
    z = complex(eng.impedance()[0])
    gains, fields = {}, {}
    for thetas, phis in ((np.array([90.0]), run.AZ_PHIS), (run.EL_THETAS, np.array([0.0]))):
        fine = run.nec5_fine_cut(eng, thetas, phis)
        gains.update({(round(t, 3), round(p % 360, 3)): g for (t, p), g in fine.items()})
        # the same deck again: served from the capture cache by its hash
        f = eng.builder.freq
        sources, _ = eng._excitation(f)
        text = eng._run(eng.deck(
            [f], sources=sources,
            rp_grid=(*n5._even_axis(thetas, "theta"), *n5._even_axis(phis, "phi")),
        ))
        fields.update(printout_fields(text))
    return z, gains, fields, run._nseg(eng)


def lane_momwire(deck, solver, kwargs, ek, dialect):
    from antennaknobs.engines.momwire import MomwireEngine

    eng = MomwireEngine(
        builder_from(deck, dialect), solver=solver, solver_kwargs=kwargs,
        extended_kernel=ek,
    )
    z = complex(eng.impedance()[0])
    gain = eng.gain_evaluator()
    wl = eng._wavelength_for(eng.builder.freq)
    sim, coeffs, _ = eng._solved_excited(wl)
    mid, dr, i_mid = eng._segment_dipoles(sim, coeffs)
    k = 2 * np.pi / wl
    fhz = eng.builder.freq * 1e6
    gains, fields = {}, {}
    for thetas, phis in ((np.array([90.0]), run.AZ_PHIS), (run.EL_THETAS, np.array([0.0]))):
        g = gain(thetas, phis)
        v = eng._evaluate_M_perp(
            mid, dr, i_mid, k, np.deg2rad(thetas), np.deg2rad(phis), fhz, vector=True
        )
        for a, t in enumerate(thetas):
            for b, p in enumerate(phis):
                key = (round(float(t), 3), round(float(p) % 360, 3))
                gains[key] = float(g[a, b])
                m = v[a, b]
                fields[key] = [m[0].real, m[0].imag, m[1].real, m[1].imag, m[2].real, m[2].imag]
    return z, gains, fields, run._nseg(eng)


def builder_from(deck, dialect):
    if dialect == "nec2":
        return run.builder_from(deck)
    from types import MappingProxyType

    from antennaknobs import AntennaBuilder, WireSpec
    from antennaknobs.nec_import import parse_nec

    dk = parse_nec(deck, name="nbs688", network=True, dialect=dialect)
    assert dk.dialect == dialect, dk.dialect
    net, tups = dk.network(), dk.wire_tuples(specs=True)

    class DeckBuilder(AntennaBuilder):
        default_params = MappingProxyType({"freq": nbs.FREQ})

        def build_wires(self):
            return tups

        def build_network(self):
            return net

        def build_wire_material(self):
            return WireSpec(radius=dk.dominant_radius())

    return DeckBuilder()


def normalise(gains, fields):
    """Scale each direction's field so |e|^2 = linear gain."""
    out = {}
    for key, g in gains.items():
        f = np.asarray(fields[key], float)
        c = f[0::2] + 1j * f[1::2]
        e2 = float(np.sum(np.abs(c) ** 2))
        s = np.sqrt(10 ** (g / 10) / e2) if e2 > 0 and g > -900 else 0.0
        out[key] = (f * s).tolist()
    return out


def solve(lane, deck):
    from momwire import BSplineSolver, RazorSolver, SinusoidalSolver

    t0 = time.time()
    try:
        nseg = None
        if lane == "nec2c":
            z, gains, fields = lane_printout(run.run_nec2c, deck)
        elif lane == "nec42":
            z, gains, fields = lane_printout(run.run_nec42, deck)
        elif lane == "nec5":
            z, gains, fields, nseg = lane_nec5(deck)
        elif lane == "bs2":
            ek = "\nEK\n" in deck
            z, gains, fields, nseg = lane_momwire(deck, BSplineSolver, {"degree": 2}, ek, "nec2")
        elif lane == "sin":
            ek = "\nEK\n" in deck
            z, gains, fields, nseg = lane_momwire(deck, SinusoidalSolver, {}, ek, "nec2")
        elif lane == "razor2p":
            z, gains, fields, nseg = lane_momwire(
                deck, RazorSolver, {"nec5_quadrature": True}, True, "nec5"
            )
        e = normalise(gains, fields)
        az, el = nbs.split_cuts(gains)
        azc, elc = nbs.split_cuts(e)
        r = {
            "z": [z.real, z.imag] if z is not None else None,
            "nseg": nseg,
            "metrics": nbs.cut_metrics(az, el),
            "az": [az[p] for p in sorted(az)],
            "el": [el[t] for t in sorted(el)],
            "azc": [azc[p] for p in sorted(azc)],
            "elc": [elc[t] for t in sorted(elc)],
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001 - record and keep going
        import traceback

        r = {"error": f"{type(exc).__name__}: {exc}", "tb": traceback.format_exc()[-1500:]}
    r["seconds"] = time.time() - t0
    return r


def decks(n, lab, d, Ld, ek, knot):
    if d is None:
        deck = run.dipole_deck(Ld, 1)
        deck = deck.replace(f"GW 1 {nbs.NSEG_BASE} ", f"GW 1 {n} ").replace(
            f"EX 0 1 {(nbs.NSEG_BASE + 1) // 2} 0", f"EX 0 1 {(n + 1) // 2} 0"
        )
        tag = 1
    else:
        deck = run.deck_for(d, Ld, 1, nseg_base=n, ek=ek)
        tag = next(ln.split()[2] for ln in deck.splitlines() if ln.startswith("EX"))
    if ek and "\nEK\n" not in deck:
        deck = deck.replace("\nEX ", "\nEK\nEX ", 1)
    if knot:
        assert n % 2 == 0
        old = f"EX 0 {tag} {n // 2} 0 1 0"
        assert old in deck, (old, deck[-300:])
        deck = deck.replace(old, f"EX 0 {tag} {n // 2} 2 1 0")
    return deck


def main():
    designs = nbs.load_designs()
    trim = run.load_trim()
    cases = [(lab, d, trim["designs"][lab]["driven_len_lambda"]) for lab, d in designs.items()]
    cases.append(("ref", None, trim["ref_dipole"]["len_lambda"]))
    plan = []
    for i in range(len(ODD)):
        no, ne = ODD[i], EVEN[i]
        for lab, d, Ld in cases:
            red = ("nec2c", "bs2", "sin") if no <= REDUCED_MAX else ()
            plan.append((no, lab, d, Ld, False, False, ("nec42",) + red))
            plan.append((no, lab, d, Ld, True, False, ("nec2c", "bs2", "sin")))
            plan.append((ne, lab, d, Ld, False, True, ("nec5", "razor2p")))
    for n, lab, d, Ld, ek, knot, lanes in plan:
        deck = decks(n, lab, d, Ld, ek, knot)
        tagname = f"dbl_{lab}_n{n}{'_ek' if ek else ''}{'_knot' if knot else ''}.nec"
        (run.DECKS / tagname).write_text(deck)
        for lane in lanes:
            r = solve(lane, deck)
            r.update(
                design=lab, nseg_el=n, lane=lane + ("EK" if ek else ""),
                ladder="even" if knot else "odd", driven_len_lambda=Ld,
                deck_sha256=run.sha(deck), **run.MW,
            )
            with open(OUT, "a") as fh:
                fh.write(json.dumps(r) + "\n")
            m = r.get("metrics") or {}
            print(
                f"{lab} n={n} {r['lane']} Z={r.get('z')} fwd={m.get('fwd_dbi')}"
                f" fb={m.get('fb_db')} nseg={r.get('nseg')} err={r['error']}"
                f" t={r['seconds']:.1f}s",
                flush=True,
            )


if __name__ == "__main__":
    main()
