# Verdict: Cebik's 3-element 20 m yagi with tapered elements

**Added:** 2026-11-23 by Steve Burns, KK7KNB, from a segment-convergence
study of momwire's engines. **Status: verdict published** (nec2c, NEC-5 and
momwire; licensed NEC-4.2 not yet run).

## The antenna

L. B. Cebik, W4RNL, "I Want to Build a 3-Element Yagi", part 3: the 20 m
"high-load" design, with its telescoping aluminium elements, in free space.

- Full element lengths: reflector 447.3 in, driven element 421.6 in,
  director 393.3 in.
- Spacing: reflector to driven element 80.0 in, driven element to director
  106.0 in.
- Taper, from the boom outward (the article's Fig. 23 schedule): 48 in of
  1.25 in OD (one 96 in centre tube), then 24 in of 1.0 in, 20 in of
  0.875 in, 42 in of 0.75 in, 20 in of 0.625 in, and a 0.5 in tip to the
  element's end. Eleven wires per element.
- Fed at the centre of the driven element's centre tube.
- **Frequency 14.175 MHz.** This is an assumption: the article's page names
  no frequency; 14.175 MHz is the 20 m design frequency of Cebik's taper
  study.

`tapered-yagi.nec` is the NEC-2-dialect deck at the base mesh (each
section about 20 in a segment, the centre tube odd). `study/mkyagi.py`
writes it from the dimensions above.

## The ladder

Every GW count is multiplied by an odd m and the source re-centred, as for
the tapered dipole. NEC-5 and the NEC-5-dialect momwire engines read the
same structure written in NEC-5's dialect, with the source at the centre
tube's middle knot (one more segment on the fed wire). All values are
Zin in Ω at 14.175 MHz.

| m | N (NEC-2 deck) | nec2c | momwire sinusoidal, NEC-2 rules | momwire sinusoidal, NEC-4.2 rules | NEC-5 | momwire razor2p | momwire bs2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 61 | 19.81 + j17.87 | 19.80 + j17.90 | 27.81 + j0.97 | 31.73 − j8.61 | 31.72 − j8.61 | 30.28 − j5.02 |
| 3 | 183 | 15.41 + j28.93 | 15.40 + j28.96 | 26.34 + j3.88 | 30.78 − j6.02 | 30.78 − j6.02 | 30.12 − j4.66 |
| 5 | 305 | 13.67 + j34.15 | 13.66 + j34.19 | 25.70 + j5.20 | 30.52 − j5.45 | 30.52 − j5.45 | 30.05 − j4.55 |
| 9 | 549 | 12.04 + j39.78 | 12.03 + j39.82 | 25.59 + j5.51 | 30.30 − j5.01 | 30.30 − j5.01 | 29.99 − j4.45 |
| 15 | 915 | 11.08 + j43.69 | 11.07 + j43.73 | 26.68 + j3.33 | 30.16 − j4.73 | 30.16 − j4.75 | 29.95 − j4.39 |
| 29 | 1769 | 10.55 + j46.54 | 10.55 + j46.58 | 28.86 − j1.64 | 30.03 − j4.51 | 30.03 − j4.52 | 29.90 − j4.34 |

From m = 37 on, some segment is shorter than its wire's radius (the
0.625 in sections), outside the thin-wire kernels' range, so those rungs
(to m = 75 for momwire) are in the figure but not used for the call.

![R and X against total segments, all engines](figures/ladder.png)

## The verdict

**≈ 29.8 − j4.3 Ω**, on two independent formulations that converge to it:

- momwire bs2 extrapolates to 29.83 − j4.31 Ω (it is within 1 % of that
  from 428 segments, and within |ΔΓ| 0.01 from 184).
- NEC-5, and its momwire twin razor2p, approach it from above more slowly
  (razor2p extrapolates to 29.85 − j4.27 Ω, 0.05 Ω from bs2; within 1 %
  only from about 1,770 segments). NEC-5 itself reads 30.03 − j4.51 Ω at
  m = 29 and is still falling towards it.
- It agrees with Cebik's own description of the design, a feed impedance
  of about 30 Ω.

**Raw NEC-2 is wrong here, and refining the mesh makes it worse.** nec2c
reads 19.8 + j17.9 Ω at the base mesh and 10.6 + j46.5 Ω at m = 29, about
55 Ω and |ΔΓ| 0.9 from the answer. It is the stepped-radius defect the
tapered-dipole verdict shows, much larger on a yagi: the taper steps sit in
every element, and the parasitic elements' currents carry the error into
the feed. momwire's NEC-2 twin (sinusoidal with NEC-2's rules) reproduces
nec2c to about 0.04 Ω at every rung.

**Equal segment lengths across the steps do not help.** The usual NEC-2
advice for a stepped element is to keep segments the same length on both
sides of each diameter step. With every segment in an element about the
same length (`study/equal_segments.py`), nec2c moves away from the answer
just as the odd-multiple ladder does:

| segment length | N | nec2c |
| --- | --- | --- |
| 20 in | 61 | 19.81 + j17.87 |
| 8 in | 153 | 16.24 + j26.49 |
| 4 in | 315 | 13.51 + j34.41 |
| 2 in | 633 | 11.70 + j40.94 |
| 1.2 in | 1059 | 10.87 + j44.50 |

So there is no segment count at which raw NEC-2 reaches the answer here.

**momwire's NEC-4.2-rule sinusoidal does not converge either.** It sits
5–11 Ω off on the usable rungs (25.6 + j5.5 Ω at m = 9), and crosses the
answer only once segments are about as short as the radius. Licensed
NEC-4.2 has not been run on this deck yet; until it is, this row is
momwire's NEC-4.2-rule engine, not NEC-4.2.

**The radius steps are the cause.** The same yagi with every tube at one
radius (9.525 mm, `study/uniform-control.nec`, detuned to about
10.9 + j55 Ω) brings both sinusoidal rule sets to within 0.2–1.4 Ω of bs2.
NEC-2's extended kernel does not fix the tapered case (still about 55 Ω
off).

## Reproducing

- `study/mkyagi.py` writes `tapered-yagi.nec`; `study/mkuniform.py` the
  uniform-radius control.
- `study/ladder.py` writes the odd-multiple rungs (the source re-centred to
  (s − 1)m + (m + 1)/2, as in this repo's other ladders).
- nec2c 1.3.1 and NEC-5 read the rung decks verbatim. NEC-5 printouts are
  End-User Reports (LLNL-CODE-746721); only their numbers appear here.
- momwire 0.97.1: each engine through its own launcher (`momwire-nec2c-sinusoidal`,
  `momwire-nec42-sinusoidal`, `momwire-nec5-razor2p`, `momwire-nec5-bs2`).
