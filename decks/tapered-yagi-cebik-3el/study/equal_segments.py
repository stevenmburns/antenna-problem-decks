"""Cebik tapered yagi, every segment in an element about the same length
(delta inches): n = max(1, round(L/delta)) per section, centre tube odd."""
import sys
IN = 0.0254
SCHED = [(48, 1.25), (24, 1.0), (20, 0.875), (42, 0.75), (20, 0.625)]
ELEMS = [("refl", 447.3, 0.0), ("de", 421.6, 80.0), ("dir", 393.3, 186.0)]
def deck(delta):
    cards, tag, fed, N = [], 0, None, 0
    for name, full, x in ELEMS:
        half = full / 2
        pts = [0.0]
        for L, _ in SCHED: pts.append(pts[-1] + L)
        pts.append(half)
        dias = [d for _, d in SCHED] + [0.5]
        segs = [(-pts[k], -pts[k-1], dias[k-1]) for k in range(len(pts)-1, 1, -1)]
        segs.append((-pts[1], pts[1], dias[0]))
        segs += [(pts[k], pts[k+1], dias[k]) for k in range(1, len(pts)-1)]
        for y0, y1, d in segs:
            tag += 1
            n = max(1, round((y1 - y0) / delta))
            centre = y0 < 0 < y1
            if centre and n % 2 == 0: n += 1
            if centre and name == "de": fed = (tag, n)
            N += n
            cards.append(f"GW {tag} {n} {x*IN:.6f} {y0*IN:.6f} 0 {x*IN:.6f} {y1*IN:.6f} 0 {d/2*IN:.6e}")
    t, n = fed
    return "\n".join(["CM eq", "CE"] + cards + ["GE 0", f"EX 0 {t} {(n+1)//2} 0 1 0", "FR 0 1 0 0 14.175 0", "XQ 0", "EN"]) + "\n", N
if __name__ == "__main__":
    for delta in (20, 12, 8, 6, 4, 3, 2, 1.5, 1.2):
        txt, N = deck(delta)
        open(f"eq_{delta}.nec", "w").write(txt)
        print(delta, N)
