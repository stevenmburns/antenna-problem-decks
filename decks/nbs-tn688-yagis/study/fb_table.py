"""F/B per design at the rungs where the end-cap families meet.

    python fb_table.py
"""
import json

import numpy as np

R = [json.loads(l) for f in ("results/dbl.jsonl", "results/nocap.jsonl") for l in open(f)]
PHI = np.arange(720) * 0.5
REAR = (PHI >= 90) & (PHI <= 270)
LANES = [("nec2cEK", 37, 75), ("nec2cEK_nocap", 37, 75), ("nec42", 37, 75), ("sinEK", 37, 75),
         ("bs2EK", 37, 75), ("nec5", 40, 80), ("razor2p", 40, 80)]


def fb(d, lane, n):
    r = next(x for x in R if x["design"] == d and x["lane"] == lane and x["nseg_el"] == n)
    a = np.array(r["az"])
    return a[0] - a[360], a[0] - a[REAR].max()


for which, name in ((0, "F/B at 180"), (1, "front over worst rear (90-270)")):
    print(name, "  cols:", " ".join(f"{l}({a}/{b})" for l, a, b in LANES))
    for d in ["0.4", "0.8", "1.2", "2.2", "3.2", "4.2"]:
        print(f"{d:4s}", " | ".join(f"{fb(d, l, a)[which]:5.1f} {fb(d, l, b)[which]:5.1f}"
                                    for l, a, b in LANES))
