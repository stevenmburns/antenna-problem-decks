"""Tables for verdict.md from results/*.jsonl (no solves).

python3 analyze.py > analysis.txt
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbs

HERE = Path(__file__).resolve().parent
R = HERE / "results"
ENG = ("nec2c", "nec42", "bs2", "nec5")
NAME = {"nec2c": "nec2c", "nec42": "NEC-4.2", "bs2": "momwire bs2", "nec5": "NEC-5"}
LABS = nbs.LABELS
DBD = 2.15


def load(name):
    return [json.loads(line) for line in (R / f"{name}.jsonl").open()]


def series(rows, lab, eng, key, variant=None):
    s = sorted(
        (
            r
            for r in rows
            if r["design"] == lab and r["engine"] == eng and r.get("variant") == variant
        ),
        key=lambda r: r["m"],
    )
    ms = [r["m"] for r in s]
    if key == "R":
        v = [r["z"][0] for r in s]
    elif key == "X":
        v = [r["z"][1] for r in s]
    else:
        v = [r["metrics"][key] for r in s]
    return ms, v


def extrap(ms, vs, use=(5, 7, 9)):
    idx = [ms.index(m) for m in use if m in ms]
    hs = [1.0 / ms[i] for i in idx]
    fs = [vs[i] for i in idx]
    return nbs.richardson(hs, fs)


def best(ms, vs):
    """Converged value: Richardson over (x5, x7, x9) when that triple is
    monotone with shrinking steps AND the fitted order is 0.5..4; otherwise
    the x9 value, labelled (a creeping or turning ladder is not
    extrapolated)."""
    rr = extrap(ms, vs)
    if rr["monotone"] and rr["f_inf"] is not None and 0.5 <= rr["order"] <= 4.0:
        return rr["f_inf"], f"Richardson p={rr['order']:.2f}"
    if rr["monotone"]:
        return vs[-1], f"x9 (monotone but p={rr['order']:.2f}: not extrapolated)"
    return vs[-1], "x9 (not monotone)"


def main():
    designs = nbs.load_designs()
    lad = load("ladder")
    print("momwire", {(r["momwire_version"], r["antennaknobs_version"]) for r in lad})
    print("errors", sum(1 for r in lad if r.get("error")))

    print("\n## Ladder: forward gain dBi per rung")
    for lab in LABS + ["ref"]:
        print(f"\n### {lab}")
        print(
            "| engine | "
            + " | ".join(f"x{m}" for m in (1, 3, 5, 7, 9))
            + " | converged | how |"
        )
        print("|---|" + "---|" * 7)
        for e in ENG:
            ms, vs = series(lad, lab, e, "fwd_dbi")
            b, how = best(ms, vs)
            print(
                f"| {NAME[e]} | "
                + " | ".join(f"{v:.3f}" for v in vs)
                + f" | {b:.3f} | {how} |"
            )

    print("\n## Headline: converged dBd vs NBS")
    conv = {}
    for lab in LABS:
        conv[lab] = {}
        for e in ENG:
            ms, vs = series(lad, lab, e, "fwd_dbi")
            conv[lab][e] = best(ms, vs)[0]
    refg = {e: best(*series(lad, "ref", e, "fwd_dbi"))[0] for e in ENG}
    print("ref dipole dBi:", {e: round(v, 3) for e, v in refg.items()})
    print(
        "| design | NBS dBd | "
        + " | ".join(NAME[e] for e in ENG)
        + " | spread | mean-NBS |"
    )
    print("|---|---|" + "---|" * 6)
    for lab in LABS:
        meas = designs[lab]["measured_dbd"]
        vals = [conv[lab][e] - DBD for e in ENG]
        cells = [f"{v:.2f} ({v - meas:+.2f})" for v in vals]
        mean = sum(vals) / len(vals)
        print(
            f"| {lab} | {meas} | "
            + " | ".join(cells)
            + f" | {max(vals) - min(vals):.3f} | {mean - meas:+.2f} |"
        )
    print("\nsame, engine's own dipole as the reference (dBi - own dipole dBi):")
    for lab in LABS:
        print(lab, {e: round(conv[lab][e] - refg[e], 3) for e in ENG})

    print("\n## x9 raw fwd dBd and x5")
    for lab in LABS:
        print(
            lab,
            {
                e: (
                    round(series(lad, lab, e, "fwd_dbi")[1][2] - DBD, 3),
                    round(series(lad, lab, e, "fwd_dbi")[1][-1] - DBD, 3),
                )
                for e in ENG
            },
        )

    for key, title in (
        ("fb_db", "F/B (180 deg)"),
        ("fr_db", "front-to-rear (worst lobe 90-270)"),
        ("bw_e_deg", "E-plane (azimuth) -3 dB beamwidth"),
        ("bw_h_deg", "H-plane (elevation) -3 dB beamwidth"),
        ("R", "feed R"),
        ("X", "feed X"),
    ):
        print(f"\n## {title} per rung x1/x3/x5/x7/x9")
        for lab in LABS + ["ref"]:
            if lab == "ref" and key in ("fb_db", "fr_db"):
                continue
            print(lab)
            for e in ENG:
                ms, vs = series(lad, lab, e, key)
                print(f"   {NAME[e]:12}", "  ".join(f"{v:7.2f}" for v in vs))

    ek = load("ek")
    print("\n## EK variant (nec2c, bs2): fwd dBi, F/B, X per rung")
    for lab in LABS:
        for e in ("nec2c", "bs2"):
            ms, g = series(ek, lab, e, "fwd_dbi", "EK")
            _, fb = series(ek, lab, e, "fb_db", "EK")
            _, x = series(ek, lab, e, "X", "EK")
            _, g0 = series(lad, lab, e, "fwd_dbi")
            print(
                f"{lab} {e:6} G",
                " ".join(f"{v:.3f}" for v in g),
                "| dG vs no-EK",
                " ".join(f"{a - b:+.3f}" for a, b in zip(g, g0, strict=True)),
                "| F/B",
                " ".join(f"{v:.1f}" for v in fb),
                "| X",
                " ".join(f"{v:.2f}" for v in x),
            )

    sens = load("sens")
    print("\n## driven length +-1 % at x5: fwd dBi delta, F/B delta, Z")
    for lab in LABS:
        for e in ENG:
            base = [
                r
                for r in lad
                if r["design"] == lab and r["engine"] == e and r["m"] == 5
            ][0]
            out = []
            for v in ("driven x0.99", "driven x1.01"):
                r = [
                    r
                    for r in sens
                    if r["design"] == lab and r["engine"] == e and r["variant"] == v
                ][0]
                out.append(
                    f"{v[-4:]}: dG {r['metrics']['fwd_dbi'] - base['metrics']['fwd_dbi']:+.3f}"
                    f" dFB {r['metrics']['fb_db'] - base['metrics']['fb_db']:+.2f}"
                    f" Z {r['z'][0]:.1f}{r['z'][1]:+.1f}"
                )
            print(f"{lab} {NAME[e]:12}", " | ".join(out))

    d4 = load("dir04")
    print("\n## 0.4 lambda: D1 = 0.424 (Table 1) vs 0.443 (Fig 9)")
    for e in ENG:
        ms, g = series(d4, "0.4", e, "fwd_dbi", "D1=0.443")
        ms0, g0 = series(lad, "0.4", e, "fwd_dbi")
        b, how = best(ms, g)
        b0, how0 = best(ms0, g0)
        _, fb = series(d4, "0.4", e, "fb_db", "D1=0.443")
        _, fb0 = series(lad, "0.4", e, "fb_db")
        _, z = series(d4, "0.4", e, "R", "D1=0.443")
        _, x = series(d4, "0.4", e, "X", "D1=0.443")
        print(
            f"{NAME[e]:12} 0.424: {b0 - DBD:.3f} dBd ({how0}) F/B x9 {fb0[-1]:.1f} | 0.443: {b - DBD:.3f} dBd ({how})"
            f" F/B x9 {fb[-1]:.1f}  Z x5 {z[2]:.1f}{x[2]:+.1f}  rungs",
            " ".join(f"{v:.3f}" for v in g),
        )

    gr = load("ground")
    print(
        "\n## ground: Yagi minus reference dipole, same height, forward, by elevation"
    )
    els = (0.25, 1.0, 2.0, 3.0, 5.0)
    for h in (2.0, 3.0):
        for e in ("bs2", "nec42"):
            ref = [
                r
                for r in gr
                if r["design"] == "ref" and r["engine"] == e and r["height_lambda"] == h
            ][0]["fan"]
            ref = {float(k): v for k, v in ref.items()}
            pk_ref = max(ref, key=ref.get)
            print(
                f"h={h} {NAME[e]}: dipole lobe peak {ref[pk_ref]:.2f} dBi at el {90 - pk_ref:.2f}"
            )
            for lab in LABS:
                f = [
                    r
                    for r in gr
                    if r["design"] == lab
                    and r["engine"] == e
                    and r["height_lambda"] == h
                ][0]["fan"]
                f = {float(k): v for k, v in f.items()}
                pk = max(f, key=f.get)
                fs = conv[lab][e] - refg[e] if e in conv[lab] else None
                cells = " ".join(f"{f[90 - el] - ref[90 - el]:.3f}" for el in els)
                print(
                    f"   {lab}: ratio at el {els}: {cells} | peak-to-peak {f[pk] - ref[pk_ref]:.3f} (Yagi el {90 - pk:.2f})"
                    f" | free-space (own dipole) {fs:.3f} | grazing-free {f[89.75] - ref[89.75] - fs:+.3f}"
                )

    fo = load("folded")
    print("\n## folded driven element (0.8 lambda design)")
    for e in ENG:
        ms, g = series(fo, "0.8", e, "fwd_dbi", "folded 0.01")
        _, R_ = series(fo, "0.8", e, "R", "folded 0.01")
        _, X_ = series(fo, "0.8", e, "X", "folded 0.01")
        _, fb = series(fo, "0.8", e, "fb_db", "folded 0.01")
        _, g0 = series(lad, "0.8", e, "fwd_dbi")
        err = [r.get("error") for r in fo if r["engine"] == e and r.get("error")]
        print(
            f"{NAME[e]:12} m={ms} G",
            " ".join(f"{v:.3f}" for v in g),
            "| straight",
            " ".join(f"{v:.3f}" for v in g0[:3]),
            "| Z",
            " ".join(f"{a:.1f}{b:+.1f}" for a, b in zip(R_, X_, strict=True)),
            "| F/B",
            " ".join(f"{v:.1f}" for v in fb),
            err[:1],
        )

    print("\n## timing (s) and nseg at x9")
    for e in ENG:
        t = sum(r["seconds"] for r in lad if r["engine"] == e)
        r9 = [
            r for r in lad if r["engine"] == e and r["m"] == 9 and r["design"] == "3.2"
        ][0]
        print(NAME[e], f"{t:.1f}s total", r9.get("nseg"))


if __name__ == "__main__":
    main()
