"""Leeson stepped-diameter correction for Cebik's tapered 3-element 20 m yagi.

Each tapered element is replaced by the uniform cylinder that Leeson's
procedure gives (D. B. Leeson, W6QHS, *Physical Design of Yagi Antennas*,
ARRL 1992, ch. 8, sec. 8.4, Eqs 8-44 to 8-59 and Tables 8-2/8-3). The
equations are taken from the transcription in fnec-rust
(github.com/dc0sk/fnec-rust, crates/nec_solver/src/taper.rs, commit
1c5a8d6e), which reproduces the book's worked example; this script checks
that example and Cebik's published EZNEC substitutes before using them
(``python leeson.py check``).

    python leeson.py check            # the method against its published cases
    python leeson.py table            # the corrected element of each yagi element
    python leeson.py deck [N] > f.nec # the corrected yagi, N segments per element
    python leeson.py ladder           # nec2c on N = 11, 21, ... (needs nec2c)

The result is in the caller's unit: the method depends only on ratios.
"""

import math
import pathlib
import subprocess
import sys
import tempfile

IN = 0.0254
FREQ = 14.175
# Fig. 23 high-load taper, from the boom outward: (inches of tube, OD inches);
# the 0.5 in tip runs to the element end.
SCHED = [(48, 1.25), (24, 1.0), (20, 0.875), (42, 0.75), (20, 0.625)]
TIP_OD = 0.5
ELEMS = [("refl", 447.3, 0.0), ("de", 421.6, 80.0), ("dir", 393.3, 186.0)]
CONVERGED = complex(29.8, -4.3)  # verdict: bs2 and NEC-5/razor2p


def leeson(sections):
    """Equivalent uniform cylinder of a stepped half-element.

    ``sections``: [(radius, length)] from the centre outward. Returns
    (half-length l', radius a') plus intermediates.
    """
    lh = sum(L for _, L in sections)  # physical half-length l
    # Eq 8-44: length-weighted mean of ln(radius).
    ln_ae = sum(L / lh * math.log(a) for a, L in sections)
    # Eq 8-47: average characteristic impedance of the tapered element.
    ka = 120 * (math.log(2 * lh) - ln_ae - 1)
    # Table 8-2: the taper's corrections to the cylinder's M and N terms and
    # their derivatives, with the resonant phase 2*beta*x = pi*x/l.
    dn = dm = dnp = dmp = 0.0
    x0 = 0.0
    for a, L in sections:
        x1 = x0 + L
        r = math.log(a) - ln_ae
        p1, p0 = math.pi * x1 / lh, math.pi * x0 / lh
        dn += 60 * r * (math.sin(p1) - math.sin(p0))
        dm += -60 * r * (math.cos(p1) - math.cos(p0))
        dnp += 120 / lh * r * (x1 * math.cos(p1) - x0 * math.cos(p0))
        dmp += 120 / lh * r * (x1 * math.sin(p1) - x0 * math.sin(p0))
        x0 = x1
    # Table 8-3: the tapered element's half-wave reactance X0 and effective
    # characteristic impedance Z0 (cylinder constants at beta*l = pi/2).
    m = -21.13 + dm
    xr = (42.545 - dn) * (1 - m / ka)
    z0 = ka - 2 * m - (1 - m / ka) * (56.93 + dnp) - xr / ka * (76.39 + dmp)
    # Eqs 8-54 to 8-59: the cylinder with the same resonance and Z0.
    xr_cyl = 42.545 * (1 + 21.13 / ka)
    fr = 1 - 2 * (xr - xr_cyl) / (math.pi * z0)  # f0'/f0
    lp = lh / fr
    ka_cyl = z0 * fr + 14.67 + 4253 / ka + 68673 / ka**2
    ap = math.exp(math.log(2 * lp) - ka_cyl / 120 - 1)
    return {"l": lp, "a": ap, "ae": math.exp(ln_ae), "ka": ka, "x0": xr, "z0": z0}


def half_sections(full_in):
    """[(radius_in, length_in)] of one yagi element, centre outward."""
    tip = full_in / 2 - sum(L for L, _ in SCHED)
    return [(d / 2, L) for L, d in SCHED] + [(TIP_OD / 2, tip)]


