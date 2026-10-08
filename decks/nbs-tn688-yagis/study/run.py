"""Four-engine runner for the NBS TN 688 Yagis (needs your own licensed NEC-4.2 and NEC-5 binaries; set NEC42_EXE and NEC5_EXE).

    python run.py trim                 # bs2 x5: driven length for X = 0
    python run.py ladder               # all engines, x1/x3/x5/x7, six designs
    python run.py sens                 # driven length +-1 %, all engines, x5
    python run.py dir04                # 0.4 lambda design with D1 = 0.443
    python run.py ground               # bs2 + NEC-4.2 over Sommerfeld ground
    python run.py folded               # folded driven element check (0.8)

Every result line is JSON appended to results/<cmd>.jsonl, and carries the
momwire version/path and the deck sha256.

NEC-4.2 and NEC-5 are licensed black boxes: this script runs the binaries
and reads their printouts only (End-User Reports; NEC-4.2 LLNL-CODE-491368,
NEC-5 LLNL-CODE-746721).
"""

from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import MappingProxyType

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbs

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
DECKS = HERE / "decks-run"
DECKS.mkdir(exist_ok=True)
NEC42 = os.environ.get("NEC42_EXE", os.path.expanduser("~/bin/nec42"))
NEC5 = os.environ.get("NEC5_EXE", os.path.expanduser("~/bin/nec5"))
ENGINES = ("nec2c", "nec42", "bs2", "nec5")
GROUND = (13.0, 0.005)

import momwire  # noqa: E402

MW = {
    "momwire_version": md.version("momwire"),
    "momwire_file": momwire.__file__,
    "antennaknobs_version": md.version("antennaknobs"),
}
print("momwire", MW, flush=True)

AZ_PHIS = np.arange(0.0, 360.0, 0.5)
EL_THETAS = np.arange(0.0, 180.0 + 1e-9, 0.5)
GR_THETAS = np.arange(89.75, 74.99, -0.25)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------- binaries
def run_nec2c(deck):
    with tempfile.TemporaryDirectory(prefix="n2_") as d:
        Path(d, "d.nec").write_text(deck)
        subprocess.run(
            ["nec2c", "-i", "d.nec", "-o", "d.out"],
            cwd=d,
            capture_output=True,
            timeout=600,
        )
        return Path(d, "d.out").read_text(errors="replace")


