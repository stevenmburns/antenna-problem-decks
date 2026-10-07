# Verdict: tapered dipole, 20:1 radius taper

**Submitted:** 2026-08-13 by Ward Harriman, AE6TY (author of SimNEC),
via the groups.io Antenna Research thread. **Status: verdict
published; re-run four-way (NEC-4.2 added) 2026-10-06 — see the
addendum below.**

## The antenna

A 10.51 m free-space dipole at 14.2 MHz built from ten colinear
sections whose radius steps linearly from 1.25 mm to 25 mm — a 20:1
taper end to end. Fed at the center of section 6. This is the
stepped-radius class NEC-2 carries a documented defect on (the reason
EZNEC ships the Leeson correction), pushed about as hard as a wire
antenna can push it.

## The three-way ladder (as published, 2026-08)

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

## 2026-10-06 four-way re-run: NEC-4.2 does not join the consensus

The same ladder, re-run with licensed NEC-4.2 as a fourth engine and
with current momwire. Two more rungs (×7, ×9) were added to see where
the ladders head.

| engine | ×1 | ×3 | ×5 | ×7 | ×9 |
| --- | --- | --- | --- | --- | --- |
| nec2c (raw NEC-2) | 78.09 + j24.17 | 79.33 + j29.02 | 79.86 + j31.23 | 80.21 + j32.74 | 80.50 + j33.93 |
| NEC-4.2 | 76.36 + j12.86 | 76.92 + j14.91 | 77.20 + j16.46 | 77.40 + j17.53 | 77.59 + j18.23 |
| momwire bs2 | 75.66 + j7.99 | 75.91 + j8.36 | 76.00 + j8.48 | 76.05 + j8.53 | 76.09 + j8.57 |
| NEC-5 | 75.89 + j8.10 | 76.06 + j8.25 | 76.13 + j8.25 | 76.16 + j8.19 | 76.20 + j8.26 |

All values are at 14.2 MHz. The NEC-5 rows are each rung's (N, 2N)
Richardson pair, as before. The NEC-5 (×3, ×5) pair is unchanged:
**76.22 + j8.24 Ω**. nec2c and NEC-5 reproduce the published ladder
to the digit. momwire bs2 moved by at most 0.14 Ω, from the solver
changes since 0.28.1, the largest being that the extended kernel now
applies across this deck's radius steps (momwire#1368).

**The bs2/NEC-5 consensus stands.** bs2 at ×5 sits 0.33 Ω from the
NEC-5 pair (ΔΓ 0.0020), slightly closer than the published
0.40 Ω / 0.0025, and both ladders stay flat through ×9.

**NEC-4.2 disagrees with that consensus. Here is the size of the gap
and where it sits.** At ×5 NEC-4.2 reads **77.20 + j16.46 Ω**. That
is 8.07 Ω from bs2 (ΔΓ 0.050) and 8.28 Ω from the NEC-5 pair
(ΔΓ 0.051). Almost all of the gap is reactance: NEC-4.2 reads about
8 Ω more inductive than the consensus. Like nec2c's reactance, NEC-4.2's
rises at every refinement step (+2.05, +1.55, +1.07, +0.70 Ω from one
rung to the next), and it has not levelled off by ×9 (j18.23). NEC-4.2
sits between raw NEC-2 and the consensus. It is 15.0 Ω from nec2c at
×5 and about half that from bs2 and NEC-5. It agrees with neither
side. On a 20:1 taper, NEC-4.2 therefore does not remove the
reactance error that this deck was submitted to expose. It shrinks
that error to roughly a third of NEC-2's (j16.5 against j31.2 at ×5,
where the consensus reads j8.4), and like NEC-2's error it grows as
the mesh is refined. We report this disagreement as measured and have
not adjudicated its cause.

At ×9 the fattest section's segments are 39 mm long on a 25 mm
radius, a length-to-radius ratio of 1.6. Neither the nec2c printout
nor the NEC-4.2 printout warns about it. The ladder stops there on
purpose, before the thin-wire assumption is stretched further.

**The call, as of 2026-10-06:** unchanged. **≈ 76 + j8 Ω**, on two
independent formulations (momwire bs2 and NEC-5). Raw NEC-2 reads
the reactance ~23 Ω high (j31 at ×5) and gets worse with refinement.
NEC-4.2 reads it ~8 Ω high (j16.5 at ×5) and also drifts upward. A
NEC-4.2 user modelling a steeply tapered element should not take its
reactance as converged, at least not on this geometry.

## Reproducing

The deck is `tapered.nec` in this directory, verbatim as submitted.
The ladder driver multiplies each GW's segment count and re-centers the
EX segment; engines run through antennaknobs' census harness
(`scripts/bench_nec_corpus.py` — nec2c on PATH, momwire ≥ 0.28.1,
`$NEC5_EXE` for the licensed NEC-5 lane; NEC-5 printouts are End-User
Reports, LLNL-CODE-746721). See the antennaknobs
[validation page](https://antennaknobs.dev/reference/validation/) for
the wider Leeson story this case now extends.

**The 2026-10-06 re-run** used the same ladder rule: every GW count
×m, and each EX segment re-centred to (s−1)·m + (m+1)/2. It was run on
one machine. nec2c 1.3.1 and NEC-4.2 read the laddered deck verbatim.
NEC-4.2 is the licensed console binary (sha256 `02c6fc87c8cb75cb…`);
its printouts are End-User Reports, LLNL-CODE-491368. NEC-5 is the
licensed binary (sha256 `39e628ad79ea1b54…`), driven through
antennaknobs' `NEC5Engine` with an (N, 2N) pair per rung;
LLNL-CODE-746721. momwire is `main` at `6b71942d` (0.73.1 plus
unreleased commits), run as bs2 through antennaknobs `main` at
`ed5058f4`.

Kernels, stated explicitly:

- **nec2c and bs2** both honour this deck's `EK` card, so both ran the
  extended thin-wire kernel. The run recorded `extended_kernel=True` on
  the momwire solver.
- **NEC-4.2** ignores `EK`; its printout reports that the card has no
  effect.
- **NEC-5** has no `EK` card.
