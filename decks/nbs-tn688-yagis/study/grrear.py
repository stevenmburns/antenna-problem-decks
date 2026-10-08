"""F/B over ground at grazing: does NBS's range geometry change the rear
the way it does not change the forward gain?

    python grrear.py   -> results/grrear.jsonl, prints a table

0.8 lambda design (the one with a measured F/B, 15 dB) plus the reference
dipole, at 2 and 3 lambda over Sommerfeld ground (eps 13, sigma 0.005),
x5 mesh as in the earlier ground check, bs2 (deck as written) and NEC-4.2.
Fan of elevations 0.25 .. 15 deg, forward (phi 0) AND rear (phi 180).
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbs
import run

M = 5
ELEV = np.arange(0.25, 15.001, 0.25)
THETAS = 90.0 - ELEV


def fan_deck(deck):
    lines = [ln for ln in deck.splitlines() if not ln.startswith("RP")]
    i = lines.index("EN")
    lines[i:i] = [f"RP 0 {len(THETAS)} 2 0000 89.75 0 -0.25 180"]
    return "\n".join(lines) + "\n"


def nec42(deck):
    text = run.run_nec42(deck)
    _, g = nbs.parse_nec2_printout(text)
    f = np.array([g[(round(t, 3), 0.0)] for t in THETAS])
    b = np.array([g[(round(t, 3), 180.0)] for t in THETAS])
    return f, b


def bs2(deck):
    from antennaknobs.engines.momwire import MomwireEngine
    from momwire import BSplineSolver

    eng = MomwireEngine(run.builder_from(deck), solver=BSplineSolver,
                        solver_kwargs={"degree": 2}, ground=("finite", *run.GROUND),
                        extended_kernel=False)
    g = eng.gain_evaluator()(THETAS, np.array([0.0, 180.0]))
    return g[:, 0], g[:, 1]


def main():
    d = nbs.load_designs()["0.8"]
    trim = run.load_trim()
    Ld = trim["designs"]["0.8"]["driven_len_lambda"]
    out = run.OUT / "grrear.jsonl"
    for h in (2.0, 3.0):
        yagi = fan_deck(run.deck_for(d, Ld, M, height_lambda=h, ground=run.GROUND))
        dip = fan_deck(run.dipole_deck(trim["ref_dipole"]["len_lambda"], M, h, run.GROUND))
        for name, fn in (("nec42", nec42), ("bs2", bs2)):
            yf, yb = fn(yagi)
            df, _ = fn(dip)
            row = dict(design="0.8", height_lambda=h, engine=name, m=M,
                       elev=ELEV.tolist(), yagi_fwd=yf.tolist(), yagi_back=yb.tolist(),
                       dipole_fwd=df.tolist(), **run.MW)
            with open(out, "a") as fh:
                fh.write(json.dumps(row) + "\n")
            print(f"h={h} {name}: elev  F/B   Yagi-dipole(fwd)  Yagi-dipole(rear)")
            for e in (0.25, 0.5, 1.0, 2.0, 5.0, 10.0):
                k = int(round((e - 0.25) / 0.25))
                print(f"   {ELEV[k]:5.2f}  {yf[k]-yb[k]:5.2f}  {yf[k]-df[k]:7.3f}  {yb[k]-df[k]:7.3f}")


if __name__ == "__main__":
    main()
