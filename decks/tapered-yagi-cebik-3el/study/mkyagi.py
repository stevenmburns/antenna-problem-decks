"""Cebik 3-element 20 m 'high-load' tapered yagi (L. B. Cebik, W4RNL,
"I Want to Build a 3-Element Yagi", part 3, Fig. 23 taper schedule and the
20-meter dimension table). Writes a NEC-2 deck (free space).

Element lengths (full, inches): refl 447.3, DE 421.6, dir 393.3.
Spacing: refl-DE 80.0, DE-dir 106.0 (inches).
Taper from centre outward (inches of tube, OD inches):
48 @ 1.25, 24 @ 1.0, 20 @ 0.875, 42 @ 0.75, 20 @ 0.625, end @ 0.5
(end = half-length - 154). Frequency: 14.175 MHz (Cebik's 20 m mid-band
design frequency on his taper study; the 3lyg3 page names no frequency).
Base mesh: each section n = max(1, round(L/20")), centre tube odd.
"""
import sys
IN = 0.0254
SCHED = [(48, 1.25), (24, 1.0), (20, 0.875), (42, 0.75), (20, 0.625)]
ELEMS = [("refl", 447.3, 0.0), ("de", 421.6, 80.0), ("dir", 393.3, 186.0)]

def deck():
    cards, tag, fed = [], 0, None
    for name, full, x in ELEMS:
        half = full / 2
        # breakpoints from centre outward
        pts = [0.0]
        for L, _d in SCHED:
            pts.append(pts[-1] + L)
        pts.append(half)
        dias = [d for _L, d in SCHED] + [0.5]
        # centre wire spans -48..48
        segs = []
        # negative side, outer to inner (excluding centre)
        for k in range(len(pts) - 1, 1, -1):
            segs.append((-pts[k], -pts[k - 1], dias[k - 1]))
        segs.append((-pts[1], pts[1], dias[0]))
        for k in range(1, len(pts) - 1):
            segs.append((pts[k], pts[k + 1], dias[k]))
        for y0, y1, d in segs:
            tag += 1
            L = y1 - y0
            n = max(1, round(L / 20.0))
            centre = y0 < 0 < y1
            if centre and n % 2 == 0:
                n += 1
            if centre and name == "de":
                fed = (tag, n)
            cards.append(
                f"GW {tag} {n} {x*IN:.6f} {y0*IN:.6f} 0 {x*IN:.6f} {y1*IN:.6f} 0 {d/2*IN:.6e}"
            )
    t, n = fed
    out = ["CM Cebik W4RNL 3-el 20 m high-load tapered yagi (3lyg3 Fig. 23)", "CE"]
    out += cards
    out += ["GE 0", f"EX 0 {t} {(n+1)//2} 0 1 0", "FR 0 1 0 0 14.175 0", "XQ 0", "EN"]
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    sys.stdout.write(deck())
