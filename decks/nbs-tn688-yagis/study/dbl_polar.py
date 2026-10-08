"""Polar pattern progression on the doubling ladder, with NBS's measured
points. Full 360 deg azimuth (E-plane: theta = 90, the plane of the
elements), FREE SPACE, gain in dBd (dBi - 2.15), one curve per rung
(light = coarse, dark = fine).

    python dbl_polar.py           -> dbl_polar.png (seven lanes x four designs)
    python dbl_polar.py trimmed   -> dbl_polar_trimmed.png

Reads results/dbl.jsonl and results/nocap.jsonl (nec2c EK with its
free-end cap zeroed; see nocap.py).

NBS points (TN 688, Table 1 and the 5-element pattern in the text):
forward gain for every design; for 0.8 lambda also F/B 15 dB and the
E-plane -3 dB beamwidth 48 deg.
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = [json.loads(l) for f in ("results/dbl.jsonl", "results/nocap.jsonl") for l in open(f)]
R = [r for r in R if not r.get("error")]
PHI = np.deg2rad(np.append(np.arange(720) * 0.5, 360.0))
ALL_LANES = [("nec2c", "nec2c (reduced kernel)"), ("nec2cEK", "nec2c EK"),
             ("nec2cEK_nocap", "nec2c EK, free-end cap zeroed"),
             ("sinEK", "momwire sin EK"), ("bs2EK", "momwire bs2 EK"), ("nec42", "NEC-4.2"),
             ("nec5", "NEC-5"), ("razor2p", "momwire razor-2p (EK)")]
NBS = {"0.4": {"fwd": 7.1}, "0.8": {"fwd": 9.2, "fb": 15.0, "bw_e": 48.0},
       "1.2": {"fwd": 10.2}, "2.2": {"fwd": 12.25}, "3.2": {"fwd": 13.4}, "4.2": {"fwd": 14.2}}
DBD = 2.15
TOP, FLOOR = 18.0, -27.0          # dBd range on the radial axis


def r_of(g):
    return np.maximum(g, FLOOR) - FLOOR


def panel(ax, d, lane, legend=True):
    rs = sorted((r for r in R if r["design"] == d and r["lane"] == lane),
                key=lambda r: r["nseg_el"])
    cm = plt.cm.viridis(np.linspace(0.85, 0.0, 5))
    for k, r in enumerate(rs):
        g = np.array(r["az"]) - DBD
        g = np.append(g, g[0])
        ax.plot(PHI, r_of(g), color=cm[k], lw=1.2,
                label=f"n={r['nseg_el']}  {g[0]:.2f} dBd, F/B {g[0]-g[360]:.1f}")
    m = NBS.get(d, {})
    if "fwd" in m:
        ax.plot([0], [r_of(m["fwd"])], "o", ms=7, mfc="none", mec="red", mew=1.8,
                label="NBS measured", zorder=5)
    if "fb" in m:
        ax.plot([np.pi], [r_of(m["fwd"] - m["fb"])], "o", ms=7, mfc="none", mec="red",
                mew=1.8, zorder=5)
    if "bw_e" in m:
        h = np.deg2rad(m["bw_e"] / 2)
        ax.plot([h, 2 * np.pi - h], [r_of(m["fwd"] - 3)] * 2, "o", ms=6, mfc="none",
                mec="red", mew=1.8, zorder=5)
    ax.set_theta_zero_location("N")
    ax.set_rlim(0, TOP - FLOOR)
    ticks = [-20, -10, 0, 10]
    ax.set_rticks([t - FLOOR for t in ticks])
    ax.set_yticklabels([f"{t}" for t in ticks[:-1]] + ["10 dBd"], fontsize=7)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 45)))
    ax.tick_params(axis="x", labelsize=7)
    if legend:
        ax.legend(fontsize=6.5, loc="lower left", bbox_to_anchor=(-0.2, -0.2))


def figure(lanes, designs, out, size, dpi, wrap=False):
    fig, axs = plt.subplots(len(lanes), len(designs), figsize=size,
                            subplot_kw={"projection": "polar"}, squeeze=False)
    for i, (lane, name) in enumerate(lanes):
        for j, d in enumerate(designs):
            ax = axs[i, j]
            panel(ax, d, lane)
            if i == 0:
                ax.set_title(f"{d} λ Yagi (NBS {NBS[d]['fwd']} dBd)\n", fontsize=11)
            if j == 0:
                ax.text(-0.45, 0.5, name, transform=ax.transAxes, rotation=90,
                        va="center", ha="center", fontsize=11)
    sep = "\n" if wrap else " "
    fig.suptitle("NBS TN 688 Yagis, free space, E-plane (azimuth, the plane of the elements)"
                 f"{sep}as each engine's mesh doubles. Forward = up; red circles = NBS measured.\n"
                 "n = segments per element; segment/radius 9 → 11.6, 19 → 5.5, 37 → 2.8, "
                 f"75 → 1.4, 151 → 0.7{sep}(NEC-5 and razor-2p: n = 10 … 160)", fontsize=11)
    fig.tight_layout(rect=(0.02, 0, 1, 0.955 if wrap else 0.975))
    fig.savefig(out, dpi=dpi)


if len(sys.argv) > 1 and sys.argv[1] == "trimmed":
    keep = {"nec2cEK", "nec2cEK_nocap", "bs2EK", "nec5"}
    figure([x for x in ALL_LANES if x[0] in keep], ["0.8", "2.2"],
           "dbl_polar_trimmed.png", (10, 20), 100, wrap=True)
else:
    figure(ALL_LANES, ["0.8", "1.2", "2.2", "4.2"], "dbl_polar.png", (16, 32), 85)