def run_nec42(deck):
    with tempfile.TemporaryDirectory(prefix="n42_") as d:
        Path(d, "model.nec").write_text(deck)
        env = dict(os.environ, OMP_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4")
        subprocess.run(
            [NEC42, "model.nec", "model.out"],
            cwd=d,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=1200,
            env=env,
        )
        return Path(d, "model.out").read_text(errors="replace")


# ---------------------------------------------------------- importer lanes
def builder_from(deck):
    from antennaknobs import AntennaBuilder, WireSpec
    from antennaknobs.nec_import import parse_nec

    # dialect pinned: a GN card ending NOFILE (NEC-4.2's spelling) would
    # otherwise be read as NEC-5, whose EX addresses a segment END.
    dk = parse_nec(deck, name="nbs688", network=True, dialect="nec2")
    assert dk.dialect == "nec2", dk.dialect
    net = dk.network()
    tups = dk.wire_tuples(specs=True)

    class DeckBuilder(AntennaBuilder):
        default_params = MappingProxyType({"freq": nbs.FREQ})

        def build_wires(self):
            return tups

        def build_network(self):
            return net

        def build_wire_material(self):
            return WireSpec(radius=dk.dominant_radius())

    return DeckBuilder()


def _nseg(eng):
    from antennaknobs.network import as_wire

    tups = getattr(eng, "tups", None)
    return None if tups is None else [as_wire(t).n_seg for t in tups]


def _ground_arg(ground):
    return None if ground is None else ("finite", *ground)


def lane_bs2(deck, mode, ground=None):
    from antennaknobs.engines.momwire import MomwireEngine
    from momwire import BSplineSolver

    from antennaknobs.nec_import import parse_nec

    ek = parse_nec(deck, name="nbs688", dialect="nec2").extended_kernel
    eng = MomwireEngine(
        builder_from(deck),
        solver=BSplineSolver,
        solver_kwargs={"degree": 2},
        ground=_ground_arg(ground),
        extended_kernel=ek,
    )
    z = complex(eng.impedance()[0])
    gain = eng.gain_evaluator()
    res = {"z": [z.real, z.imag], "nseg": _nseg(eng), "extended_kernel": bool(ek)}
    if mode == "cuts":
        az = gain(np.array([90.0]), AZ_PHIS)[0]
        el = gain(EL_THETAS, np.array([0.0]))[:, 0]
        res["az"] = dict(zip(map(float, AZ_PHIS), map(float, az), strict=True))
        res["el"] = dict(zip(map(float, EL_THETAS), map(float, el), strict=True))
    else:
        g = gain(GR_THETAS, np.array([0.0]))[:, 0]
        res["fan"] = dict(zip(map(float, GR_THETAS), map(float, g), strict=True))
    return res


def lane_nec5(deck, mode, ground=None):
    from antennaknobs.engines.nec5 import NEC5Engine

    assert ground is None
    eng = NEC5Engine(
        builder_from(deck),
        nec5_exe=NEC5,
        timeout=1200,
        capture_dir=str(HERE / "nec5-captures"),
    )
    z = complex(eng.impedance()[0])
    res = {"z": [z.real, z.imag], "nseg": _nseg(eng)}
    az = nec5_fine_cut(eng, np.array([90.0]), AZ_PHIS)
    res["az"] = {ph: g for (th, ph), g in az.items()}
    el = nec5_fine_cut(eng, EL_THETAS, np.array([0.0]))
    res["el"] = {th: g for (th, ph), g in el.items()}
    return res


def nec5_fine_cut(eng, thetas, phis):
    """NEC5Engine.gain_grid's run, read to more digits: gain is
    proportional to |E_theta|^2 + |E_phi|^2, so the printed TOTAL (0.01 dB)
    fixes the constant (median over the rows within 30 dB of the peak) and
    the field magnitudes give the rest. Each value is checked against its
    printed TOTAL to rounding."""
    from antennaknobs.engines import nec5 as n5

    f = eng.builder.freq
    sources, p_source = eng._excitation(f)
    deck = eng.deck(
        [f],
        sources=sources,
        rp_grid=(*n5._even_axis(thetas, "theta"), *n5._even_axis(phis, "phi")),
    )
    text = eng._run(deck)
    rows = eng._parse_radiation_fields(text)
    shift = 10.0 * np.log10(eng._to_source_gain(text, p_source))
    gmax = max(g for g, _, _ in rows.values())
    offs = [
        g - 10 * np.log10(et * et + ep * ep)
        for g, et, ep in rows.values()
        if g > -900 and g > gmax - 30 and (et * et + ep * ep) > 0
    ]
    c = float(np.median(offs))
    out = {}
    for (th, ph), (g, et, ep) in rows.items():
        e2 = et * et + ep * ep
        fine = 10 * np.log10(e2) + c if e2 > 0 else -999.99
        if g > -900 and g > gmax - 30:
            assert abs(fine - g) < 0.0062, (th, ph, fine, g)
        out[(float(th), float(ph))] = (fine if g > -900 else g) + shift
    return out


def lane_printout(runner, deck, mode):
    text = runner(deck)
    z, gains = nbs.parse_nec2_printout(text)
    res = {
        "z": [z.real, z.imag] if z is not None else None,
        "warnings": nbs.nec2_warnings(text),
    }
    if mode == "cuts":
        az, el = nbs.split_cuts(gains)
        res["az"], res["el"] = az, el
    else:
        res["fan"] = {th: g for (th, ph), g in gains.items() if abs(ph) < 1e-6}
    return res


def solve(engine, deck, mode="cuts", ground=None):
    t0 = time.time()
    try:
        if engine == "nec2c":
            r = lane_printout(run_nec2c, deck, mode)
        elif engine == "nec42":
            r = lane_printout(run_nec42, deck, mode)
        elif engine == "bs2":
            r = lane_bs2(deck, mode, ground)
        elif engine == "nec5":
            r = lane_nec5(deck, mode, ground)
        r["error"] = None
    except Exception as e:  # noqa: BLE001 - record and keep going
        import traceback

        r = {"error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}
    r["seconds"] = time.time() - t0
    if mode == "cuts" and not r.get("error"):
        az = {float(k): v for k, v in r["az"].items()}
        el = {float(k): v for k, v in r["el"].items()}
        r["metrics"] = nbs.cut_metrics(az, el)
        # keep the raw cuts compact
        r["az"] = [az[p] for p in sorted(az)]
        r["el"] = [el[t] for t in sorted(el)]
    return r


def emit(name, row):
    row.update(MW)
    with open(OUT / f"{name}.jsonl", "a") as fh:
        fh.write(json.dumps(row) + "\n")
    m = row.get("metrics") or {}
    z = row.get("z")
    print(
        f"{name} {row.get('design')} {row.get('variant', '')} m={row.get('m')} {row['engine']}"
        f" Z={z} fwd={m.get('fwd_dbi')} fb={m.get('fb_db')} err={row.get('error')}"
        f" t={row['seconds']:.1f}s",
        flush=True,
    )


def comments(design, Ld, extra=()):
    return [
        f"NBS Technical Note 688 (Viezbicke 1976), Table 1: {design['label']} lambda Yagi,",
        f"{design['n_elements']} elements, 400 MHz, element d/lambda = 0.0085, director spacing"
        f" {design['S']} lambda,",
        "reflector 0.2 lambda behind the driven element, non-conducting boom (none modelled).",
        f"NBS measured gain {design['measured_dbd']} dB re a half-wave dipole (+-0.5 dB).",
        "Driven element: NBS used a lambda/2 FOLDED dipole of untabulated length. This deck",
        f"models it as a STRAIGHT dipole of {Ld:.5f} lambda, trimmed for X = 0 at 400 MHz with",
        "the parasitics present (momwire bs2, x5 mesh). Free space; elements along y, boom +x.",
        *extra,
    ]


def load_trim():
    return json.loads((HERE / "trim.json").read_text())


def deck_for(design, Ld, m, **kw):
    extra = kw.pop("extra", ())
    return nbs.deck_text(design, Ld, m=m, comments=comments(design, Ld, extra), **kw)


# ------------------------------------------------------------------ steps
def trim_bs2(make_deck, L0):
    """Secant on length (lambda) for X = 0 on bs2."""

    def x_of(L):
        return _z_only(make_deck(L)).imag

    L1, L2 = L0, L0 * 1.01
    x1, x2 = x_of(L1), x_of(L2)
    hist = [(L1, x1), (L2, x2)]
    for _ in range(12):
        L3 = L2 - x2 * (L2 - L1) / (x2 - x1)
        x3 = x_of(L3)
        hist.append((L3, x3))
        L1, x1, L2, x2 = L2, x2, L3, x3
        if abs(x3) < 1e-3:
            break
    return L2, hist


def _z_only(deck):
    from antennaknobs.engines.momwire import MomwireEngine
    from momwire import BSplineSolver

    eng = MomwireEngine(
        builder_from(deck), solver=BSplineSolver, solver_kwargs={"degree": 2}
    )
    return complex(eng.impedance()[0])


def cmd_trim():
    designs = nbs.load_designs()
    out = {"mesh_m": 5, "engine": "bs2", **MW, "designs": {}}
    for lab, d in designs.items():
        L, hist = trim_bs2(lambda L, d=d: nbs.deck_text(d, L, m=5), 0.47)
        z = _z_only(nbs.deck_text(d, L, m=5))
        out["designs"][lab] = {
            "driven_len_lambda": L,
            "z_x5": [z.real, z.imag],
            "hist": hist,
        }
        print(lab, L, z, flush=True)
    # reference half-wave dipole alone (same radius), for the ground ratio
    L, hist = trim_bs2(lambda L: dipole_deck(L, 5), 0.48)
    z = _z_only(dipole_deck(L, 5))
    out["ref_dipole"] = {"len_lambda": L, "z_x5": [z.real, z.imag], "hist": hist}
    print("ref", L, z, flush=True)
    (HERE / "trim.json").write_text(json.dumps(out, indent=1))


def dipole_deck(L, m, height_lambda=None, ground=None, rp="cuts"):
    n = nbs.NSEG_BASE * m
    z0 = 0.0 if height_lambda is None else height_lambda * nbs.LAM
    Y = L * nbs.LAM / 2
    f = nbs._f
    lines = [
        f"CM reference half-wave dipole, d/lambda 0.0085, {L:.5f} lambda (bs2 x5 X=0)",
        "CE",
        f"GW 1 {n} 0 {f(-Y)} {f(z0)} 0 {f(Y)} {f(z0)} {f(nbs.RADIUS)}",
    ]
    if height_lambda is None:
        lines.append("GE 0")
    else:
        lines += ["GE 1", f"GN 2 0 0 0 {f(ground[0])} {f(ground[1])} NOFILE"]
    lines.append(f"EX 0 1 {4 * m + (m + 1) // 2} 0 1 0")
    lines.append(f"FR 0 1 0 0 {f(nbs.FREQ)} 0")
    if rp == "cuts":
        lines += [
            "RP 0 1 2 0000 90 0 0 180",
            "RP 0 1 720 0000 90 0 0 0.5",
            "RP 0 361 1 0000 0 0 0.5 0",
        ]
    else:
        lines.append("RP 0 60 1 0000 89.75 0 -0.25 0")
    lines.append("EN")
    return "\n".join(lines) + "\n"


def cmd_ladder(rungs=(1, 3, 5, 7, 9), engines=ENGINES):
    designs = nbs.load_designs()
    trim = load_trim()
    for lab, d in designs.items():
        Ld = trim["designs"][lab]["driven_len_lambda"]
        for m in rungs:
            deck = deck_for(d, Ld, m)
            (DECKS / f"nbs688_{lab}lambda_x{m}.nec").write_text(deck)
            for e in engines:
                r = solve(e, deck)
                r.update(
                    design=lab,
                    m=m,
                    engine=e,
                    driven_len_lambda=Ld,
                    deck_sha256=sha(deck),
                )
                emit("ladder", r)
    # reference dipole ladder (free space), so each engine's own dBd is available
    L = trim["ref_dipole"]["len_lambda"]
    for m in rungs:
        deck = dipole_deck(L, m)
        for e in engines:
            r = solve(e, deck)
            r.update(
                design="ref", m=m, engine=e, driven_len_lambda=L, deck_sha256=sha(deck)
            )
            emit("ladder", r)


def cmd_ek(rungs=(1, 3, 5, 7, 9)):
    """Kernel check: the same ladder with an EK card (nec2c and bs2 honour
    it; NEC-4.2 ignores the card and NEC-5 has none, so they are not rerun)."""
    designs = nbs.load_designs()
    trim = load_trim()
    for lab, d in designs.items():
        Ld = trim["designs"][lab]["driven_len_lambda"]
        for m in rungs:
            deck = deck_for(
                d,
                Ld,
                m,
                ek=True,
                extra=("VARIANT: EK card (extended thin-wire kernel).",),
            )
            for e in ("nec2c", "bs2"):
                r = solve(e, deck)
                r.update(
                    design=lab,
                    m=m,
                    engine=e,
                    variant="EK",
                    driven_len_lambda=Ld,
                    deck_sha256=sha(deck),
                )
                emit("ek", r)


def cmd_sens(m=5):
    designs = nbs.load_designs()
    trim = load_trim()
    for lab, d in designs.items():
        L0 = trim["designs"][lab]["driven_len_lambda"]
        for f in (0.99, 1.01):
            deck = deck_for(d, L0 * f, m)
            for e in ENGINES:
                r = solve(e, deck)
                r.update(
                    design=lab,
                    m=m,
                    engine=e,
                    variant=f"driven x{f}",
                    driven_len_lambda=L0 * f,
                    deck_sha256=sha(deck),
                )
                emit("sens", r)


def cmd_dir04(rungs=(1, 3, 5, 7, 9)):
    d = nbs.load_designs()["0.4"]
    Ld = load_trim()["designs"]["0.4"]["driven_len_lambda"]
    for m in rungs:
        deck = deck_for(
            d,
            Ld,
            m,
            dir_override={0: 0.443},
            extra=(
                "VARIANT: director 0.443 lambda (Fig 9 curve A reading), not"
                " Table 1's 0.424.",
            ),
        )
        for e in ENGINES:
            r = solve(e, deck)
            r.update(
                design="0.4",
                m=m,
                engine=e,
                variant="D1=0.443",
                driven_len_lambda=Ld,
                deck_sha256=sha(deck),
            )
            emit("dir04", r)


def cmd_ground(m=5, heights=(2.0, 3.0), engines=("bs2", "nec42")):
    designs = nbs.load_designs()
    trim = load_trim()
    jobs = [("ref", None)] + list(designs.items())
    for h in heights:
        for lab, d in jobs:
            if lab == "ref":
                deck = dipole_deck(
                    trim["ref_dipole"]["len_lambda"], m, h, GROUND, rp="ground"
                )
            else:
                Ld = trim["designs"][lab]["driven_len_lambda"]
                deck = deck_for(
                    d,
                    Ld,
                    m,
                    height_lambda=h,
                    ground=GROUND,
                    rp="ground",
                    extra=(
                        f"VARIANT: {h} lambda over Sommerfeld ground eps 13,"
                        " sigma 0.005 S/m.",
                    ),
                )
            for e in engines:
                r = solve(e, deck, mode="fan", ground=GROUND)
                r.update(
                    design=lab,
                    m=m,
                    engine=e,
                    height_lambda=h,
                    ground=GROUND,
                    deck_sha256=sha(deck),
                )
                emit("ground", r)


def cmd_folded(rungs=(1, 3, 5), spacing=0.01):
    d = nbs.load_designs()["0.8"]
    Ls = load_trim()["designs"]["0.8"]["driven_len_lambda"]
    # trim the folded element too, on bs2 at x3
    Lf, hist = trim_bs2(lambda L: nbs.deck_text(d, L, m=3, folded=spacing), Ls)
    print("folded trim", Lf, hist[-1], flush=True)
    for m in rungs:
        deck = deck_for(
            d,
            Lf,
            m,
            folded=spacing,
            extra=(
                f"VARIANT: folded driven element, conductors {spacing} lambda"
                f" apart in z, length {Lf:.5f} lambda (bs2 x3 X=0).",
            ),
        )
        for e in ENGINES:
            r = solve(e, deck)
            r.update(
                design="0.8",
                m=m,
                engine=e,
                variant=f"folded {spacing}",
                driven_len_lambda=Lf,
                deck_sha256=sha(deck),
            )
            emit("folded", r)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {
        "trim": cmd_trim,
        "ladder": cmd_ladder,
        "ek": cmd_ek,
        "sens": cmd_sens,
        "dir04": cmd_dir04,
        "ground": cmd_ground,
        "folded": cmd_folded,
    }[cmd]()
