# CLAUDE.md — missile_defense

## Read PLAN.md first, every session

`PLAN.md` is the authoritative ledger for this effort (SBIR topic DAF26BX06-NV510).
Read it before doing anything else in this directory. It holds the target facts, the
calendar, the task ledger, the risk register, the decisions log and the amendment log.

## Working rules

0. **Respect the phase gates (§1A of PLAN.md).** Work one phase at a time. Do not start
   the next phase until the current phase's written exit criteria are met and the gate has
   been reviewed with Mason. Do not batch several phases into one pass. If a gate's
   criteria look wrong, amend them in §8 — never quietly relax them to let the gate pass.
   The current phase is **D — Data foundation**.
1. **Find the task ID before starting work.** Every unit of work is a ledger row
   (`G-`, `E-`, `S-`, `A-`, `W-`, `X-`). If the work you are about to do has no row, add
   one — with a Definition of Done and a named artifact — before starting.
2. **Update the ledger when you finish.** Set the status and record the artifact path.
   A task is not `DONE` until its artifact exists on disk.
3. **Amend, never drift.** Any change to scope, dates or approach gets a dated row in
   §8 of `PLAN.md` with the reason. Strike old text; do not delete it.
4. **Every number gets a source.** Quantitative values headed for the proposal need a row
   in `analysis/assumptions_register.md` classified `PUBLIC-CITED`, `NOTIONAL-SWEPT` or
   `DERIVED`.
5. **Unclassified, public-domain inputs only.** No classified or customer-supplied
   parameters, and no bulk raw Space-Track pulls, enter this repo. See
   `analysis/compliance/itar_posture.md` (task G-05).
6. **Reproducible or it doesn't count.** Every figure regenerates from a seeded script via
   `scripts/make_figures.py`.

## Layout

```
PLAN.md              the ledger — the master document
mwsim/               the trade-space simulation package
scripts/             entry points (fetch, validate, make figures)
data/raw/            inputs as downloaded, never hand-edited
data/processed/      everything the scripts generate
analysis/            validation notes, compliance, engagement, assumptions register
proposal/            CONOPS, feasibility study, figures, cost, submission package
docs/topic/          the solicitation PDFs
docs/research/       background research
docs/extracted/      text extracted from the PDFs (grep-able)
tests/               pytest; the S-03 propagation validation gate lives here
```

## Stack

Python-first (decision DEC-03): Stone Soup for tracking and metrics, `sgp4`/Skyfield for
propagation, numpy/scipy, matplotlib for figures. Prefer MIT/Apache dependencies — avoid
`pynrlmsise00` (GPLv2), `hypervehicle` (GPLv3) and the AGPL CelesTrak
`fundamentals-of-astrodynamics` repo, since this work may be commercialized.

## Facts that are easy to get wrong

- The Phase III transition path named by the topic is the **Space Modernization Initiative
  (SMI)** — *not* FORGE or DAVE. The background research file says FORGE; the official topic
  PDF says SMI. The topic wins.
- The topic's four Phase II metrics are **accuracy, latency, resilience, coverage**. Every
  analysis artifact maps to at least one.
- The CONOPS is written **system level first**, then our technology's functions.
- SDA MEO missile warning is **notional / planned**, not on orbit. Label it as such.
