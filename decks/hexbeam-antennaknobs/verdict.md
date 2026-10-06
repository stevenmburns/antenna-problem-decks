# Verdict: G3TXQ-class broadband hexbeam (antennaknobs catalog)

**Submitted:** 2026-08-14, requested via Reddit by u/Pyro_raptor841.
The antenna is the antennaknobs catalog's own `beams.hexbeam`, exported
by `nec_export`. **Status: verdict published; re-run four-way
(NEC-4.2 added) 2026-10-06 — see the addendum below.**

## The antenna

A G3TXQ-class broadband hexbeam in free space at 28.47 MHz, uniform
0.5 mm wire, on a hexagonal footprint of radius 1.6165 m. Two elements:
a W-shaped driven element fed at the hex center, and a *perimeter*
reflector — three full hexagon sides across the back with no center
indent — coupled to the driver only across two open tip gaps. That
reflector is the defining change of Steve Hunt G3TXQ's broadband
hexbeam over the classic design, whose reflector mirrors the driver's
W ([antenneX Issue 128, December
2007](https://www.hexkit.com/files/hexbeam.pdf)).

The topology is G3TXQ's; the dimensions are catalog-tuned. Measured as
scale-free ratios against G3TXQ's published 20 m monoband reference
(half driver 219.5", half reflector 207.5", end spacing 24"), the
catalog design reproduces the hexagon radius to **−0.6%**, the half
reflector to **+0.2%** and the half driver to **+1.8%** — but its tip
gap is **30% narrower** (0.131 R vs G3TXQ's 0.186 R). That is the one
real dimensional difference, and it is a deliberate design choice
rather than an error: G3TXQ's own end-spacing study found end spacing
"mostly affects the peak F/B performance" and warned that gaps of 24"
and above buy their high F/B numbers from deep, narrow notches in the
azimuth pattern that "are somewhat illusory" in day-to-day operation.
A narrower gap trades peak F/B for a broader, better-behaved pattern.
**Feedpoint impedance and tuning are set by the driver and reflector
lengths, both of which match**, so the verdict below is a verdict on
the published design's electrical behavior, not on a variant.

Unlike the tapered dipole (radius steps) and the hentenna (a
multi-junction loop), this deck carries no known NEC-2 stressor. It is
here as a control: the most-built wire beam in amateur radio, asked of
all three engines at once.

## The three-way ladder (as published, 2026-08)

Per-wire segment counts multiplied ×1 / ×3 / ×5 (88 / 264 / 440
segments). The fed wire is the 0.05 m span across the hex center; at
1 / 3 / 5 segments it keeps a center segment at every rung, and the EX
card is re-centered on it per rung.

| engine | ×1 | ×3 | ×5 |
| --- | --- | --- | --- |
| nec2c (raw NEC-2) | 48.45 + j19.82 | 50.44 + j20.58 | 50.31 + j20.48 |
| momwire bs2 | 50.05 + j19.94 | 50.17 + j20.27 | 50.22 + j20.35 |
| NEC-5 | 50.13 + j20.36 | 50.15 + j20.35 | 50.20 + j20.36 |

NEC-5 Richardson pair (×3, ×5): **50.20 + j20.36 Ω**.

## The verdict

The two independent formulations agree: **≈ 50.2 + j20.4 Ω** (bs2
finest vs the NEC-5 pair: **0.021 Ω apart, ΔΓ 0.0002** — the tightest
agreement of any entry in this collection so far, and both ladders are
mesh-stable to the second decimal).

**And raw NEC-2 agrees with them.** At the finest rung nec2c sits
0.15 Ω from the consensus (ΔΓ 0.0015) — closer than the *disagreements*
this collection has documented elsewhere by two orders of magnitude.
This is the first entry here where the answer is that nothing is wrong:
**NEC-2 models a broadband hexbeam correctly.** The tens of thousands
of hexbeams designed in NEC-2-based software were not designed on a
broken tool.

The one honest caveat is at the base mesh. nec2c reads **1.9 Ω low in R
at ×1** and reaches the consensus by ×3; bs2 and NEC-5 are already
there at ×1. The cause is the deck's feed idiom — see below — and the
behavior is *converging*, not drifting: nec2c's rung-to-rung step
collapses from +1.98 Ω to −0.13 Ω, an overshoot-and-settle, the
opposite of the hentenna's super-logarithmic crawl. Refinement fixes it
and then leaves it alone. The base-mesh offset is reproducible live:
the hosted simulator's convergence view shows its NEC-2 lane a couple
of ohms from bs2 at comparable densities (that lane is nec2++ rather
than nec2c, and the app drives the design through its port convention
rather than this deck's EX card — both move the curves by fractions of
an ohm on top of the mesh effect).

The design's own note, not a defect: this hexbeam is not resonant at
its design frequency. It carries **+j20 Ω** on this deck's 0.5 mm wire
— SWR 1.50 against 50 Ω, on which all three engines agree to three
decimal places (a #16 build sits ~3 Ω less inductive; see the wire
judgment call below). That matches
what G3TXQ published for the broadband design, whose modelled and
measured SWR minima also sit near 1.4–1.5 rather than at 1.0. The
broadband hexbeam trades a perfect match for bandwidth by design.

### Modeling judgment calls

Three choices a reader should weigh before reusing these numbers:

- **Wire: 0.5 mm radius, PEC.** G3TXQ built and published with #16 bare
  copper (0.645 mm radius); the deck's wire is 22% thinner and lossless.
  We measured the gauge dependence at the finest rung rather than assuming
  it: R barely moves (+0.6 Ω across #18-class → #14) — the resistive
  signature of G3TXQ's actual claim, that *tuning* and published
  *dimensions* are gauge-independent — but the reactance does not:
  **+j20.4 on this deck's wire → +j17.3 on #16 → +j14.5 on #14** (SWR
  1.50 → 1.41 → 1.33, independently matching G3TXQ's own SWR-vs-gauge
  chart). All three engines agree on the shift to within 0.03 Ω. So read
  this deck's R as the built antenna's; read its X as the thin wire's —
  the consensus for a #16 build is **50.5 + j17.3 Ω** — and do not read
  gain or front-to-back off a lossless-wire deck at all.
- **The feed.** A 0.05 m wire spans the hex center, against ~0.12 m
  segments on its neighbours — a segment-length discontinuity sitting
  exactly at the source. The hentenna deck had its short-bridge feed
  removed for precisely this reason; this one keeps it, because here the
  span **is** the physical center-post geometry rather than a modeling
  convenience, and removing it would model a different antenna. The
  ladder above prices the choice honestly: it costs raw NEC-2 about
  1.9 Ω at the base mesh, costs the other two engines nothing measurable,
  and is gone from all three by ×3.
- **Tip gaps are true open gaps** — unconnected endpoints on a shared
  hexagon side, with no bridging wire and no load. That is faithful to
  the built antenna, where a non-conducting cord spans them.

## 2026-10-06 four-way re-run: four engines, one answer

This is the same ladder, re-run with licensed NEC-4.2 as a fourth
engine and with current momwire. All values are at 28.47 MHz.

| engine | ×1 | ×3 | ×5 |
| --- | --- | --- | --- |
| nec2c (raw NEC-2) | 48.45 + j19.82 | 50.44 + j20.58 | 50.31 + j20.48 |
| NEC-4.2 | 48.45 + j19.82 | 50.46 + j20.59 | 50.38 + j20.49 |
| momwire bs2 | 49.99 + j20.24 | 50.16 + j20.39 | 50.21 + j20.42 |
| NEC-5 | 50.13 + j20.36 | 50.15 + j20.35 | 50.20 + j20.36 |

NEC-5 rows are (N, 2N) Richardson pairs per rung, as before. nec2c and
NEC-5 reproduce the published ladder to the digit. bs2 moved by at
most 0.31 Ω at ×1 and 0.07 Ω at ×5, from the solver changes since
0.28.1.

**All four engines agree.** At ×5:

- Every pair of engines sits within 0.22 Ω (ΔΓ ≤ 0.0021).
- The bs2/NEC-5 midpoint is **50.21 + j20.39 Ω**. nec2c is 0.13 Ω
  from it (ΔΓ 0.0013) and NEC-4.2 is 0.20 Ω (ΔΓ 0.0019).
- All four read SWR 1.50 against 50 Ω (1.497–1.500).

The verdict's call is unchanged and now rests on four engines rather
than three.

**NEC-4.2 tracks raw NEC-2 on this deck, including its base-mesh
offset.** At ×1 the two print the same impedance to the last digit
shown (48.45 + j19.82), and at ×5 they are 0.07 Ω apart. So the
1.9 Ω base-mesh deficit described above is shared by NEC-4.2. bs2 and
NEC-5 are free of it. The finer rungs remove it from both NEC-2-family
engines, as before.

**Wire gauge, four-way.** The gauge study was repeated at ×5 with
NEC-4.2 added (radius 0.6453 mm for #16, 0.814 mm for #14):

| engine | 0.5 mm (deck) | #16 | #14 |
| --- | --- | --- | --- |
| nec2c | 50.31 + j20.48 | 50.63 + j17.40 | 50.94 + j14.59 |
| NEC-4.2 | 50.38 + j20.49 | 50.75 + j17.43 | 51.14 + j14.64 |
| momwire bs2 | 50.21 + j20.42 | 50.52 + j17.37 | 50.82 + j14.59 |
| NEC-5 | 50.20 + j20.36 | 50.51 + j17.30 | 50.82 + j14.50 |

The reactance shift from 0.5 mm to #16 is −3.05 to −3.08 Ω on all
four engines. To #14 it is −5.83 to −5.89 Ω. The four agree on the
shift to within 0.06 Ω. The judgment-call conclusions above stand:
read R as the built antenna's and X as the thin wire's.

**A correction to the published table's footnote.** The value printed
above as the NEC-5 "Richardson pair (×3, ×5)", 50.20 + j20.36 Ω, is
the ×5 row's own (N, 2N) pair. Extrapolating the ×3 and ×5 rows at
order 1 instead, as the tapered-dipole and hentenna verdicts do, gives
**50.28 + j20.38 Ω**. bs2 at ×5 sits 0.08 Ω from that value
(ΔΓ 0.0007). No call depends on the difference.

## Reproducing

The deck is `hexbeam.nec` in this directory, exported verbatim from the
catalog design with `export_nec(Builder(), ground=None, freq=28.47)`.
The ladder driver multiplies each GW's segment count and re-centers the
EX segment; engines run through antennaknobs' census harness
(`scripts/bench_nec_corpus.py` — nec2c on PATH, momwire ≥ 0.28.1,
`$NEC5_EXE` for the licensed NEC-5 lane; NEC-5 printouts are End-User
Reports, LLNL-CODE-746721). The whole ladder is 8.5 s of wall time.

The design itself is `beams.hexbeam` in the antennaknobs catalog — the
[hosted simulator](https://antennaknobs.dev/) solves it live on the
non-NEC-2 engines. G3TXQ's published dimensions come from [antenneX
Issue 128](https://www.hexkit.com/files/hexbeam.pdf) and his own
[karinya.net hexbeam pages](http://karinya.net/g3txq/hexbeam/broadband/)
(note: that site's TLS certificate has expired).

**The 2026-10-06 re-run** used the same ladder rule (every GW count
×m, each EX segment re-centred to (s−1)·m + (m+1)/2). It was run on
one machine:

- nec2c 1.3.1 and NEC-4.2 read the laddered deck verbatim. NEC-4.2 is
  the licensed console binary (sha256 `02c6fc87c8cb75cb…`); its
  printouts are End-User Reports, LLNL-CODE-491368.
- NEC-5 is the licensed binary (sha256 `39e628ad79ea1b54…`) through
  `NEC5Engine`, with an (N, 2N) pair per rung; LLNL-CODE-746721.
- momwire `main` at `6550d7e3` (0.72.0 plus unreleased commits) ran as
  bs2 through antennaknobs `main` at `5aef3392`.

Kernels, stated explicitly:

- **nec2c and bs2** use the standard thin-wire kernel, because the
  deck has no `EK` card. The run recorded `extended_kernel=False` on
  the momwire solver.
- **NEC-4.2** ignores `EK`; its printout says so.
- **NEC-5** has no `EK` card.

A kernel-matched bs2 (extended kernel forced on) differs from the
table's bs2 by at most 0.02 Ω.
