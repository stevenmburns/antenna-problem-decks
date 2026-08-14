# Verdict: tapered dipole, 20:1 radius taper

**Submitted:** 2026-08-13, via the groups.io Antenna Research thread
(SimNEC-authored deck). **Status: verdict published.**

## The antenna

A 10.51 m free-space dipole at 14.2 MHz built from ten colinear
sections whose radius steps linearly from 1.25 mm to 25 mm — a 20:1
taper end to end. Fed at the center of section 6. This is the
stepped-radius class NEC-2 carries a documented defect on (the reason
EZNEC ships the Leeson correction), pushed about as hard as a wire
antenna can push it.

## The three-way ladder

Segment counts per section: 3 / 9 / 15 (odd multiples, so the fed
section keeps a center segment at every rung).

| engine | ×1 | ×3 | ×5 |
| --- | --- | --- | --- |
| nec2c (raw NEC-2) | 78.09 + j24.17 | 79.33 + j29.02 | 79.86 + j31.23 |
| momwire bs2 | 75.67 + j8.02 | 75.94 + j8.49 | 76.02 + j8.58 |
| NEC-5 | 75.89 + j8.10 | 76.06 + j8.25 | 76.13 + j8.25 |

NEC-5 Richardson pair (×3, ×5): **76.22 + j8.24 Ω**.

## The verdict

The two independent formulations agree: **≈ 76 + j8 Ω** (bs2 finest vs
the NEC-5 pair: 0.40 Ω apart, ΔΓ 0.0025, both ladders mesh-stable).
Raw NEC-2 reads the reactance **~23 Ω high (j31 vs j8) and the error
grows with segment density** — refining the model makes it worse, the
opposite of what refinement usually buys. Any NEC-2-based program run
uncorrected on this geometry (nec2c, EZNEC without Leeson correction,
4nec2, SimNEC's bundled engine) will misreport this antenna's
feedpoint: the ~j24–31 readings are the defect, not the antenna.

The submitter's distrust was correct, and correctly aimed.

## Reproducing

The deck is `tapered.nec` in this directory, verbatim as submitted.
The ladder driver multiplies each GW's segment count and re-centers the
EX segment; engines run through antennaknobs' census harness
(`scripts/bench_nec_corpus.py` — nec2c on PATH, momwire ≥ 0.28.1,
`$NEC5_EXE` for the licensed NEC-5 lane; NEC-5 printouts are End-User
Reports, LLNL-CODE-746721). See the antennaknobs
[validation page](https://antennaknobs.dev/reference/validation/) for
the wider Leeson story this case now extends.
