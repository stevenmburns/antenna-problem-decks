# Verdict: hentenna (antennaknobs catalog)

**Submitted:** 2026-08-13, by antennaknobs itself — the curator's own
hard case (`specialty.hentenna`, exported by `nec_export`).
**Status: verdict published.**

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

## The three-way ladder

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

## Reproducing

`hentenna.nec` is the exported deck, verbatim. Same harness as the
tapered-dipole verdict (nec2c on PATH, momwire ≥ 0.28.1, `$NEC5_EXE`;
NEC-5 printouts are End-User Reports, LLNL-CODE-746721). The design
itself is `specialty.hentenna` in the antennaknobs catalog — the
[hosted simulator](https://antennaknobs.dev/) solves it live on the
non-NEC-2 engines.
