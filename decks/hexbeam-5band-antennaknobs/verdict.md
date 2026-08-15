# Verdict: 5-band stacked hexbeam (antennaknobs catalog)

**Submitted:** 2026-08-14, by antennaknobs itself — a follow-up to
u/Pyro_raptor841's single-band hexbeam request. The design is the
catalog's `multiband.hexbeam_5band`, exported by `nec_export`.
**Status: verdict published.**

## Two antennas, two questions

This deck collection answers two different questions, and conflating
them would mislead a builder.

**The physical antenna has one feed.** Band 0 is driven; the other four
couple to it through 50 Ω coax jumpers up the stack. The catalog models
that with `build_network()`, and the engines solve it by a circuit
reduction over the antenna's own multiport admittance — **not** with
native NEC cards. There is no faithful single `.nec` deck of it, and
`nec_export` refuses to emit one. Section *"The physical antenna"*
below gives those numbers, and they are the ones a builder wants.

**The decks in this directory are the other thing:** the catalog's
exportable `daisy_chain=False` convention, **all five feeds driven
simultaneously at 1 V**. The design's own docstring calls it "a tuning
aid, not the physical feed." Two consequences:

- The off-band feeds are **co-driven, not parasitic.** Four of five
  ports sit at large **negative** input resistance (−106 Ω to −724 Ω) —
  power flowing from the array back into those sources. Correct linear
  algebra for this excitation; meaningless as an antenna impedance.
- The active band's impedance here is **not** what the one-coax antenna
  presents on that band. Compare 20 m: 44.9 + j35.2 Ω multi-feed
  against 86.2 + j13.2 Ω physical.

The multi-feed decks earn their place as a **numerical** validation
target — three independent formulations on a hard, strongly coupled,
50-wire, five-source problem — not as a performance claim.

## The antenna

Five G3TXQ-class broadband hexbeams (W driver, perimeter reflector,
open tip gaps — see the single-band verdict) stacked concentrically on
one mast in free space, 20 / 17 / 15 / 12 / 10 m at 14.300, 18.1575,
21.383, 24.97 and 28.47 MHz. 50 wires, 308 segments at the base mesh,
uniform 0.5 mm wire, band 0 on top.

Three parameter sets appear below, all shipped:

- **`default`** — the untuned canonical set (`halfdriver_factor` 1.071,
  `t0_factor` 0.1243, `tipspacer_factor` 0.1312 on every band). This is
  what `multiband.hexbeam_5band` resolves to with no `:variant` suffix,
  so it is what the hosted simulator serves by default, and it is this
  verdict's primary.
- **`opt_coupled`** — a joint tune with all five bands present at every
  objective evaluation, so the optimiser sees real inter-band coupling.
  Reached as `multiband.hexbeam_5band:opt_coupled`. Reported as a
  companion throughout.
