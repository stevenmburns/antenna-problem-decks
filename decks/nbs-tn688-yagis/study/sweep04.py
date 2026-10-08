"""0.4 lambda design: forward gain vs director length, all four engines, x5.
Tests which director length maximises gain (Table 1 is titled 'optimized').

    python sweep04.py   (appends results/sweep04.jsonl)
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbs
import run

d = nbs.load_designs()["0.4"]
Ld = run.load_trim()["designs"]["0.4"]["driven_len_lambda"]
for m in (5, 9):
    for D1 in np.round(np.arange(0.410, 0.4601, 0.0025), 4):
        deck = run.deck_for(
            d,
            Ld,
            m,
            dir_override={0: float(D1)},
            extra=(f"VARIANT: director {D1} lambda (sweep).",),
        )
        for e in run.ENGINES:
            r = run.solve(e, deck)
            r.update(
                design="0.4",
                m=m,
                engine=e,
                variant=f"D1={D1}",
                D1=float(D1),
                driven_len_lambda=Ld,
                deck_sha256=run.sha(deck),
            )
            r.pop("az", None)
            r.pop("el", None)
            run.emit("sweep04", r)