def check():
    """The method against its published cases (all lengths are half-lengths)."""
    rows = []
    # Leeson's worked example (Tables 8-2/8-3): 50 + 50 units, OD 0.8 / 0.4.
    e = leeson([(0.4, 50), (0.2, 50)])
    rows.append(("Leeson worked example", e["l"], 2 * e["a"], 95.70, 0.594))
    # Cebik, "I Want to Build a 3-Element Yagi" pt 3, Fig. 16 (28.5 MHz) table.
    fig16 = [
        ("Cebik Fig. 16 top", [(0, 33, 0.75), (33, 66, 0.625), (66, 100.8, 0.5)], 98.58, 0.631),
        ("Cebik Fig. 16 middle", [(0, 18, 0.75), (18, 60, 0.625), (60, 100.6, 0.5)], 98.67, 0.598),
        ("Cebik Fig. 16 bottom", [(0, 33, 1.0), (33, 66, 0.75), (66, 102.4, 0.5)], 98.39, 0.739),
        # Cebik, "Tapering to Perfection" (Antenna Modeling #10), 14 MHz dipoles.
        ("Cebik amod10 one step far", [(0, 150, 1.0), (150, 204, 0.75)], 201.45, 0.966),
        ("Cebik amod10 one step near", [(0, 50, 1.0), (50, 204, 0.75)], 201.661, 0.792),
        ("Cebik amod10 two steps", [(0, 20, 1.25), (20, 100, 1.0), (100, 205.75, 0.75)], 201.49, 0.889),
        ("Cebik amod10 extreme", [(0, 20, 2.5), (20, 100, 1.0), (100, 208.5, 0.75)], 201.63, 0.895),
    ]
    for name, sch, pl, pd in fig16:
        e = leeson([(d / 2, b - a) for a, b, d in sch])
        rows.append((name, e["l"], 2 * e["a"], pl, pd))
    print("| case | l' (this) | d' (this) | l' (published) | d' (published) |")
    print("| --- | --- | --- | --- | --- |")
    for name, l, d, pl, pd in rows:
        print(f"| {name} | {l:.2f} | {d:.4f} | {pl} | {pd} |")


def corrected():
    out = []
    for name, full, x in ELEMS:
        e = leeson(half_sections(full))
        out.append((name, full, x, e))
    return out


def table():
    print("| element | physical length (in) | corrected length (in) | corrected OD (in) | first-order log-mean OD (in) |")
    print("| --- | --- | --- | --- | --- |")
    for name, full, _x, e in corrected():
        print(f"| {name} | {full:.1f} | {2 * e['l']:.2f} | {2 * e['a']:.4f} | {2 * e['ae']:.4f} |")


def deck(nseg=51):
    if nseg % 2 == 0:
        raise SystemExit("segments per element must be odd (centre feed)")
    cards = []
    for tag, (_name, _full, x, e) in enumerate(corrected(), 1):
        h = e["l"] * IN
        cards.append(
            f"GW {tag} {nseg} {x * IN:.6f} {-h:.6f} 0 {x * IN:.6f} {h:.6f} 0 {e['a'] * IN:.6e}"
        )
    out = [
        "CM Cebik W4RNL 3-el 20 m high-load yagi (3lyg3 Fig. 23), each tapered",
        "CM element replaced by its Leeson uniform equivalent (study/leeson.py)",
        "CE",
        *cards,
        "GE 0",
        f"EX 0 2 {(nseg + 1) // 2} 0 1 0",
        f"FR 0 1 0 0 {FREQ} 0",
        "XQ 0",
        "EN",
    ]
    return "\n".join(out) + "\n"


def zin_nec2c(text, exe="nec2c"):
    with tempfile.TemporaryDirectory() as d:
        # relative names: nec2c refuses long paths
        pathlib.Path(d, "in.nec").write_text(text)
        subprocess.run([exe, "-i", "in.nec", "-o", "out.txt"], cwd=d, check=True, capture_output=True)
        lines = pathlib.Path(d, "out.txt").read_text().splitlines()
    for i, line in enumerate(lines):
        if "ANTENNA INPUT PARAMETERS" in line:
            f = lines[i + 3].split()
            return complex(float(f[6]), float(f[7]))
    raise RuntimeError("no input parameters in nec2c output")


def gamma(z, z0=50.0):
    return (z - z0) / (z + z0)


def ladder(ns=(11, 21, 31, 51, 81, 121, 201, 301)):
    print("| segments per element | N | nec2c Zin (Ω) | Δ from 29.8 − j4.3 (Ω) | abs ΔΓ |")
    print("| --- | --- | --- | --- | --- |")
    for n in ns:
        z = zin_nec2c(deck(n))
        dz = abs(z - CONVERGED)
        dg = abs(gamma(z) - gamma(CONVERGED))
        sign = "+" if z.imag >= 0 else "−"
        print(f"| {n} | {3 * n} | {z.real:.2f} {sign} j{abs(z.imag):.2f} | {dz:.2f} | {dg:.3f} |")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "deck"
    if cmd == "check":
        check()
    elif cmd == "table":
        table()
    elif cmd == "deck":
        sys.stdout.write(deck(int(sys.argv[2]) if len(sys.argv) > 2 else 51))
    elif cmd == "ladder":
        ladder()
    else:
        raise SystemExit(__doc__)
