# antenna-problem-decks

Antennas that modeling programs disagree about — submitted by the
community, each answered with a published four-way verdict.

## What this is

[antennaknobs](https://antennaknobs.dev/) runs a cross-validation of
four formulations — nec2c (NEC-2), NEC-4.2, NEC-5, and
[momwire](https://github.com/stevenmburns/momwire) — and publishes
per-case verdicts with their evidence on the
[validation page](https://antennaknobs.dev/reference/validation/).
The curated test corpus has its curator's blind spots; this repo is the
intake for the decks it would never have picked.

## Submitting

Open a [deck submission](../../issues/new?template=submit-deck.yml).
You'll need the NEC deck text and a sentence about what disagreed or
what you don't trust. NEC-2-dialect wire decks are ideal, and NEC-4 or
NEC-5 dialect decks are welcome. Wires over, crossing into, or buried
in real ground are in scope: momwire solves buried and crossing wires,
NEC-4.2 serves its Sommerfeld grounds (GN 2 and GN 3) with buried wires,
and NEC-5 serves its own. Surface patches remain out of scope and get
an honest out-of-scope note rather than a verdict.

## What happens to a submission

Each accepted deck is committed under `decks/<slug>/` together with its
`verdict.md`: mesh ladders on all four engines, Richardson-extrapolated
limits, pairwise reflection-coefficient distances, and a plain-language
call. Verdicts also feed the antennaknobs validation page. The deck
stays attributed to its submitter.

## Layout

    decks/<slug>/<name>.nec    the submitted deck, verbatim
    decks/<slug>/verdict.md    the four-way verdict and its numbers
    decks/<slug>/study/        the scripts that produced it, where a case has them

NEC-4.2 and NEC-5 are licensed programs run from the maintainer's own
licensed binaries; nothing of either is distributed here. Numbers read
from their printouts are cited as End-User Reports: NEC-4.2,
LLNL-CODE-491368; NEC-5, LLNL-CODE-746721.
