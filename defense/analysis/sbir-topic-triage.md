# SBIR/STTR Topic Triage — Research Outline

Paste this above a single topic record (title, number, full description, agency, branch, dates, link). Work the stages in order. **Stop at the first STOP verdict and skip all remaining stages.**

## Context

Respondent is a small software team: strong systems/backend engineering, data pipelines, ML. No lab, no fab, no cleared facility, no aircraft or vessel access. Capable of physical prototypes only where parts are commercially sourceable and assembly is benchtop-scale.

## Operating rules

- **Triage permissively.** Wrongly killing a good topic costs one opportunity out of dozens that recycle each release. Wrongly advancing a bad one costs one deep dive. Advance on "no confirmed killer," not "confirmed promising."
- **Never estimate effort in time units.** Assess tractability via the decisive-experiment question in Stage 3 instead.
- Mark every claim as `[TOPIC TEXT]`, `[SEARCHED]`, or `[INFERRED]`. Never present an inference as fact.
- If a stage's answer is genuinely unknown after a reasonable search, write `UNKNOWN` and advance. Unknown is not a kill.
- Quote the topic's own words when identifying deliverables and requirements. Do not paraphrase specs.

---

## Stage 0 — Mechanical screen

*No research. Read the topic number and scan the text for fixed phrases.*

- **T0.1** Direct-to-Phase-II? Check the title for `DIRECT TO PHASE II` and the body for prior-feasibility language. → **STOP** unless prior non-SBIR R&D establishing feasibility can be documented.
- **T0.2** SBIR or STTR? Position 6 of the topic number (`B` = SBIR, `T` = STTR). STTR requires a research-institution partner at ≥30% of work, small business ≥40%. → **FLAG**, not a stop.
- **T0.3** Scan for `classified`, `no foreign influence`, `facility clearance`, `ITAR`, `32 U.S.C. § 2004.20`. → **FLAG** with the exact quoted phrase.
- **T0.4** Close date vs. today. Registration prerequisites (SAM.gov UEI, SBA Company Registry) must already exist or be in flight. → **FLAG** if not yet registered.

**Output:** `STOP` / `ADVANCE` + flags.

---

## Stage 1 — Close read (one pass over the description)

- **T1.1 — Literal Phase I deliverable.** Quote the sentence stating what Phase I produces. Classify: (a) study/algorithms/simulation, (b) software artifact, (c) physical article delivered to government, (d) unstated. Type (c) → **STOP** unless benchtop-sourceable.
- **T1.2 — Capability gap.** List concretely what the team would need and does not have: named datasets, instruments, facilities, clearances, domain SMEs, platform access. One line each, no hedging.
- **T1.3 — Government data wall.** Does the core input arrive only after award (GFE, classified rule sets, government-furnished data, program-internal specs)? If yes, Phase I is a writing exercise and incumbents hold the data. → **STOP** if the wall sits on the critical path.
- **T1.4 — Restated problem.** One sentence, in plain engineering terms, with no defense vocabulary. If this can't be written, the topic isn't understood yet — say so and keep reading rather than killing.

**Output:** deliverable type, gap list, wall verdict, plain-English restatement.

---

## Stage 2 — Landscape (≈3 searches)

- **T2.1 — Prior awards.** Search SBIR.gov awards for the topic's distinctive nouns and for the topic number stem across earlier years. Report: recurring topic? recurring winner? If one firm has won successive iterations, the topic is likely wired. *Highest information-per-minute question in this outline.*
- **T2.2 — Named program of record.** Extract any named program, office, or system (e.g. PMA-213, AEGIS, GPNTS, FAMM). Identify the likely incumbent integrator. Determine whether the realistic posture is prime, sub, or displacement.
- **T2.3 — Commercial state of the art.** Does a civilian product already do the general version of this? If yes, name it, and state precisely what the defense-specific delta is. "There is no delta" → **STOP**.

**Output:** competitive posture in 3 sentences + the defense-specific delta.

---

## Stage 3 — Fit and angle (survivors only)

- **T3.1 — Riskiest assumption + decisive experiment.** Name the single technical assumption most likely to be wrong, and the cheapest experiment using *public or synthetic data* that would test it. If no such experiment can be named, the topic isn't understood well enough — return to Stage 1, do not kill.
- **T3.2 — Reuse.** What does the team already have that constitutes most of a solution? Existing systems, prior code, domain knowledge. "Nothing" is permitted but weakens the case against topics with real reuse.
- **T3.3 — Non-government customer.** Who buys this if the government disappears? Dual-use determines whether Phase I is an asset or a detour. The topic's own `Dual Use:` sentence, where present, is a strong hint about how the sponsor frames it.
- **T3.4 — Differentiator.** One sentence: why this team rather than an incumbent with twenty years of platform access.

---

## Required output block

```
TOPIC:        <number> — <title>
BRANCH:       <branch>   PROGRAM: SBIR|STTR   CLOSES: <date>
VERDICT:      PURSUE | HOLD | KILL
STAGE REACHED: 0|1|2|3

DELIVERABLE:   <type + quoted phrase>
KILL REASON:   <if killed>
KILL CLASS:    PERMANENT | CONTINGENT     # see below
FLAGS:         <STTR / classification / foreign-ownership / registration>

PLAIN PROBLEM: <one sentence, no defense jargon>
GAPS:          <bulleted, concrete>
LANDSCAPE:     <incumbency + program of record + commercial SOTA>
DELTA:         <defense-specific difference>
EXPERIMENT:    <cheapest decisive test on public data>
REUSE:         <what we already have>
DUAL USE:      <non-government buyer>
DIFFERENTIATOR:<one sentence>
CONFIDENCE:    HIGH | MEDIUM | LOW + what would raise it
```

### Kill classes

Log the reason, not just the kill — topics recycle across releases.

- **PERMANENT** — structural and unchanging: requires an anechoic chamber, a wafer fab, a cleared facility, delivery of a physical article the team cannot build.
- **CONTINGENT** — true today, may be false next release: no labeled dataset yet, no RI partner for the STTR variant, registration incomplete, DP2 with no prior feasibility work.

When a new release drops, re-run only the CONTINGENT kills.

---

## Batch mode

When run across a full release rather than one topic:

1. Run Stage 0 over every topic (mechanical, near-free).
2. Run Stage 1 over Stage 0 survivors.
3. Run Stage 2 over Stage 1 survivors only.
4. Run Stage 3 over the final handful.

Cost per topic rises with each stage while topic count falls, so total cost stays roughly flat. Do **not** convert this into a flat scorecard applied uniformly — that pays full price on every topic and is the failure mode this outline exists to avoid.
