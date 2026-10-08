"""The doubling ladder's odd rungs on nec2c EK with its free-end cap zeroed
(nec2c-nocap.patch, NOCAP=1), in dbl.jsonl's row shape, for every design.

    python nocap_ladder.py   -> results/nocap.jsonl   (nec2c only)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbl
import nbs
import nocap
import run

OUT = run.OUT / "nocap.jsonl"
OUT.unlink(missing_ok=True)
designs = nbs.load_designs()
trim = run.load_trim()
cases = [(lab, d, trim["designs"][lab]["driven_len_lambda"]) for lab, d in designs.items()]
for lab, d, Ld in cases:
    for n in dbl.ODD:
        deck = dbl.decks(n, lab, d, Ld, True, False)
        z, g = nbs.parse_nec2_printout(nocap.nec2c(deck, True))
        az, el = nbs.split_cuts(g)
        m = nbs.cut_metrics(az, el)
        row = dict(design=lab, nseg_el=n, lane="nec2cEK_nocap", ladder="odd",
                   z=[z.real, z.imag], metrics=m, az=[az[p] for p in sorted(az)],
                   el=[el[t] for t in sorted(el)], error=None, deck_sha256=run.sha(deck),
                   instrument="nec2c 1.3.1 + nec2c-nocap.patch, NOCAP=1")
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(lab, n, round(m["fwd_dbi"], 3), round(m["fb_db"], 2), flush=True)