- **`opt_physical`** — the follow-up this verdict's own findings forced
  (antennaknobs#921): the same knobs re-tuned with the objective
  evaluated through the one-coax reduction, i.e. against the Z a
  builder's coax actually sees. Covered in *"The physical antenna"*
  below only — it targets the single-feed model, so the multi-feed
  censuses above it do not apply.

(A fourth set, `opt`, is a sequential single-band tune that does not
see coupling; it is not covered here.)

**This verdict is about the catalog design, not about G3TXQ's built
5-bander.** They differ structurally in ways that matter more than in
the single-band case:

- **Stack spacing.** The catalog stacks bands at a *uniform* 0.2 m
  (7.9"), 0.8 m total. G3TXQ's published prototype is strongly
  *non-uniform* — 38" / 15" / 9" / 5" / 0" from the 10 m wires, i.e.
  gaps of 23" / 6" / 4" / 5", 38" total. The catalog's 20–17 m gap is a
  third of his; its 15–12 m gap is twice his.
- **Flat vs dished.** The catalog stacks perfectly planar hexagons.
  Real spreaders bow into a shallow dish, and G3TXQ blames that dish
  directly for the 12 m and 10 m wires ending up "very close to one
  another", which forced the compromise dimensions in his table. A
  flat-stack model cannot reproduce that interaction.
- **Tip gaps** carry the single-band deck's −30% delta against his
  published end spacing.

Same topology, same band plan, materially different stack.

## The three-way ladder (default parameters)

Per-wire segment counts ×1 / ×3 / ×5 (308 / 924 / 1540 segments). Each
band's five 1-segment feed wires go 1 / 3 / 5, keeping a center segment
at every rung, with all five EX cards re-centered per rung. One deck per
band frequency; geometry byte-identical across the five, only `FR`
differs. Rows are that band's **active** feed.

| band | engine | ×1 | ×3 | ×5 |
| --- | --- | --- | --- | --- |
| **20 m** | nec2c | 41.53 + j32.54 | 44.96 + j35.37 | 45.14 + j35.48 |
| | momwire bs2 | 44.90 + j34.76 | 44.91 + j35.11 | 44.92 + j35.18 |
| | NEC-5 | 44.96 + j35.09 | 44.90 + j35.20 | 44.91 + j35.22 |
| **17 m** | nec2c | 37.87 + j32.93 | 40.59 + j36.89 | 40.75 + j37.02 |
| | momwire bs2 | 40.46 + j35.89 | 40.51 + j36.46 | 40.52 + j36.58 |
| | NEC-5 | 40.76 + j36.61 | 40.54 + j36.66 | 40.53 + j36.68 |
| **15 m** | nec2c | 42.31 + j35.89 | 45.76 + j39.42 | 46.02 + j39.64 |
| | momwire bs2 | 45.57 + j38.24 | 45.71 + j38.96 | 45.74 + j39.12 |
| | NEC-5 | 46.13 + j39.18 | 45.78 + j39.22 | 45.78 + j39.25 |
| **12 m** | nec2c | 44.38 + j35.19 | 47.47 + j38.71 | 47.69 + j38.94 |
| | momwire bs2 | 47.13 + j37.32 | 47.33 + j38.21 | 47.37 + j38.41 |
| | NEC-5 | 47.84 + j38.24 | 47.43 + j38.48 | 47.43 + j38.53 |
| **10 m** | nec2c | 54.96 + j18.06 | 60.28 + j19.99 | 60.71 + j20.04 |
| | momwire bs2 | 59.70 + j18.79 | 60.22 + j19.47 | 60.34 + j19.62 |
| | NEC-5 | 60.96 + j18.92 | 60.38 + j19.71 | 60.40 + j19.75 |

NEC-5 rows are Richardson (N, 2N) pairs at every rung.

## The verdict

The two independent formulations agree on all five bands, and **raw
NEC-2 agrees with them on all five**:

| band | consensus (bs2 / NEC-5, ×5) | bs2 vs NEC-5 | nec2c distance |
| --- | --- | --- | --- |
| 20 m | 44.91 + j35.20 | 0.042 Ω, ΔΓ 0.0004 | 0.364 Ω, ΔΓ 0.0035 |
| 17 m | 40.52 + j36.63 | 0.097 Ω, ΔΓ 0.0010 | 0.449 Ω, ΔΓ 0.0047 |
| 15 m | 45.76 + j39.19 | 0.133 Ω, ΔΓ 0.0012 | 0.530 Ω, ΔΓ 0.0049 |
| 12 m | 47.40 + j38.47 | 0.135 Ω, ΔΓ 0.0012 | 0.554 Ω, ΔΓ 0.0050 |
| 10 m | 60.37 + j19.68 | 0.145 Ω, ΔΓ 0.0011 | 0.494 Ω, ΔΓ 0.0039 |

NEC-2's worst distance from consensus is 0.55 Ω (ΔΓ 0.0050), on a deck
with fifty wires, five simultaneous sources, and coupling strong enough
to drive four ports negative-resistive. This is the second agreement
verdict in this collection, and a harder-won one than the single-band
case: **the stacked, strongly coupled multiband array is still inside
NEC-2's envelope.** The nec2c distance is 3–4× the single-band deck's
0.15 Ω and grows smoothly with frequency across the stack — a visible
cost, two orders of magnitude below the disagreements this collection
was built to document.

**Refinement drift.** Every engine converges; nothing crawls. nec2c
starts 3–5 Ω low in R at the base mesh and closes almost entirely by ×3
(second-step increment 4–8% of the first). bs2 decays geometrically at a
near-constant |d2/d1| ≈ 0.22 on all five bands; NEC-5 is essentially
converged at ×1. Not one of the fifteen band/engine ladders shows the
hentenna's monotone super-logarithmic crawl. The base-mesh deficit is
the single-band verdict's feed-wire segment-length discontinuity,
multiplied by five feed wires.

**Co-driven off-band feeds.** These carry the full inter-band coupling
and run to thousands of ohms with negative real parts. All three
engines track them to **≈1% of |Z|** almost everywhere (3–13 Ω of
spread on |Z| of 400–1400 Ω). The exceptions are three ports near an
anti-resonance where |Z| > 1800 Ω and conditioning degrades; worst is
the 17 m feed on the 15 m deck at 4.4% (nec2c 1842, bs2 1737, NEC-5
1707, all ≈ −j2530). Near-anti-resonant ports are exactly where
formulations are expected to part company.

## And dialed in: the `opt_coupled` census

The same 45-solve census on the coupled-tuned variant. Consensus and
distances at ×5:

| band | consensus (bs2 / NEC-5, ×5) | SWR₅₀ | bs2 vs NEC-5 | nec2c distance |
| --- | --- | --- | --- | --- |
| 20 m | 48.25 − j1.34 | 1.05 | 0.043 Ω, ΔΓ 0.0004 | 0.268 Ω, ΔΓ 0.0028 |
| 17 m | 42.04 − j1.39 | 1.19 | 0.114 Ω, ΔΓ 0.0013 | 0.284 Ω, ΔΓ 0.0033 |
| 15 m | 43.95 − j0.66 | 1.14 | 0.146 Ω, ΔΓ 0.0017 | 0.334 Ω, ΔΓ 0.0038 |
| 12 m | 42.56 − j0.71 | 1.18 | 0.146 Ω, ΔΓ 0.0017 | 0.347 Ω, ΔΓ 0.0040 |
| 10 m | 47.84 − j0.81 | 1.05 | 0.037 Ω, ΔΓ 0.0004 | 0.327 Ω, ΔΓ 0.0034 |

The tune does what it says: reactance collapses from +j35…+j39 to
under 1.4 Ω on every band, and multi-feed SWR falls from 2.1–2.3 to
1.05–1.19. **The three-way agreement is unchanged — if anything slightly
tighter** (nec2c's worst distance improves from 0.554 Ω to 0.347 Ω).
Engine agreement is a property of the geometry class, not of how well
the antenna happens to be tuned.

## The physical antenna, two-formulation

The one-coax antenna (`daisy_chain=True`), per band, at the base mesh
(nominal 21 seg/quarter-wave, 308 segments) and one refinement (nominal
63, 917 segments). **How each engine consumes it — and which cannot:**

- **momwire bs2** — `MomwireEngine` computes the antenna's 5-port
  admittance from momwire's quadratic B-spline MoM solution, then the
  engine-layer `NetworkReducer` stamps the four TL jumpers and the
  `Driven` source as a circuit over that Y and solves the driven port.
- **PyNEC (NEC-2 kernel)** — the *same* `NetworkReducer`, with Y coming
  from nec2++'s NEC-2 kernel instead.
- **NEC-5 — cannot, and is absent below.** `NEC5Engine` serves only
  `Load` branches natively; it raises `NotImplementedError: NEC5Engine
  cannot stamp a TL branch (only Load is served natively; lines/two-ports
  have no NEC-5 native cards on this path)`. NEC-5 has no circuit-stamping
  layer on this path.

**So it is NEC-5, not NEC-2, that sits this one out.** NEC-2 is absent
only from the *deck* form of this problem; through the engine layer it
solves the physical antenna fine. And the honest limit of the phrase
"two-formulation": bs2 and PyNEC are two independent **field** solvers
sharing **one common circuit reduction**. The physics differs between
them; the network algebra does not.

Refined (N=63) results:

| band | `default` consensus | SWR₅₀ | bs2 vs PyNEC | `opt_coupled` consensus | SWR₅₀ | bs2 vs PyNEC |
| --- | --- | --- | --- | --- | --- | --- |
| 20 m | 86.18 + j13.21 | 1.78 | 0.530 Ω, ΔΓ 0.0028 | 44.89 − j17.69 | 1.47 | 0.212 Ω, ΔΓ 0.0023 |
| 17 m | 120.53 − j13.68 | 2.45 | 1.037 Ω, ΔΓ 0.0035 | 48.48 − j21.39 | 1.54 | 0.388 Ω, ΔΓ 0.0038 |
| 15 m | 115.60 − j33.08 | 2.54 | 1.150 Ω, ΔΓ 0.0040 | 50.98 − j21.02 | 1.51 | 0.474 Ω, ΔΓ 0.0045 |
| 12 m | 104.93 − j43.66 | 2.55 | 1.105 Ω, ΔΓ 0.0043 | 52.79 − j19.95 | 1.48 | 0.621 Ω, ΔΓ 0.0057 |
| 10 m | 71.85 − j18.21 | 1.60 | 0.880 Ω, ΔΓ 0.0058 | 47.93 − j6.67 | 1.15 | 0.339 Ω, ΔΓ 0.0035 |

The two formulations agree to ≤1.15 Ω (ΔΓ ≤ 0.0058) on every band of
both parameter sets. **These are the numbers a builder wants.**

Two things the multi-feed census could not have told you:

1. **The physical feedpoint is nowhere near the multi-feed reading.**
   At default parameters the one-coax antenna presents 72–121 Ω, not
   the 40–60 Ω the co-driven decks show — the TL jumpers and the
   parallel combination of four undriven bands transform it
   substantially. Reading multi-feed numbers as physical would mislead
   by up to 75 Ω.
2. **The `opt_coupled` tune does not fully transfer to the physical
   feed.** It was optimised against a per-band multi-feed Z = 50 + 0j
   objective and hits that (X < 1.4 Ω, SWR ≈ 1.05–1.19 above), but the
   *physical* one-coax antenna it produces still carries **−j17 to
   −j21** on four bands (SWR 1.47–1.54). A tune against the physical
   feed is a different optimisation, and this deck shows the gap.

### And closed: the `opt_physical` tune

Finding 2 became antennaknobs#921, and `opt_physical` is the answer: a
re-tune of the same per-band knobs with every objective evaluation
routed through the one-coax reduction (full 5-port Y + jumper-chain
stamp per solve, momwire engine). Starting from `opt_coupled` it
converged in two coordinate-descent passes. Refined (N=63), same
two-formulation protocol as above:

| band | `opt_physical` consensus | SWR₅₀ | bs2 vs PyNEC |
| --- | --- | --- | --- |
| 20 m | 50.44 + j0.35 | 1.01 | 0.256 Ω, ΔΓ 0.0025 |
| 17 m | 50.51 + j0.65 | 1.02 | 0.523 Ω, ΔΓ 0.0052 |
| 15 m | 50.75 + j0.15 | 1.02 | 0.375 Ω, ΔΓ 0.0037 |
| 12 m | 51.60 + j0.44 | 1.03 | 0.396 Ω, ΔΓ 0.0038 |
| 10 m | 50.67 + j0.17 | 1.01 | 0.374 Ω, ΔΓ 0.0037 |

The −j17…−j21 residual is gone; worst SWR₅₀ across the five bands is
1.03 (momwire) / 1.04 (PyNEC). The mesh-sensitivity asymmetry above
repeats on cue: the tune was run at bs2's base mesh, and refining moves
bs2 only 0.5–1.4 Ω, while a base-mesh PyNEC run of the same geometry
reads 4–5 Ω low in R on every band. Same lesson — refine NEC-2 before
believing it on this model.

**Mesh sensitivity is where the two engines differ most.** Between
N=21 and N=63 the bs2 answer moves 0.3–2.1 Ω, while PyNEC moves
3.7–15.4 Ω — the network reduction amplifies NEC-2's base-mesh deficit,
because the reduction inverts the whole 5×5 admittance rather than
reading one diagonal element. **On the physical single-feed model, a
base-mesh NEC-2 run is not trustworthy**; at N=21 it reads 8 Ω low on
20 m and 15 Ω low on 17 m. Refine before believing it. bs2 is close to
converged at the base mesh on both parameter sets.

### Modeling judgment calls

Carried from the single-band verdict, all still in force: 0.5 mm PEC
wire, the retained 0.05 m feed wires, true open tip gaps. On wire gauge
the single-band deck was **measured** rather than argued, and the result
transfers: across 0.5 mm → #16 → #14, feedpoint **R moved less than
0.7 Ω** while **X moved −5.9 Ω**, with all three engines agreeing on the
shift to within 0.03 Ω. So the resistances here are robust to gauge;
**the reactances are not**, and a #16 build would read roughly 3 Ω less
inductive per band. Gain and F/B should not be read off these decks.

## Reproducing

The five multi-feed decks are `band{0..4}_<freq>.nec` in this directory,
exported at default parameters with `daisy_chain=False`; geometry is
identical across them and only the `FR` card differs. The matching
coupled-tuned decks are in `opt_coupled/`. The ladder driver multiplies
each GW's segment count and re-centers every EX segment.
The physical single-feed results come from the builder directly
(`daisy_chain=True`, mesh set by `nominal_nsegs` 21 and 63), since that
model has no deck form. The `opt_physical` tune is
`scripts/tune_hexbeam_5band_physical.py` in antennaknobs, and the
variant is reached as `multiband.hexbeam_5band:opt_physical`. Engines run through antennaknobs' census harness
(`scripts/bench_nec_corpus.py` — nec2c on PATH, momwire ≥ 0.29.0,
`$NEC5_EXE` for the licensed NEC-5 lane; NEC-5 printouts are End-User
Reports, LLNL-CODE-746721). The two 45-solve censuses are 79 s and 108 s
of wall time; the physical-antenna runs are 49 s and 21 s.

The design is `multiband.hexbeam_5band` in the antennaknobs catalog —
the [hosted simulator](https://antennaknobs.dev/) solves it live in its
physical single-feed form. G3TXQ's published 5-band dimensions come from
[antenneX Issue 128](https://www.hexkit.com/files/hexbeam.pdf).
