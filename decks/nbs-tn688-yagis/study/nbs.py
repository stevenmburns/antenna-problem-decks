"""NBS TN 688 (Viezbicke 1976) Yagi decks and four-engine runners.

Geometry, deck writer, ladder rule, printout parsers and pattern metrics,
shared by run.py, sweep04.py and analyze.py.

Conventions:
  - 400 MHz, lengths in metres (lambda = c/400 MHz = 0.749481 m).
  - Elements straight along y, centred on the boom; boom along +x
    (forward = +x = theta 90, phi 0). Reflector at x = -0.2 lambda,
    driven element at x = 0, director k at x = k*S.
  - Element radius = 0.0085 lambda / 2.
  - Base mesh: 9 segments on every element (odd; 9.3-11.6 segments per
    half wave over the 0.386-0.482 lambda elements).
  - Ladder: every GW count x m, EX segment (s-1)*m + (m+1)/2.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

C0 = 299.792458  # m/us -> lambda[m] = C0 / f[MHz]
FREQ = 400.0
LAM = C0 / FREQ
RADIUS = 0.0085 * LAM / 2.0
NSEG_BASE = 9
ETA0 = 376.730313
HERE_DEFAULT = Path(__file__).resolve().parent

LABELS = ["0.4", "0.8", "1.2", "2.2", "3.2", "4.2"]


def load_designs(path=None):
    """The six Table 1 designs from extraction A, keyed by label."""
    path = Path(path or HERE_DEFAULT / "designs-extractA.json")
    d = json.loads(path.read_text())
    out = {}
    for t, lab in zip(d["tabulated_designs"], LABELS, strict=True):
        assert t["boom_length_lambda_as_labelled"] == float(lab), t["id"]
        refl = [e for e in t["elements"] if e["role"] == "reflector"]
        dirs = [e for e in t["elements"] if e["role"] == "director"]
        assert len(refl) == 1 and len(dirs) == t["n_directors"]
        out[lab] = {
            "label": lab,
            "id": t["id"],
            "S": t["director_spacing_lambda"],
            "refl_len": refl[0]["length_lambda"],
            "dir_lens": [e["length_lambda"] for e in dirs],
            "measured_dbd": t["measured_gain_dB"],
            "n_elements": t["n_elements_total_incl_reflector_and_driven"],
        }
    return out


def elements(design, driven_len_lambda, *, dir_override=None):
    """[(role, x_lambda, length_lambda)] reflector, driven, directors."""
    dl = list(design["dir_lens"])
    if dir_override:
        for k, v in dir_override.items():
            dl[k] = v
    els = [("R", -0.2, design["refl_len"]), ("DE", 0.0, driven_len_lambda)]
    for k, L in enumerate(dl, start=1):
        els.append((f"D{k}", round(k * design["S"], 6), L))
    return els


def _f(x):
    return f"{x:.7g}"


def deck_text(
    design,
    driven_len_lambda,
    *,
    m=1,
    height_lambda=None,
    ground=None,
    dir_override=None,
    folded=None,
    rp="cuts",
    comments=(),
    nseg_base=NSEG_BASE,
    ek=False,
):
    """A NEC-2 dialect deck.

    height_lambda: None = free space (GE 0). Otherwise every wire sits at
      z = h*lambda over ground (eps, sigma) = ``ground`` as Sommerfeld GN 2
      (``NOFILE`` appended: NEC-4.2's spelling; nec2c ignores the token).
    folded: None for a straight driven element, else the conductor spacing
      in lambda for a folded dipole (two parallel wires offset in z, ends
      joined by short vertical wires; fed at the centre of the lower wire).
    rp: "cuts" = forward/back + azimuth (E-plane) cut + elevation (H-plane)
      cut; "ground" = low-elevation fan in the forward direction.
    """
    n = nseg_base * m
    z0 = 0.0 if height_lambda is None else height_lambda * LAM
    lines = [f"CM {c}" for c in comments]
    lines.append("CE")
    tag = 0
    ex = None
    for role, x, L in elements(design, driven_len_lambda, dir_override=dir_override):
        X = x * LAM
        Y = L * LAM / 2.0
        if role == "DE" and folded:
            dz = folded * LAM
            tag += 1
            lines.append(
                f"GW {tag} {n} {_f(X)} {_f(-Y)} {_f(z0)} {_f(X)} {_f(Y)} {_f(z0)} {_f(RADIUS)}"
            )
            ex = (tag, (nseg_base // 2) * m + (m + 1) // 2)
            tag += 1
            lines.append(
                f"GW {tag} {n} {_f(X)} {_f(-Y)} {_f(z0 + dz)} {_f(X)} {_f(Y)} {_f(z0 + dz)} {_f(RADIUS)}"
            )
            for yy in (-Y, Y):
                tag += 1
                lines.append(
                    f"GW {tag} 1 {_f(X)} {_f(yy)} {_f(z0)} {_f(X)} {_f(yy)} {_f(z0 + dz)} {_f(RADIUS)}"
                )
            continue
        tag += 1
        lines.append(
            f"GW {tag} {n} {_f(X)} {_f(-Y)} {_f(z0)} {_f(X)} {_f(Y)} {_f(z0)} {_f(RADIUS)}"
        )
        if role == "DE":
            # (s-1)*m + (m+1)/2 with s = (nseg_base+1)/2
            s = (nseg_base + 1) // 2
            ex = (tag, (s - 1) * m + (m + 1) // 2)
    if height_lambda is None:
        lines.append("GE 0")
    else:
        lines.append("GE 1")
        eps, sig = ground
        lines.append(f"GN 2 0 0 0 {_f(eps)} {_f(sig)} NOFILE")
    if ek:
        lines.append("EK")
    lines.append(f"EX 0 {ex[0]} {ex[1]} 0 1 0")
    lines.append(f"FR 0 1 0 0 {_f(FREQ)} 0")
    if rp == "cuts":
        lines.append("RP 0 1 2 0000 90 0 0 180")  # forward (+x) and back (-x)
        lines.append("RP 0 1 720 0000 90 0 0 0.5")  # azimuth (E-plane) cut
        lines.append("RP 0 361 1 0000 0 0 0.5 0")  # phi=0 elevation (H-plane) cut
    elif rp == "ground":
        # theta from zenith: 89.75 .. 75 (elevation 0.25 .. 15 deg), forward
        lines.append("RP 0 60 1 0000 89.75 0 -0.25 0")
    lines.append("EN")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- printouts
_FLOAT = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"


def parse_nec2_printout(text):
    """(Z feed complex, {(theta, phi): total_dB}) from a nec2c / NEC-4.2
    printout. Z from the first ANTENNA INPUT PARAMETERS row (cols 6, 7);
    patterns from every RADIATION PATTERNS block, TOTAL = 5th token."""
    lines = text.splitlines()
    z = None
    p_in = None
    gains = {}
    fine = {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        if z is None and "ANTENNA INPUT PARAMETERS" in ln:
            j = i + 1
            while j < len(lines):
                # NEC-4.2 prints E-format fields with no separating space
                # ("1.35483E-02-2.18691E-02"): pull the E-format numbers out
                # by pattern. Row = tag seg | V re im | I re im | Z re im ...
                vals = re.findall(r"[-+]?\d*\.\d+E[-+]\d+", lines[j])
                head = lines[j].split()[:2]
                if len(vals) >= 6 and all(h.isdigit() for h in head):
                    z = complex(float(vals[4]), float(vals[5]))
                    if len(vals) >= 9:
                        p_in = float(vals[8])
                    break
                j += 1
        if "RADIATION PATTERNS" in ln:
            j = i + 1
            started = False
            while j < len(lines):
                toks = lines[j].split()
                ok = False
                if len(toks) >= 11:
                    try:
                        th, ph, tot = float(toks[0]), float(toks[1]), float(toks[4])
                        ok = True
                    except ValueError:
                        ok = False
                if ok:
                    started = True
                    key = (round(th, 3), round(ph % 360.0, 3))
                    gains[key] = tot
                    try:
                        e2 = float(toks[-4]) ** 2 + float(toks[-2]) ** 2
                    except ValueError:
                        e2 = None
                    if e2 is not None and p_in:
                        # G = 4 pi |rE|^2 / (2 eta0 P_in): the TOTAL column to
                        # ~5 digits instead of the printed 0.01 dB.
                        g = 4 * math.pi * e2 / (2 * ETA0 * p_in)
                        fine[key] = 10 * math.log10(g) if g > 0 else -999.99
                elif started:
                    break
                j += 1
            i = j
            continue
        i += 1
    # every printed TOTAL must agree with the field-derived gain to rounding
    bad = [
        k
        for k, g in gains.items()
        if g > -900 and k in fine and abs(fine[k] - g) > 0.0065
    ]
    if bad:
        raise ValueError(f"field-derived gain disagrees with TOTAL at {bad[:3]}")
    if len(fine) == len(gains) and gains:
        return z, fine
    return z, gains


def nec2_warnings(text):
    keys = ("WARNING", "ERROR", "FAULTY", "RUN ABORTED")
    return sorted(
        {ln.strip()[:120] for ln in text.splitlines() if any(k in ln for k in keys)}
    )


# ----------------------------------------------------------------- metrics
def _crossing(xs, ys, level):
    """First x where ys drops below level, walking from xs[0]; linear interp."""
    for k in range(1, len(xs)):
        if ys[k] < level <= ys[k - 1]:
            t = (ys[k - 1] - level) / (ys[k - 1] - ys[k])
            return xs[k - 1] + t * (xs[k] - xs[k - 1])
    return math.nan


def cut_metrics(az, el):
    """az: {phi: dB} at theta=90 over 0..359.5; el: {theta: dB} at phi=0
    over 0..180. Returns forward/back gain, F/B, the E-plane (azimuth) and
    H-plane (elevation) -3 dB full beamwidths, and the azimuth peak."""
    phis = sorted(az)
    fwd = az[0.0]
    back = az[180.0]
    peak_phi = max(phis, key=lambda p: az[p])
    lvl = fwd - 3.0
    right = [p for p in phis if p <= 180.0]
    left = [0.0] + [
        360.0 - p for p in sorted((p for p in phis if p >= 180.0), reverse=True)
    ]
    left_vals = [az[0.0]] + [
        az[p] for p in sorted((p for p in phis if p >= 180.0), reverse=True)
    ]
    a1 = _crossing(right, [az[p] for p in right], lvl)
    a2 = _crossing(left, left_vals, lvl)
    th_up = sorted((t for t in el if t <= 90.0), reverse=True)  # 90 -> 0
    th_dn = sorted(t for t in el if t >= 90.0)  # 90 -> 180
    h1 = _crossing([90 - t for t in th_up], [el[t] for t in th_up], lvl)
    h2 = _crossing([t - 90 for t in th_dn], [el[t] for t in th_dn], lvl)
    # worst rear lobe, 90..270 deg azimuth (front-to-rear)
    rear = max(az[p] for p in phis if 90.0 <= p <= 270.0)
    return {
        "fwd_dbi": fwd,
        "back_dbi": back,
        "fb_db": fwd - back,
        "fr_db": fwd - rear,
        "peak_phi": peak_phi,
        "peak_dbi": az[peak_phi],
        "bw_e_deg": a1 + a2,
        "bw_h_deg": h1 + h2,
    }


def split_cuts(gains):
    az = {ph: g for (th, ph), g in gains.items() if abs(th - 90.0) < 1e-6}
    el = {th: g for (th, ph), g in gains.items() if abs(ph) < 1e-6}
    return az, el


def richardson(hs, fs):
    """Extrapolate f(h) to h=0 from the last three rungs if the sequence is
    monotone with shrinking steps (estimated order p), else return the
    order-1 pair extrapolation of the last two with a flag."""
    out = {"monotone": None, "order": None, "f_inf": None, "f_inf_p1": None}
    if len(fs) >= 2:
        h1, h2 = hs[-2], hs[-1]
        f1, f2 = fs[-2], fs[-1]
        out["f_inf_p1"] = f2 + (f2 - f1) * h2 / (h1 - h2)
    if len(fs) < 3:
        return out
    (ha, hb, hc), (fa, fb, fc) = hs[-3:], fs[-3:]
    d1, d2 = fb - fa, fc - fb
    mono = d1 * d2 > 0 and abs(d2) < abs(d1)
    out["monotone"] = bool(mono)
    if not mono:
        return out
    r = d1 / d2

    def g(p):
        return (ha**p - hb**p) / (hb**p - hc**p) - r

    lo, hi = 0.05, 8.0
    if g(lo) * g(hi) > 0:
        out["monotone"] = False
        return out
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    p = 0.5 * (lo + hi)
    out["order"] = p
    out["f_inf"] = fc + d2 * hc**p / (hb**p - hc**p)
    return out


def gamma(z, z0=50.0):
    return (z - z0) / (z + z0)


def strip_re(s):
    return re.sub(r"\s+", " ", s)
