# antenna-problem-decks

Antennas that modeling programs disagree about — submitted by the
community, each answered with a published three-way verdict.

## What this is

[antennaknobs](https://antennaknobs.dev/) runs a cross-validation of
three independent formulations — nec2c (NEC-2), NEC-5, and
[momwire](https://github.com/stevenmburns/momwire) — and publishes
per-case verdicts with their evidence on the
[validation page](https://antennaknobs.dev/reference/validation/).
The curated test corpus has its curator's blind spots; this repo is the
intake for the decks it would never have picked.

## Submitting

Open a [deck submission](../../issues/new?template=submit-deck.yml).
You'll need the NEC deck text and a sentence about what disagreed or
what you don't trust. NEC-2-dialect wire decks are ideal; patch and
buried-wire models get an honest out-of-scope note rather than a
verdict.

## What happens to a submission

Each accepted deck is committed under `decks/<slug>/` together with its
`verdict.md`: mesh ladders on all three engines, Richardson-extrapolated
limits, pairwise reflection-coefficient distances, and a plain-language
call. Verdicts also feed the antennaknobs validation page. The deck
stays attributed to its submitter.

## Layout

    decks/<slug>/<name>.nec    the submitted deck, verbatim
    decks/<slug>/verdict.md    the three-way verdict and its numbers
