"""Is momwire's slow march on the NBS Yagis a fat-wire effect or a defect?

    python radius.py  -> results/radius.jsonl, prints tables

A single centre-fed dipole, length 0.47 lambda at 400 MHz, free space, at
three radii (d/lambda 0.001, 0.003, 0.0085), on a roughly doubling ladder
n = 9, 19, 37, 75, 151, 301, 601 (odd, centre segment) cut off where
segment/radius < 0.7. NEC-5 and razor-2p get n+1 with a knot feed.

Lanes: nec2c, nec2c EK, bs2, bs2 EK, sin, sin EK, NEC-4.2, NEC-5, razor-2p.
Test 1 (thin wire): does bs2 EK converge cleanly at d/lambda 0.001?
Test 2 (EK correction): Z_EK - Z_noEK per rung, bs2 vs nec2c, where the
correction should be small (segment/radius >= 3).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbl
import nbs
import run

LAM = nbs.LAM
L = 0.47
DOVERL = (0.001, 0.003, 0.0085)
NS = (9, 19, 37, 75, 151, 301, 601)
OUT = run.OUT / "radius.jsonl"


def deck(n, a, ek, knot):
    Y = L * LAM / 2
    f = nbs._f
    lines = ["CM radius study dipole", "CE",
             f"GW 1 {n} 0 {f(-Y)} 0 0 {f(Y)} 0 {f(a * LAM)}", "GE 0"]
    if ek:
        lines.append("EK")
    lines.append(f"EX 0 1 {n // 2} 2 1 0" if knot else f"EX 0 1 {(n + 1) // 2} 0 1 0")
    lines += [f"FR 0 1 0 0 {f(nbs.FREQ)} 0", "XQ", "EN"]
    return "\n".join(lines) + "\n"


def z_of(lane, dk):
    from antennaknobs.engines.momwire import MomwireEngine
    from antennaknobs.engines.nec5 import NEC5Engine
    from momwire import BSplineSolver, RazorSolver, SinusoidalSolver

    ek = "\nEK\n" in dk
    if lane == "nec2c":
        return nbs.parse_nec2_printout(run.run_nec2c(dk))[0]
    if lane == "nec42":
        return nbs.parse_nec2_printout(run.run_nec42(dk))[0]
    if lane == "nec5":
        eng = NEC5Engine(dbl.builder_from(dk, "nec5"), nec5_exe=run.NEC5, timeout=1200,
                         capture_dir=str(run.HERE / "nec5-captures"))
        return complex(eng.impedance()[0])
    solver, kw, dialect = {
        "bs2": (BSplineSolver, {"degree": 2}, "nec2"),
        "sin": (SinusoidalSolver, {}, "nec2"),
        "razor2p": (RazorSolver, {"nec5_quadrature": True}, "nec5"),
    }[lane]
    if lane == "razor2p":
        ek = True
    eng = MomwireEngine(dbl.builder_from(dk, dialect), solver=solver, solver_kwargs=kw,
                        extended_kernel=ek)
    return complex(eng.impedance()[0])


def main():
    for dl in DOVERL:
        a = dl / 2
        for n in NS:
            if (L / n) / a < 0.7:
                continue
            jobs = [(n, False, False, ("nec2c", "bs2", "sin", "nec42")),
                    (n, True, False, ("nec2c", "bs2", "sin")),
                    (n + 1, False, True, ("nec5", "razor2p"))]
            for nn, ek, knot, lanes in jobs:
                dk = deck(nn, a, ek, knot)
                for lane in lanes:
                    t0 = time.time()
                    try:
                        z, err = z_of(lane, dk), None
                        if z is None:
                            raise ValueError("no impedance parsed")
                    except Exception as e:  # noqa: BLE001 - record and keep going
                        z, err = None, f"{type(e).__name__}: {e}"
                    row = dict(d_over_lambda=dl, n=nn, lane=lane + ("EK" if ek else ""),
                               dl_over_a=(L / nn) / a,
                               z=None if z is None else [z.real, z.imag], error=err,
                               seconds=time.time() - t0, deck_sha256=run.sha(dk), **run.MW)
                    with open(OUT, "a") as fh:
                        fh.write(json.dumps(row) + "\n")
                    print(f"d/l={dl} n={nn} {row['lane']:8s} D/a={row['dl_over_a']:5.2f} "
                          f"Z={z} err={err} t={row['seconds']:.1f}", flush=True)


if __name__ == "__main__":
    main()
