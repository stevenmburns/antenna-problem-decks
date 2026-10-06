# Verdict: hentenna (antennaknobs catalog)

**Submitted:** 2026-08-13, by antennaknobs itself — the curator's own
hard case (`specialty.hentenna`, exported by `nec_export`).
**Status: verdict published; re-run four-way (NEC-4.2 added)
2026-10-06 — see the addendum below.**

## The antenna

The classic hentenna: a tall rectangular loop with an interior feed
rung, free space, 28.47 MHz, uniform 0.5 mm wire. The rung is one
center-fed wire (11 segments at the base mesh) — the catalog design's
NEC-2-era short-bridge feed idiom was deliberately removed from the
deck so no segment-length discontinuity sits at the feed and the
verdict cannot be attributed to a modeling quirk. No radius steps
anywhere — this deck probes a DIFFERENT NEC-2 weakness than the
tapered dipole: a multi-junction loop geometry on which NEC-2's
three-term current basis drifts, a documented behavior in the
antennaknobs cross-basis studies long before this repo existed.

## The three-way ladder (as published, 2026-08)

Per-wire segment counts multiplied ×1 / ×3 / ×5 (the fed rung keeps a
center segment at every rung of the ladder).

| engine | ×1 | ×3 | ×5 |
| --- | --- | --- | --- |
| nec2c (raw NEC-2) | 43.24 + j29.33 | 43.36 + j29.87 | 43.37 + j30.30 |
| momwire bs2 | 43.03 + j38.90 | 43.08 + j38.90 | 43.09 + j38.91 |
| NEC-5 | 43.11 + j39.62 | 43.12 + j38.82 | 43.13 + j38.76 |

NEC-5 Richardson pair (×3, ×5): **43.13 + j38.68 Ω**.

## The verdict

The two independent formulations agree: **≈ 43.1 + j38.8 Ω** (0.23 Ω
apart, ΔΓ 0.0023; bs2 is stable to the second decimal over the whole
ladder). Raw NEC-2 gets the resistance
right and the **reactance ~8 Ω low (j30.3 vs j38.8)** — and its ladder
is still crawling upward at ×5, the super-logarithmic basis drift the
antennaknobs cross-basis arbitration documented: it is heading toward
the right answer at a rate that never arrives at practical segment
counts. On this geometry the drift is a property of NEC-2's three-term
current expansion itself, not of any modeling choice in the deck.

Together with the tapered dipole this makes two entries, two distinct
NEC-2 failure classes — radius steps there, junction-fan basis drift
here — with the same two-formulation consensus standing behind both
verdicts.

## 2026-10-06 four-way re-run: NEC-4.2 lands between NEC-2 and the consensus

This is the same ladder, re-run with licensed NEC-4.2 as a fourth
engine and with current momwire. Two more rungs (×9, ×15) were added
to see where each engine settles. All values are at 28.47 MHz.

| engine | ×1 | ×3 | ×5 | ×9 | ×15 |
| --- | --- | --- | --- | --- | --- |
| nec2c (raw NEC-2) | 43.24 + j29.33 | 43.36 + j29.87 | 43.37 + j30.30 | 43.38 + j30.93 | 43.37 + j31.59 |
| NEC-4.2 | 42.92 + j37.08 | 43.11 + j36.21 | 43.16 + j35.87 | 43.17 + j36.44 | 43.19 + j36.30 |
| momwire bs2 | 43.02 + j38.89 | 43.07 + j38.91 | 43.09 + j38.91 | 43.10 + j38.91 | 43.11 + j38.92 |
| NEC-5 | 43.11 + j39.62 | 43.12 + j38.82 | 43.13 + j38.76 | 43.13 + j38.75 | 43.13 + j38.76 |

NEC-5 rows are (N, 2N) Richardson pairs per rung, as before. The NEC-5
(×3, ×5) pair is unchanged at **43.13 + j38.68 Ω**. nec2c and NEC-5
reproduce the published ladder to the digit, and bs2 moved by
≤ 0.01 Ω. bs2 at ×5 sits 0.24 Ω from the NEC-5 pair (ΔΓ 0.0023, as
published). At ×15 bs2 and NEC-5 are 0.16 Ω apart (ΔΓ 0.0016).

**All four engines agree on the resistance:** 43.1–43.2 Ω at every
rung from ×3 up. **They disagree on the reactance, in three
places.**

- **bs2 and NEC-5 read j38.8–j38.9.** Both stay flat from ×5 to ×15.
- **NEC-4.2 reads j35.9–j36.4.** That is 3.0 Ω below bs2 at ×5
  (ΔΓ 0.030) and 2.6 Ω below at ×15 (ΔΓ 0.026). Its ladder is not
  monotone. It falls from j37.08 at ×1 to j35.87 at ×5, rises to
  j36.44 at ×9, and reads j36.30 at ×15. It moves within about
  ±0.3 Ω from ×5 to ×15 and never closes the gap. A Richardson
  extrapolation needs a monotone ladder, so none is quoted for
  NEC-4.2 here.
- **nec2c reads j30.3 at ×5 and j31.6 at ×15**, still climbing
  (7.3 Ω below bs2 at ×15). This is the super-logarithmic crawl
  described above, confirmed two rungs further out.

So NEC-4.2 removes most of NEC-2's reactance deficit on this
multi-junction loop, but not all of it. It settles about 2.5 Ω short
of the bs2/NEC-5 value. We report this disagreement as measured and
have not adjudicated its cause.

**The call, as of 2026-10-06:** unchanged. **≈ 43.1 + j38.8 Ω**, on
two independent formulations (bs2 and NEC-5). Raw NEC-2's reactance
is ~8 Ω low and still drifting. NEC-4.2's is ~2.5–3 Ω low, does not
drift away, and does not converge onto the consensus either.

## Reproducing

`hentenna.nec` is the exported deck, verbatim. Same harness as the
tapered-dipole verdict (nec2c on PATH, momwire ≥ 0.28.1, `$NEC5_EXE`;
NEC-5 printouts are End-User Reports, LLNL-CODE-746721). The design
itself is `specialty.hentenna` in the antennaknobs catalog — the
[hosted simulator](https://antennaknobs.dev/) solves it live on the
non-NEC-2 engines.

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
  deck carries no `EK` card. The run recorded `extended_kernel=False`
  on the momwire solver.
- **NEC-4.2** ignores `EK`; its printout says so.
- **NEC-5** has no `EK` card.

A kernel-matched bs2 run (extended kernel forced on) differs from the
table's bs2 by at most 0.02 Ω at any rung. The kernel is not what
separates the engines here.
