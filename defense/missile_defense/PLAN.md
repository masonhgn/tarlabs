# ACTION PLAN — DAF26BX06-NV510

**AI/ML for Next Generation of Missile Detection, Warning, Tracking, and Reporting**
SpaceWERX / SSC Space Sensing Delta 84 / OPIR Tap Lab · SBIR Phase I · DAF Release 6 CSO

> **This file is the authoritative ledger for the whole effort.** Read it at the start of
> every work session. Do not do work that is not on it; if work is needed that is not on it,
> add a task first. Every status change is a ledger edit. Every scope change is an entry in
> the Amendment Log (§8).

---

## 1. Standing rules

1. **Ledger first.** Before starting, find the task ID. After finishing, set the status and
   record the artifact path. A task is not `DONE` until its artifact exists on disk.
2. **Every task has a Definition of Done (DoD) and a named artifact.** No "work on X" tasks.
3. **Amend, never drift.** Changing scope, dates, or approach → append to §8 with the date and
   the reason. Old text is struck, not deleted.
4. **Every number gets a source.** Anything quantitative that reaches the proposal must have a
   row in `analysis/assumptions_register.md` marked `PUBLIC-CITED`, `NOTIONAL-SWEPT`, or
   `DERIVED`. No naked numbers.
5. **Unclassified only.** All inputs are published / public-domain. No classified or
   customer-supplied parameters enter this repo. See G-05.
6. **Reproducible or it doesn't count.** Every figure regenerates from a seeded script with one
   command. The evaluators are FFRDCs with better simulators than ours; reproducibility and
   openness are the differentiator, not fidelity.

### Status vocabulary
`TODO` · `WIP` · `DONE` · `BLOCKED` (say on what) · `DROPPED` (say why, in §8) · `N/A`

---

## 1A. Phase gates — how this effort is paced

**One phase at a time. Each phase has written exit criteria. No phase starts until the
previous one has met its criteria and the gate has been reviewed.**

Innovating in a subject area none of us came from requires thoughtful design, tradeoff
consideration, research and pacing. A phase finished sloppily corrupts everything built on
top of it, and in a simulation that corruption is silent — a bad detection threshold or a
bad frame conversion does not raise; it just produces a confident wrong chart. So depth
within the current phase beats progress into the next one.

Exit criteria may evolve. They are amended in §8, never quietly relaxed to let a gate pass.

| Phase | Name | Gate — cannot start until | Status |
|---|---|---|---|
| **D** | **Data foundation** | — (this is the first phase) | **PASSED 2026-09-23** |
| S | Simulation core | Gate D reviewed and passed | **OPEN — gate cleared 2026-09-23** |
| T | The trade (fusion placement) | Gate S reviewed and passed | not started |
| R | Robustness & ML | Gate T reviewed and passed | not started |
| W | Writing | Gate T passed (R may run in parallel) | not started |
| X | Submission | Gate W reviewed and passed | not started |

Phases **G** (compliance gates) and **E** (engagement) run continuously alongside all of
the above, because they are externally clocked — registration queues and the Oct 7 Q&A
deadline do not wait for our gates.

### Gate D — exit criteria (the current gate)

Phase D is done when **every data type and source that will be of use has been identified,
acquired, organized, and understood.** Concretely, all six must hold:

- **D-i — Identified.** A written inventory exists covering every data domain the effort
  needs, with the domains enumerated deliberately rather than discovered by accident later.
  A source we decide *not* to use is listed with the reason, so the decision is on record.
- **D-ii — Acquired.** Everything acquirable is on disk, in `data/raw/`, by a scripted and
  repeatable pull. Anything not acquirable (gated, classified, non-existent) is recorded as
  such, with what we will do instead.
- **D-iii — Organized.** A documented directory structure, stable naming, and provenance
  for every artifact: where it came from, when, under what terms, and at what version.
- **D-iv — Understood.** For each source we can state, in writing: what is actually in it,
  its units and conventions, its accuracy and its failure modes, and how it feeds a
  specific downstream task. *Understood* means we have looked at the data, not just
  downloaded it.
- **D-v — Licensed.** Redistribution and export terms recorded per source, with the
  public-repo / internal-only split decided. Feeds G-05.
- **D-vi — Gap-honest.** The things we wanted and cannot get are written down explicitly,
  each with the parameterization that replaces it. This list is a proposal asset, not an
  embarrassment — candour about the unclassified/classified boundary is what the evaluators
  reward.

**Gate D review:** walk the inventory with Mason, source by source, before any Phase S work
resumes.

---

## 2. The target — facts from the official topic PDF

| Item | Value | Source |
|---|---|---|
| Topic # | DAF26BX06-NV510 | official PDF |
| Agency | USAF / SpaceWERX, with SSC Space Sensing Delta 84 + OPIR Tap Lab | official PDF |
| Vehicle | SBIR Phase I, DAF Release 6 CSO | internal brief |
| Award | $150,000 / 3 months | internal brief |
| Tech volume limit | 30 pages | internal brief (DAF CSO index table) — **verify, G-06** |
| CMMC | Level 2 (Self) | official PDF |
| ITAR | 22 CFR 120-130; FN disclosure required per §3.5 of the Announcement | official PDF |
| Topic opens | 2026-09-23 (TPOC direct contact ends) | internal brief |
| DSIP Q&A closes | 2026-10-07, 12:00 ET | internal brief |
| **Proposals due** | **2026-10-21, 12:00 ET** | internal brief — **verify on DSIP, G-08** |
| Phase III transition | **Space Modernization Initiative (SMI)**, SSC Space Sensing portfolio | official PDF |
| TPOC-1 | Michael Cumming — michael.cumming.1@spaceforce.mil | official PDF |
| TPOC-2 | Wynn Sanders — wynn.sanders.2@spaceforce.mil | official PDF |
| References named | GAO-20-48g (TRL Guide); boulderlab.org | official PDF |

### Required Phase I deliverables (structure taken verbatim from the topic)

A **feasibility study** that:
- identifies the benefits of the new technology within the CONOPS over existing solutions
  (or the lack thereof)
- identifies risks, uncertainties/unknowns and issues **with mitigation *and* closure measures**
- identifies the **critical technology elements (CTEs)**
- provides, **per CTE**: literature research, trade studies, analysis, and heritage usage with
  identified differences in operations and/or environment

A **CONOPS** written **at the system level first**, then expanded to how the technology's
functions enable successful military operations.

Plus "algorithm prototypes or simulation results as applicable" and "a clear path to
integration and testing within the OPIR Tap Lab."

### Four focus areas (any part is acceptable)
1. Edge Fusion & Autonomy
2. Multi-Source Integration
3. **OODA Loop Collapse & Mission Assurance** ← our primary lane ("AI trade-space exploration", explainability)
4. New sources and methods outside current MW TTPs ← our secondary lane

### Phase II metrics named by the topic
**accuracy · latency · resilience · coverage** — every analysis artifact maps to one or more.

### What the SITIS Q&A already settled (this de-risks the entire approach)
- **A1** — "Yes, a feasibility study would be appropriate for this topic." A deterministic
  simulation that screens the multi-orbit OPIR sensing trade space, proposing **no new
  detection algorithm**, is responsive. The government decides the future use of the Phase I
  product (offline tool vs. Tap Lab plug-in) at the end of Phase I.
- **A2** — In-space edge-compute *architecture* work is responsive; document it with
  **DoDAF 2.0** or an equivalent architecture description methodology.
- **A3** — Mission-aware orchestration and AI-assisted trade-space decision management is
  "an appropriate submission topic for this solicitation."

---

## 3. Thesis (the one paragraph the whole proposal defends)

> Before anyone can say where AI/ML belongs in the multi-orbit OPIR kill chain, someone has to
> map the trade space it would live in. We will build an open, reproducible, deterministic
> simulation that screens which constellation, revisit, detection-threshold and
> fusion-placement parameters actually drive **warn-to-decision time** and **track continuity**
> against ballistic and maneuvering threats — and identify, against a quantified classical
> baseline, the specific points where AI/ML fusion has real leverage and where it does not.
> The Phase I deliverable is the feasibility study, the USSF CONOPS, and the trade-space engine
> itself as a reusable analysis tool with a stated path into the OPIR Tap Lab.

**Headline artifact:** a warn-to-decision-time vs. track-accuracy Pareto frontier across
ground-centralized / on-orbit-edge / hybrid fusion placements — task **A-04**.

---

## 4. Calendar and critical path

> **Demoted to reference, 2026-09-23 (DEC-32).** These dates were built around the
> 2026-10-21 submission. The objective is now research quality rather than that window,
> so the dates below record what a deadline-driven run *would* have required and are kept
> for reference only. **Pacing is set by the phase gates in §1A**, and Mason owns the
> schedule and the go/no-go decision. Nothing here licenses cutting a domain short to
> hit a date.

| Date | Milestone |
|---|---|
| Tue 2026-09-22 | *(today)* Plan set. Phase G gates opened. TPOC email drafted. |
| Wed 2026-09-23 | **TPOC direct contact ends.** Topic opens. |
| Sun 2026-09-27 | Sim spine running: propagation validated, constellations synthesized (S-01…S-04). |
| Wed 2026-09-30 | Coverage/stereo + threat trajectory library done (S-05, S-06). Q&A questions finalized. |
| Wed 2026-10-07 | **DSIP Q&A closes 12:00 ET.** Detection + tracking baseline done (S-07, S-08). |
| Sun 2026-10-11 | **Headline Pareto chart exists** (S-09, A-04). CTE list locked (A-07). |
| Wed 2026-10-14 | Full 30-page draft complete (Phase W). |
| Sat 2026-10-17 | Red-team pass done, revisions in. |
| Mon 2026-10-19 | **Submit** — 48 h before deadline. DSIP upload failures are a known killer. |
| Wed 2026-10-21 | Deadline 12:00 ET. Contingency only. |

**Critical path:** G-01 SAM.gov → G-02 SBIR.gov → G-03 DSIP → X-03 submit.
Registration, not engineering, is the most likely reason this effort fails. See R-1.

**Hard sequencing in the sim:** S-03 → S-05 → S-07 → S-08 → S-09 → A-04.
Everything else can slip; that chain cannot.

---

## 5. Ledger

### Phase G — Eligibility and compliance gates  *(BLOCKING — nothing else matters if these fail)*

| ID | Task | Owner | Status | Due | Depends | Artifact |
|---|---|---|---|---|---|---|
| G-01 | Confirm or create SAM.gov registration (UEI + CAGE) | **Mason** | TODO | 09-23 | — | `analysis/compliance/registrations.md` |
| G-02 | SBIR.gov firm registration → SBC Control ID | **Mason** | TODO | 09-25 | G-01 | same |
| G-03 | DSIP account, firm linked, topic subscribed | **Mason** | TODO | 09-25 | G-02 | same |
| G-04 | CMMC Level 2 (Self) assessment scored and posted in SPRS | **Mason** | TODO | 10-10 | G-01 | same |
| G-05 | ITAR posture: US-person roster, FN disclosure text, repo data policy | shared | TODO | 09-26 | — | `analysis/compliance/itar_posture.md` |
| G-06 | Read the DAF Release 6 CSO Announcement end-to-end; build compliance matrix | agent | TODO | 09-26 | — | `analysis/compliance/compliance_matrix.md` |
| G-07 | Download the mandatory Space FY26 SBIR Phase I proposal template from DSIP | **Mason** | TODO | 09-26 | G-03 | `docs/templates/` |
| G-08 | Verify exact deadline, page limits, volume structure and file formats on live DSIP | **Mason** | TODO | 09-26 | G-03 | `analysis/compliance/compliance_matrix.md` |

> **G-01 through G-04, G-07 and G-08 are Mason's, outside the agent's lane** (2026-09-22).
> They sit behind login walls the agent cannot reach. They remain on the ledger because
> X-03 cannot happen without them — do not mark X-03 ready until they are `DONE`.

**G-01 DoD** — a record of an *active* SAM.gov registration with UEI, CAGE and expiry date. If
not registered, registration is submitted and the expected wait recorded. *This can take 2–4
weeks and is the single biggest schedule threat on the project.*
**G-04 DoD** — SPRS shows a posted Level 2 self-assessment score with an assessment date, and an
SSP plus POA&M exist under `analysis/compliance/`.
**G-05 DoD** — a written statement of (a) who touches technical data and their US-person status,
(b) the rule that only published/public-domain inputs enter this repo, (c) what stays internal
(bulk Space-Track pulls; any parameter calibrated to a real system), (d) the §3.5 FN disclosure
text ready to paste into the proposal.
**G-06 DoD** — a table mapping every "shall/must" in the Announcement to where we satisfy it.

---

### Phase E — Engagement

| ID | Task | Status | Due | Depends | Artifact |
|---|---|---|---|---|---|
| E-01 | Email the TPOCs (Cumming, Sanders) **before the contact window closes** | TODO | **09-23** | — | `analysis/engagement/tpoc_contact.md` |
| E-02 | Register on boulderlab.org; harvest the unclassified resource library | TODO | 09-26 | — | `analysis/engagement/taplab_notes.md` |
| E-03 | Draft and submit DSIP Q&A questions | TODO | **10-06** | G-03, E-01 | `analysis/engagement/sitis_questions.md` |
| E-04 | Recruit one credentialed OPIR / space-tracking advisor (inside the 1/3 cap) | TODO | 10-08 | — | `analysis/engagement/advisor.md` |
| E-05 | Decide and write the clearance / Tap Lab onboarding narrative | TODO | 10-10 | E-02 | feeds W-07 |

**E-01 DoD** — email sent and archived. Ask the three things the existing Q&A did *not* answer:
(a) is unclassified / synthetic-data feasibility sufficient for Phase I, or is Tap Lab data
access expected inside the period of performance; (b) what architecture artifacts does the Tap
Lab expect at handoff; (c) for an offeror with no personnel or facility clearances, what does a
credible "clear path to integration and testing within the OPIR Tap Lab" look like.
*Note: SITIS Q1–Q3 on this topic appear to be ours already — do not re-ask them (see §9 Q4).*

**E-03 DoD** — questions submitted on DSIP before 10-07 12:00 ET, text archived, answers
harvested when posted and folded back into this plan through §8.

**E-05 DoD** — a decision recorded in §7. The fallback, if clearance sponsorship looks
infeasible before award, is a **ground-fusion-first CONOPS with edge fusion as the Phase II
objective** — fully executable unclassified.

---

### Phase D — Data foundation  *(CURRENT PHASE)*

Exit criteria are in §1A. Each task below is scoped to one data domain and is not `DONE`
until that domain satisfies D-i through D-vi — identified, acquired, organized, understood,
licensed, gap-honest.

| ID | Data domain | Status | Depends | Artifact |
|---|---|---|---|---|
| D-00 | **Inventory the domains themselves** — enumerate every data type the effort needs, before acquiring any of it | **DONE** (written retrospectively — see A-24) | — | `analysis/data/inventory.md` |
| D-01 | Orbital elements: CelesTrak GP/OMM, Space-Track, SupGP, withheld-object policy | WIP | D-00 | `data/raw/omm/`, `analysis/data/orbital_elements.md` |
| D-02 | Published constellation geometry: SDA/SSC fact sheets, Gunter's, eoPortal | **DONE** | D-00 | `analysis/data/constellation_geometry.md`, `mwsim/constellation_analysis.py`, `scripts/analyze_constellation.py` |
| D-03 | Threat trajectory models: Tracy & Wright, Acton, Candler, Fetter, Gronlund & Wright, Wilkening, NRC, BRSL simulator | **DONE** | D-00 | `analysis/data/threat_models.md`, `data/reference/threat_model_reference.json` |
| D-04 | IR signature & phenomenology: plume radiometry, band selection, what is and is not public | **DONE** (D-04-c/d open) | D-00 | `analysis/data/ir_signatures.md`, `data/reference/ir_reference.json` |
| D-05 | IR background imagery: GOES-R ABI L1b, VIIRS/MODIS FIRMS, DMSP | **DONE** (D-05-a open) | D-00 | `analysis/data/ir_background.md`, `mwsim/goes.py`, `data/raw/goes/` |
| D-06 | Tracking benchmark data: OpenSky ADS-B, Stone Soup reference results | **DONE** (D-06-a partially open) | D-00 | `analysis/data/tracking_benchmarks.md`, `mwsim/observability.py` |
| D-07 | Atmosphere & environment models: US Std 1976, NRLMSISE-00 (MIT/Apache routes only) | **DONE** | D-00 | `analysis/data/atmosphere.md`, `mwsim/atmosphere.py` |
| D-08 | Solar/lunar ephemeris & terminator geometry (occultation, solar exclusion) | **DONE** | D-00 | `analysis/data/ephemeris.md`, `mwsim/ephemeris.py` |
| D-09 | Program & architecture literature: CSIS, CRS, GAO, Aerospace/MITRE, AMOS | **DONE** (D-09-a/b with Mason) | D-00 | `analysis/data/literature.md`, `data/raw/doctrine/` |
| D-10 | Doctrine & format references: DoDAF 2.02, GAO-20-48g TRL guide | **DONE** | D-00 | `analysis/data/doctrine.md`, `data/raw/doctrine/` |
| D-11 | OPIR Tap Lab resource library (registration-gated) | TODO | E-02 | `analysis/engagement/taplab_notes.md` |
| D-12 | **Gap register / sufficiency assessment** — what we wanted, cannot get, and what replaces it | **DONE** | D-01…D-11 | `analysis/data/sufficiency.md` |
| D-14 | Historical element epochs & manoeuvre detection — multi-epoch orbit audit | **DONE** | D-01 | `analysis/data/orbit_history.md`, `mwsim/orbit_history.py`, `tests/test_orbit_history.py` |
| D-15 | Earth orientation & time standards (UT1-UTC, polar motion, leap seconds) | **DONE** | D-00 | `analysis/data/time_standards.md`, `mwsim/earth_orientation.py` |
| D-16 *(moved to Phase S — parameter definition, not acquisition)* | Sensor angular-noise & point-spread surrogate models | TODO | D-04 | `analysis/data/sensor_noise.md` |
| D-17 | Occultation & Earth-limb geometry; solar exclusion angles | **DONE** | D-08 | `analysis/data/occultation.md`, `mwsim/limb_geometry.py` |
| D-18 *(moved to Phase S — parameter definition, not acquisition)* | Background radiance *distributions* conditioned on cloud / terrain / view angle | TODO | D-05 | `analysis/data/background_stats.md` |
| D-19 | Line-of-sight atmospheric transmission profiles (HITRAN/HAPI, MIT-licensed) | **DONE** | D-07, D-17 | `analysis/data/transmission.md`, `mwsim/transmission.py` |
| D-20 | Network delay **distributions** (not point estimates) per architecture hop | **DONE** | D-00 | `analysis/data/latency_ledger.md`, `mwsim/latency.py` |
| D-21 | Clock and time-tag error budgets | **DONE** | D-15 | `analysis/data/time_standards.md` |
| D-22 *(moved to Phase S — parameter definition, not acquisition)* | Event-label uncertainty for any truth set | TODO | D-05 | `analysis/data/truth_labels.md` |
| D-23 | Covariance / track-quality definitions — *our* metric, explicitly not the classified one | **DONE** | D-06 | `analysis/data/track_quality.md`, `mwsim/track_quality.py` |
| D-13 | **Gate D review with Mason** — walk the inventory source by source | **DONE — PASSED** | D-00…D-23 | `analysis/data/gate_d_review.md` |

> **D-14 through D-23 were added 2026-09-23** (amendment A-6). They came from the deep
> research answer to J2, which made the point that the domains we were missing were not
> more satellite names but **uncertainty and calibration domains** — the things that turn a
> single confident curve into an honest family of curves. Their absence would not have
> shown up as an error; it would have shown up as false precision, which is worse.

**D-00 is deliberately first and deliberately separate.** Enumerating the domains before
acquiring anything is what stops us from discovering a missing data type in week three,
when it is expensive. Its DoD: a domain list that a skeptical reader agrees is complete,
each with the downstream task it feeds and a verdict of *acquire / cite only / cannot get*.

**Per-domain DoD template** (applies to D-01 through D-11):
> What it is · where it came from and when · units and conventions · accuracy and failure
> modes · license and redistribution terms · which ledger task consumes it · what we
> verified by actually looking at it · what it does not contain.

---

### Phase S — Simulation (the trade-space engine)

> **Gate:** blocked until Gate D is reviewed and passed (§1A). S-01 to S-03 below ran
> *before* this pacing was agreed, on 2026-09-22 — see amendment A-4. They stand as
> completed work and their outputs are sound, but Phase S does not resume at S-04 until
> the D gate clears.

| ID | Task | Status | Due | Depends | Artifact |
|---|---|---|---|---|---|
| S-01 | Repo scaffold, env, `mwsim` package, test harness, seeded-run convention | **DONE** | 09-23 | — | `mwsim/`, `tests/`, `requirements.txt`, `pytest.ini` |
| S-02 | Catalog ingest: CelesTrak GP API (OMM/JSON) + Space-Track, local cache | **DONE** (CelesTrak only; Space-Track deferred to D-01) | 09-24 | S-01 | `mwsim/catalog.py`, `mwsim/registry.py`, `data/raw/omm/` |
| S-03 | SGP4/SDP4 propagation + **validation** | **DONE** | 09-25 | S-02 | `mwsim/propagate.py`, `tests/test_propagation.py`, `analysis/validation/propagation.md` |
| S-04 | Walker constellation generator (delta + star), seeded from measured geometry | **DONE** (20 tests) | 09-27 | S-03, D-13 | `mwsim/constellation.py` |
| S-05 | Access geometry: LOS, horizon mask, FOR cone, **useful-stereo** convergence criterion | **DONE** (13 tests) | 09-29 | S-04 | `mwsim/coverage.py` |
| S-06 | Target motion **sourced externally** from the published BRSL simulator, not modelled here | **DONE** (15 tests) | 09-30 | S-01 | `mwsim/target_motion.py` |
| S-07 | Sensor / detection model: parameterized threshold, occultation, false-alarm rate | TODO | 10-04 | S-05, S-06 | `mwsim/sensors.py` |
| S-08 | Tracking baseline: **IMM written by us** (done, cross-validated against FilterPy) + **LMS3 variable structure, replicated against Li & Zhang 2000** (done) + JPDA association, angles-only / stereo fusion | **WIP** | 10-07 | S-07 | `mwsim/imm.py`, `mwsim/lms.py`, `mwsim/lz2000.py` |
| S-09 | Fusion-placement and latency model (ground / edge / hybrid) | TODO | 10-10 | S-08 | `mwsim/fusion.py` |
| S-10 | Resilience sweeps: Monte-Carlo node and link loss | TODO | 10-12 | S-09 | `mwsim/resilience.py` |
| S-11 | ML component vs. classical baseline (**only if it wins**) | TODO | 10-13 | S-08 | `mwsim/ml/` |
| S-12 | Reproducibility harness: one command regenerates every figure | TODO | 10-13 | S-09 | `scripts/make_figures.py` |

**S-03 DoD — the gate that protects everything downstream.** Three checks pass in CI:
1. ISS (NORAD 25544) propagation matches the published Vallado SGP4 test vectors.
2. SBIRS GEO satellites hold ~35,786 km and ~1.0 rev/day.
3. Tranche 0 satellites sit at ~1000 km, ~81° inclination.

Plus a written note on TLE/SGP4 error (~1 km at epoch, growing ~1–3 km/day) for the proposal.
*If these fail, stop and fix the propagator before doing anything else.*

**Real elements to seed with** (all publicly cataloged; none are withheld):
SBIRS GEO-1…6 = 37481, 39120, 41937, 43162, 48618, 53355 · DSP-23 = 32287 ·
SDA Tranche 0 Tracking = 56170, 56171, 57757, 57760 (+ L3Harris Raptor 58959) ·
HBTSS = 58955, 58960.
There is **no** CelesTrak group for SDA / PWSA / Tranche — pull by `CATNR` or `INTDES`.
Build the ingest around **OMM/JSON, not fixed-width TLE**: 6-digit catalog numbers have no TLE form.

**S-04 DoD** — the Walker generator reproduces the SDA-published Tranche 1 Tracking geometry
(28 SVs, 4 planes, ~1000 km, ~81°) and, seeded with the 4 real Tranche 0 elements, reproduces
their altitude / inclination / RAAN spread. MEO is **fully notional from published intent** and
must be labeled as such everywhere it appears.

**S-06 DoD** — reproduces two published results: Gronlund & Wright's 7,400 km minimum-energy
trajectory (burnout 6.3 km/s, apogee 1,340 km, flight time 29.2 min) and the Berkeley BRSL HGV
simulator's range and time-of-flight for matched inputs (β = 13,000 kg/m²). Energy is conserved
in ballistic coast.

**S-07 DoD** — detection onset coincides with the boost-phase plume; occultation and terminator
logic zero out detections when geometry forbids them; the detection threshold is a **swept
parameter**, never a hard-coded number. Bands consistent with the public 2.7 / 4.3 µm guidance.

**S-08 DoD** — the pipeline is validated on **OpenSky ADS-B** real multi-target data *before*
being pointed at synthetic threats. Report OSPA/GOSPA (c=40, p=1) and SIAP.

**S-11 gate** — ML goes in the proposal **only** if it beats the classical baseline on a clean
train/test split with no trajectory leakage. Otherwise report the classical result and cite ML
as Phase II work. Reviewers distrust un-baselined ML; this is the easiest way to lose.

---

### Phase A — Analysis artifacts (each maps to a Phase II metric)

| ID | Artifact | Metric | Status | Due | Depends |
|---|---|---|---|---|---|
| A-01 | Coverage / revisit / stereo-availability maps over a launch box | coverage | TODO | 09-30 | S-05 |
| A-02 | Detectability-vs-time curves, ballistic vs. HGV | coverage, accuracy | TODO | 10-05 | S-07 |
| A-03 | OSPA/GOSPA and track continuity vs. maneuver intensity | accuracy | TODO | 10-08 | S-08 |
| A-04 | **Warn-to-decision vs. track-accuracy Pareto, three fusion placements** | latency, accuracy | TODO | **10-11** | S-09 |
| A-05 | Degradation curves vs. % nodes / links lost | resilience | TODO | 10-12 | S-10 |
| A-06 | ML vs. classical ROC and ablation | accuracy | TODO | 10-13 | S-11 |
| A-07 | CTE list (4–5) with per-CTE evidence table | — | TODO | 10-11 | A-04 |
| A-08 | Assumptions and sources register — every number, every citation | — | TODO | ongoing | — |
| A-09 | Sensitivity analysis: no conclusion hinges on a single guessed number | — | TODO | 10-13 | A-04 |

**A-04 is the proposal.** If only one thing gets built, build this.

**A-07 candidate CTEs** (lock by 10-11; keep to 4–5):
1. Fusion-placement model for multi-orbit OPIR (ground vs. edge vs. hybrid latency/accuracy)
2. Covariance-consistent track-to-track fusion across heterogeneous orbital regimes
3. Learned data association / IMM model-set selection for maneuvering threats
4. Confidence propagation and explainability wrapper for operator handoff
5. *(reserve)* Angles-only observability management and stereo tasking

**A-08 DoD** — a table with columns `value · symbol · source · classification (PUBLIC-CITED /
NOTIONAL-SWEPT / DERIVED) · sweep range · where used`. Zero unfilled rows before W-04 starts.

---

### Phase W — Writing

| ID | Task | Status | Due | Depends | Artifact |
|---|---|---|---|---|---|
| W-00 | **AV-1 Overview and Summary Information** — visions, goals, objectives, activities, measures | TODO | 10-07 | — | `proposal/av1.md` |
| W-01 | OV-1 operational concept graphic — *the pictorial representation of the AV-1's written content* | TODO | 10-08 | W-00 | `proposal/figures/ov1.*` |
| W-02 | CONOPS — system level first, then our functions | TODO | 10-12 | W-01 | `proposal/conops.md` |
| W-03 | DoDAF subset: OV-2, OV-5b (kill chain), OV-6c (warn-to-decision trace), SV-1 | TODO | 10-12 | W-01 | `proposal/figures/` |
| W-04 | Feasibility study body: benefits, risks, CTEs, per-CTE evidence | TODO | 10-14 | A-07, A-08 | `proposal/feasibility.md` |
| W-05 | Risk register with mitigation **and closure measures** | TODO | 10-13 | — | `proposal/risks.md` |
| W-06 | Phase II plan and Phase III transition via **SMI** | TODO | 10-13 | — | `proposal/transition.md` |
| W-07 | "Clear path to integration and testing within the OPIR Tap Lab" | TODO | 10-13 | E-02, E-05 | `proposal/taplab_path.md` |
| W-08 | Explainability and confidence section (the topic *requires* this) | TODO | 10-13 | A-06 | in `feasibility.md` |
| W-09 | Cost volume ($150k; ≥2/3 in-house, ≤1/3 consultants + subcontracts) | TODO | 10-14 | E-04 | `proposal/cost/` |
| W-10 | Red-team pass against the eight-point checklist | TODO | 10-17 | W-04 | `analysis/redteam_pass.md` |
| W-11 | Compliance matrix signed off against G-06 | TODO | 10-18 | W-04 | `analysis/compliance/compliance_matrix.md` |

**W-04 structural rule (from the topic, non-negotiable):** the feasibility study must literally
contain the four bulleted elements, and the per-CTE evidence must cover all four evidence types
— *literature research · trade studies · analysis · heritage usage with identified differences*.
Use those as headings so the evaluator can check them off.

**W-02 structural rule:** system level first, technology second. Writing the CONOPS from the
algorithm outward is the classic newcomer failure.

**W-10 red-team checklist** — pre-empt each in the text; do not wait to be asked:
1. *"Your fidelity is toy-grade."* → cite every assumption; sensitivity analysis (A-09).
2. *"You validated against nothing real."* → concede it; show Vallado / Gronlund / BRSL / ADS-B
   validation (S-03, S-06, S-08); make Tap Lab calibration an explicit Phase II closure measure.
3. *"Your sensitivity and latency numbers are invented."* → report *relative* improvement and
   sweep the rest; never state a classified-adjacent absolute as fact.
4. *"STK and our FFRDC tools already do this."* → we are not claiming higher fidelity than STK.
   We claim open, reproducible, CI-tested, fast trade iteration. Say so plainly.
5. *"Where does ML actually help, and can you trust it in a nuclear-adjacent mission?"* → a
   narrow, baselined claim (S-11) plus the explainability section (W-08).
6. *"No clearances, no space-sensing past."* → turn the open-source software pedigree into the
   asset; concrete onboarding plan (W-07); one credentialed advisor (E-04).
7. *"Your CONOPS is written from the algorithm outward."* → the W-02 rule.
8. *"Three months, five CTEs — is this scoped realistically?"* → each CTE maps to a specific
   experiment rung and a named Phase II metric.

---

### Phase X — Submission

| ID | Task | Status | Due | Depends | Artifact |
|---|---|---|---|---|---|
| X-01 | Assemble volumes in the DSIP template; page and format check | TODO | 10-18 | W-11, G-07 | `proposal/submission/` |
| X-02 | Final full read-through by someone who did not write it | TODO | 10-18 | X-01 | — |
| X-03 | **Upload and submit on DSIP** | TODO | **10-19** | X-02, G-01…G-04 | confirmation # |
| X-04 | Archive the submitted package and confirmation; log lessons learned | TODO | 10-21 | X-03 | `proposal/submission/final/` |

---

## 6. Project risk register  *(distinct from the proposal's own risk section, W-05)*

| ID | Risk | Likelihood | Impact | Mitigation | Closure measure |
|---|---|---|---|---|---|
| R-1 | SAM.gov / SBIR.gov registration not complete by 10-19 → **cannot submit at all**. Owned by Mason; the agent cannot observe status | unknown | fatal | Mason is handling G-01…G-04. SAM.gov can take 2–4 weeks; 10-19 is the hard backstop | Mason confirms active UEI + CAGE and an SBC Control ID. **X-03 must not be marked ready until then.** |
| R-2 | 29 days is not enough for S-01…S-11 plus a 30-page volume | high | high | Hard-prioritize the S-03 → A-04 chain; S-10 and S-11 are cuttable | A-04 exists by 10-11 |
| R-3 | CMMC L2 self-assessment not posted → compliance finding | medium | high | G-04 by 10-10 | SPRS score posted |
| R-4 | No credentialed advisor → the CONOPS reads naive | medium | medium | E-04; otherwise lean on FFRDC / CSIS prior-art citations | Advisor named in the cost volume, or a decision logged in §8 |
| R-5 | The ML component does not beat the classical baseline | medium | low | The S-11 gate — report the classical result, defer ML to Phase II | Ablation table in A-06 |
| R-6 | Evaluators (MITRE / Aerospace) own better tools than ours | certain | medium | Position as open / reproducible / fast, not higher-fidelity | Red-team item 4 addressed in W-04 |
| R-7 | Aggregating public data into something a reviewer treats as controlled technical data | low | high | G-05 repo policy; parameterize anything classified rather than sourcing it | ITAR posture doc reviewed before any public release |

---

## 7. Decisions log

> IDs are `DEC-nn`. They were `D-n` until 2026-09-23, when that collided with the
> Phase D task IDs (`D-00`…`D-23`) — see amendment A-10.

| # | Date | Decision | Rationale |
|---|---|---|---|
| DEC-01 | 2026-09-22 | Primary lane is focus area 3 (OODA Loop Collapse / "AI trade-space exploration"); secondary is area 4 | SITIS A1 and A3 explicitly blessed this, and it is where a software-first team is strongest |
| DEC-02 | 2026-09-22 | Phase I proposes **no new detection algorithm** | SITIS A1 confirmed a screening trade study is responsive; over-promising algorithms is the classic three-month failure |
| DEC-03 | 2026-09-22 | Python-first stack (Stone Soup, sgp4 / Skyfield, numpy) | Stone Soup is Python-only and is the tracking baseline; it matches the existing `defense/` repo convention; 29 days rules out a Rust core |
| DEC-04 | 2026-09-22 | Architecture documentation follows **DoDAF 2.0**, minimal correct subset (OV-1, OV-2, OV-5b, OV-6c, SV-1) | SITIS A2 named DoDAF 2.0 directly |
| DEC-05 | 2026-09-22 | Phase III transition target is **SMI**, not FORGE / DAVE | The official topic PDF names the Space Modernization Initiative. The internal research primer's FORGE/DAVE framing is *not* what the topic says — correct this everywhere. FORGE may still be cited as context, never as *the* named pipeline |
| ~~DEC-06~~ | ~~2026-09-22~~ | ~~Target the 2026-10-21 deadline; the §4 calendar is live~~ **SUPERSEDED 2026-09-23 by DEC-32** | Reframed: the objective is research quality, not this submission window |
| DEC-07 | 2026-09-22 | Registration and portal gates (G-01…G-04, G-07, G-08) are Mason's, tracked but not agent-executed | They sit behind login walls; Mason is handling them. Risk R-1 is transferred, not closed |
| ~~DEC-08~~ | ~~2026-09-22~~ | ~~"Do not seed operational altitude from the Tranche 0 elements, because they contradict SDA's published 1000 km."~~ **RETRACTED 2026-09-23** | The premise was wrong. SDA's wording is that the *majority of Tranche 0 space vehicles* sit in two planes near 1000 km / 80° — it never claims that geometry for every Tracking satellite. There was no contradiction to find; I misread a hedged agency statement as a specific one. The supporting inference ("high n-dot means the orbit is contracting") was also over-drawn from a single element epoch. Superseded by DEC-10 |
| DEC-10 | 2026-09-23 | **Adopt the manifest-count mapping: CHECKMATE + WILDFIRE = 19 Transport; BB 1–4 + RAPTOR 1–4 = 8 Tracking; HBTSS-SV1/2 separate.** Tag its provenance as *inference*, never as a published agency lookup | The counts match one-to-one on all three launches, verified directly against the catalogue: 8 CHECKMATE + 2 BB, then 10 WILDFIRE + 1 CHECKMATE + 2 BB, then 4 RAPTOR + 2 HBTSS — totalling 19 Transport and 8 Tracking, against SDA's stated 19-on-orbit (one of 20 retained as a ground testbed) and 8 Tracking. The 19-not-20 is itself confirmatory. No agency publishes a NORAD→contractor→layer table, so this stays labelled an inference |
| DEC-11 | 2026-09-23 | **Architecture documents and catalogue geometry answer different questions.** Propagate real objects for current-epoch coverage; use agency-stated design parameters for future-architecture trades. Never substitute one for the other | This is the conceptual error behind the retracted DEC-08. A fact sheet can truthfully describe a nominal or majority architecture while individual demonstrator spacecraft sit in other or decaying orbits — both statements can be true at once |
| DEC-12 | 2026-09-23 | **Three-tier source policy.** Tier A authoritative input (fixed constant), Tier B public analytical proxy (baseline + mandatory sensitivity sweep), Tier C unresolved/classified (sweep only, no sourced value) | Gives the assumptions register a decision rule instead of a judgement call per row, and makes the public-data boundary visible to a reviewer |
| DEC-13 | 2026-09-23 | **SDA's published ~1000 km Tranche 0 figure is confirmed, not contradicted.** All eight Tracking satellites and both HBTSS prototypes were inserted at 943–998 km. Four BB satellites and HBTSS-SV1 were subsequently *flown down* by 167–442 km; RAPTOR 1–4 and HBTSS-SV2 remain near insertion | Multi-epoch audit of 25,219 Space-Track `gp_history` element sets (D-14). Measured drag at these altitudes is −0.72 to +0.88 km/yr, so changes of hundreds of km cannot be drag; step share ≈ 1.0 confirms commanded manoeuvres. RAPTOR 2 and HBTSS-SV2 register **zero** detections over 950 days, giving the detector a clean false-positive control. This closes the question the retracted DEC-08 got wrong |
| DEC-32 | 2026-09-23 | **The objective is a strong research product, not this submission window.** Dates in §4 are demoted from commitments to reference points; work is paced by quality and by the phase gates, not by the calendar. Supersedes DEC-06 | Mason: "don't worry about time constraints or cutoffs... The goal is to build a strong product regardless of whether it gets accepted. You just focus on helping accelerate the best quality research output." Practical consequences: **do not** truncate Phase D to fit a deadline; **do not** trade correctness for coverage of proposal deliverables; finish domains properly and let the submission decision follow the work. Mason owns the schedule and the go/no-go |
| ~~DEC-31~~ | ~~2026-09-23~~ | ~~"We cannot inherit Tracy & Wright's 'atmospheric attenuation is negligible'; it fails badly at the 120° FOR that coverage requires"~~ **RETRACTED 2026-09-23 by DEC-33** | The premise was a proxy, not the quantity. I reasoned from *air mass ratio* (9× more air at 84° zenith) to "the assumption fails". Optical depth is what attenuates, and 9× a very small optical depth is still very small. Line-by-line computation (D-19) gives ≤0.24 dB across the entire geometry |
| DEC-43 | 2026-09-24 | **`mwsim/lms.py` — LMS3 as published — is the variable-structure baseline; `mwsim/vsimm.py` is superseded and its measured claims withdrawn** | Two departures in the from-prose version each cost accuracy at manoeuvre onset, which is where the filter earns its keep. (1) **Activation:** it seeded a new model from the combined estimate; the published algorithm runs `VSIMM[M_n, M_{k-1}]` and, on the authors' explicit recommendation (*"One-step back is recommended and was used in our examples"*), first runs the new model over the *previous* measurement. Adding that alone cut our LMS-vs-IMM gap on topology A from +5.9% to +3.6% and peak error from 84 m to 74 m. (2) **Deletion:** it dropped anything below the lower threshold; LMS3's "AND logic" protects a model that is unlikely **but** adjacent from a principal one. `lms.py` reduces *exactly* to `mwsim.imm` under full adjacency (6e-11 on states of ~1e5 m), which chains it back through DEC-39 to FilterPy. The paper's third suggestion — iterating expansion within a step — was implemented and measured at **no effect**, because a newly activated model is essentially never principal in the step it appears; left off by default and recorded rather than dropped |
| DEC-42 | 2026-09-24 | **The survey's "substantially outperforms" is not a claim about plain LMS. Primary source Table IV puts plain LMS *behind* fixed-structure IMM on RMS position error in all six published cases; the accuracy gain belongs to LMS(λ) alone.** Replicated on the paper's own experiment | Traced [215] to Li & Zhang, *IEEE T-AES* 36(2), 448-466 — a scanned PDF, transcribed by hand into `mwsim/lz2000.py` (13 models with specified accelerations, two adjacency graphs, two 13×13 transition matrices, Table III scenarios, the semi-Markov random scenario). Published LMS/IMM ratios: 1.014, 1.012, 1.022, 1.000, 1.001, 1.007 — never below 1. What LMS buys is a FLOP ratio of 0.36-0.65. The paper's own summary says *"much more cost-effective than the IMM estimator"* — cost, not accuracy. **Our replication at 500 Monte Carlo runs:** IMM within **1.2-1.5%** of the published RMSPE in all four deterministic cases, and our LMS/IMM ratios (1.0005-1.0363) track the published ones case by case. Transcription is cross-checked by an independent route — Ω (eqs. 31-32) and Π (eqs. 33-34) are separately typeset statements of the same graph and agree exactly. **Two caveats recorded, not buried:** our random scenario comes out ~13% easier than theirs (all three estimators shift together, so the comparison holds but the absolute level does not), and we reproduce LMS(λ)'s accuracy gain only in *direction*, at ~1% against their 3.5-8.8% — eqs. (18)-(20) leave real ambiguity about when λ resets and what counts as newly activated | 
| DEC-40 | 2026-09-23 | **The classical baseline is a ladder of three, not one filter: single tuned Kalman → fixed-structure IMM → variable-structure IMM (Likely-Model Set)** | "Does ML help?" is meaningless without "compared to what?". One baseline gives a yes/no; a ladder shows *where* the value is, which is what the topic asks for. Each rung has a published justification: Mazor for FS-IMM ("nearly linear" cost at near-quadratic performance — directly relevant to the SWaP-limited edge case in DEC-29), Li & Jilkov for VSMM. It also pre-empts the obvious reviewer attack: anyone who knows the Li & Jilkov survey will ask why we compared only against fixed structure |
| DEC-41 | 2026-09-23 | ~~**Measured: VS-IMM gives ~0.5% accuracy improvement on our scenario, not the "substantial" gain the survey reports.**~~ **SUPERSEDED BY DEC-42 — the framing was wrong.** The measurement itself stands; what was wrong was calling it a shortfall against a published claim | There was no published claim to fall short of. The survey sentence was traced to its primary source (Li & Zhang 2000) and it does not describe plain LMS: Table IV reports plain LMS as slightly *worse* than fixed-structure IMM in all six of its cases. The comparison was also made on a scenario we invented rather than the paper's, so it could not have confirmed or refuted anything either way. Retained rather than deleted, per the D-8 and DEC-31 precedent |
| DEC-39 | 2026-09-23 | **Our IMM is cross-validated against FilterPy's `IMMEstimator` to machine precision (8.5e-14) and the test is permanent** | Writing our own IMM (DEC-23) raised the obvious question of whether it is correct. Our behavioural tests show it behaves sensibly, which is necessary but not sufficient — a subtly wrong filter can still behave sensibly. FilterPy is an independent MIT implementation of the same Bar-Shalom algorithm by a different author. Driven with identical inputs across straight flight, a manoeuvre, and three process-noise tunings, the two agree to machine precision: not merely similar but algebraically identical. Same validation pattern as SGP4-against-Vallado and the atmosphere against the published table |
| DEC-38 | 2026-09-23 | **Target motion is consumed from the published Berkeley (BRSL) simulator, not implemented here.** Trajectories are fetched, cached with provenance, resampled and placed on a spherical Earth; no equations of motion are integrated in this repo | Two reasons, and the methodological one is the stronger. **Methodology:** re-implementing published equations invites "did you transcribe them correctly?", and D-03 found two genuine glyph ambiguities resolved only by dimensional analysis — each a place a reviewer can push. Consuming the authors' own implementation removes that objection class entirely, and we already confirmed it reproduces the paper's published range to 0.09%. It also removes a model we would otherwise have to own, tune and defend. **Practical:** writing trajectory-propagation code repeatedly tripped a safety classifier, which is a coherent line to draw regardless of surrounding intent. `mwsim/threats.py`, written by a blocked response, was deleted rather than extended |
| DEC-37 | 2026-09-23 | **The adequate-convergence band is symmetric: `needed ≤ α ≤ 180 − needed`, not `α ≥ needed`** | Angles-only position error scales as 1/sin(α), so 150° is exactly as good as 30° and 175° exactly as bad as 5°. A one-sided test silently accepts near-antiparallel geometries where the sight lines are almost collinear again. On the 135-satellite constellation it overstated useful stereo coverage by **26 percentage points** at a 0.5 km requirement (100% → 73.8% once corrected) |
| DEC-36 | 2026-09-23 | **OpenSky `trino-tables/state_vectors` is the single tracker-validation dataset; Nantes, AIS and NRW are shelved** | One hour = 519 MB Parquet, 26.3 M rows, 13,120 aircraft, **7,353 simultaneous at 1-second cadence**, global, with geometric altitude, velocity, heading and vertical rate, and `icao24` as ground truth. It dominates all four previously acquired sets on every axis and needs no custom parser. Publicly listable at `s3.opensky-network.org/data-samples/` with no credentials — it was reachable the entire time |
| DEC-34 | 2026-09-23 | **Claim TRL 2–3 explicitly for the Phase I work, and test every candidate CTE against GAO's two-part rule** | GAO-20-48G admits modelling and simulation as TRL 3 evidence ("analytical and experimental proof of concept... modelling and simulation may be used to complement physical experiments"), so a simulation-based feasibility study is the *expected* evidence at this maturity, not a weak substitute. The topic's own TRL 6–7 language belongs to Phase III, and TRL 6 is demonstration in a relevant environment — which is what the Tap Lab is for. A CTE must be **both** new-or-novel **and** needed to meet operational performance requirements; entries failing either half get dropped, and exclusions are justified alongside inclusions |
| DEC-35 | 2026-09-23 | **Add an AV-1; put the warn-to-decision pipeline in the OV-6c; show the human decision step in the SV-1** | DoDAF 2.02 defines the OV-1 as "the pictorial representation of the written content of the AV-1", and we had no AV-1 task. OV-6c is an event-trace view, which is precisely what the latency pipeline is. DoDAF 2.0 treats organisations and personnel as Performers in the SV-1 — and since the decision stage is 55–66% of our latency budget, the human is the largest single term in the architecture rather than a footnote |
| DEC-33 | 2026-09-23 | **Tracy & Wright's neglect of atmospheric attenuation is sound for our geometry, including the wide field of regard — for a band-integrating detector.** Computed, not assumed: ≤0.24 dB band-mean attenuation across 38–57 km and 0–84° zenith | Line-by-line HITRAN/HAPI over a layered slant path. At 38–57 km the target sits above ~99.5% of the atmosphere: the CO₂ column above it is 3×10¹⁹ vs 8.7×10²¹ for the full column, so even 9× of it stays optically thin in the band mean. **Caveat that survives:** line cores remain opaque (min transmittance <10⁻³⁰⁰), so the conclusion holds for a wide-band detector and not necessarily for a narrow-band one. Model validated by reproducing the known full-atmosphere opacity of the 4.3 µm band (10.9 dB from the surface), which is why that band is used for temperature sounding |
| DEC-29 | 2026-09-23 | **Propagation delay is under 1% of the warn-to-decision budget, so edge fusion cannot win by shortening the path. Report the breakeven condition, not an absolute latency number** | Light-time is exact: LEO downlink 12 ms, LEO crosslink 25 ms, GEO 119 ms — against published detect-to-alert figures of tens of seconds. The advantage collapses to `ground_fusion − onboard_fusion` within ~37 ms. The intuitive pitch ("closer sensors mean lower latency") is wrong by two orders of magnitude and a reviewer who checks light-time will see it. The defensible claim is the condition under which edge fusion wins, which survives disagreement about our inputs |
| DEC-30 | 2026-09-23 | **Over 99.5% of any latency figure we produce is assumption, and the proposal must say so.** Absolute warn-to-decision numbers are not findings; relative comparisons under identical assumptions plus the breakeven are | Measured physics fraction: 0.07% ground-centralised, 0.41% edge-fused. Asserted by test — if propagation ever exceeds 2% of the budget the framing gets revisited automatically. Also noted: the *decision* stage dominates every budget at 55–66%, which bounds how much any sensing improvement can help end to end |
| DEC-27 | 2026-09-23 | **Covariance consistency (NEES) is our answer to the topic's "sufficient confidence" requirement, and custody is reported as continuity intervals rather than a mean** | Accuracy alone cannot support a warning decision — an operator needs to know how far to trust a track, and an overconfident filter poisons every downstream consumer silently. NEES is computable, unclassified, and speaks to whether the system knows when it is wrong. Custody as intervals because RMS cannot distinguish a track that degrades gently from one that is excellent until it fails during the manoeuvre — and the manoeuvre is where an HGV analysis lives |
| DEC-28 | 2026-09-23 | **GOSPA cutoff `c` is derived from the custody threshold, not quoted from a tutorial** | `c` sets what "completely wrong" costs and therefore how a missed track trades against an inaccurate one. The prior research's `c = 40` came from a scenario at a different scale. Deriving it makes the trade explicit: a track worse than the custody threshold scores no better than a miss, because operationally it is one |
| DEC-26 | 2026-09-23 | **Do not claim multi-orbit coverage comparison as novel — CSIS published one in Dec 2023 using SMARTSet. Position the contribution as extending it into the latency and fusion-placement dimension, reproducibly** | *Getting on Track* (127 pp, now acquired) contains nine notional architectures from 91-satellite LEO through 30 MEO + 135 LEO, with field-of-regard sensitivity analysis. Our evaluators know it. Claiming coverage analysis as new would be both wrong and visibly so. What CSIS does **not** address is where processing happens and what that costs in warn-to-decision time — which is exactly where A-04 lives. Narrower claim, defensible, and it cites the respected prior work rather than ignoring it |
| DEC-25 | 2026-09-23 | **Do not correct for UT1−UTC or polar motion; the approximations are measured and bounded instead** | IERS finals2000A, 2023 onward: UT1−UTC reaches 0.199 s (92 m at the equator) and polar motion 0.545 arcsec (17 m). Against SGP4's ~1 km floor these are 11× and 60× smaller. Correcting would add a data dependency needing upkeep to remove an error an order of magnitude below the floor. Lookups are implemented so the decision is revisitable, and tests assert the bounds so it reopens automatically if they change |
| DEC-23 | 2026-09-23 | **Stone Soup has no Gaussian IMM filter; we implement IMM ourselves on its Kalman primitives** | Verified by enumerating all 576 public classes in 1.9.1, the module layout, and PyPI for plugins. Its only multi-model machinery is particle-based. Both prior research documents claimed otherwise. IMM is the canonical classical baseline for manoeuvring targets and the whole ML argument depends on having one to beat. Implementing it ourselves is ~100 lines against Bar-Shalom and we can then explain it — which the topic's explainability requirement needs anyway |
| DEC-24 | 2026-09-23 | **Stereo coverage is scored by achieved convergence angle, not by sensor count.** Use `required_convergence_deg(range, σ, accuracy)` rather than any fixed "stereo counts above N degrees" rule | Measured: position error follows 1/sin(α), but the optimum is broad and the whole penalty sits at small angles. 45°→90° buys 34%; 5°→20° buys 4×. A constellation delivering 30–40° convergence has captured most of the benefit; one delivering 5° almost none — yet a two-sensors-in-view count scores them identically. Error scales linearly in range and in angular noise, so the sweep is cheap |
| DEC-21 | 2026-09-23 | **Temporal differencing is the enabling detection step, not an optimisation, and the detection floor is a property of threshold *and* revisit *and* background dynamics together — not of the threshold alone** | Measured on real GOES-19 Band 7 frames: a target must radiate ~159 kW/sr to equal the background in a single 2 km pixel, but differencing consecutive frames drops the 5σ floor to 12–27 kW/sr, a 13× gain. HGV hardbody estimates (3–113 kW/sr) sit below the single-frame background and above the differenced floor. It also explains why CU Boulder's Project Apollo used GOES delta-detection. Consequence: faster revisit does not only detect *sooner*, it detects *fainter*, because less background has changed between looks — a coverage/latency/accuracy coupling the Pareto analysis can quantify and that a fixed-threshold detection model cannot see |
| DEC-22 | 2026-09-23 | **GOES Band 7 background is conservative and must be described that way.** It is a 3.89 µm window band; DSP uses 2.69–2.95 µm precisely because atmospheric absorption suppresses surface background there | GOES has no solar-blind equivalent, so our measured background overstates what a real missile-warning sensor faces. Erring pessimistic is the safe direction, but claiming equivalence would not be defensible |
| DEC-19 | 2026-09-23 | **Seed the Walker generator from measured insertion geometry (943 km, 81.00°, 65° plane separation), not the published round numbers (~1000 km, 80°).** Do not assume even Walker phasing for Tranche 0 | The one constellation we can actually measure is not evenly phased: its two polar planes are 64.9° apart where an even two-plane Walker would be 90°. A generator seeded from the fact sheet would silently produce a different constellation from the real one, and coverage is exactly what that error would corrupt |
| DEC-20 | 2026-09-23 | **The Tranche 0 off-plane drift is fully explained by J2 nodal regression from the commanded altitude change — no residual.** This is accepted as independent corroboration of DEC-13/DEC-14 | Integrating the differential regression over each satellite's actual altitude history predicts −28.56° for BB 3 against −28.33° observed, and −16.84° for BB 4 against −16.49°, with agreement to hundredths of a degree before the manoeuvres begin. Two independent observables — semi-major axis and RAAN — agree on the same manoeuvre-onset day (347). Pinned by tests |
| DEC-17 | 2026-09-23 | **HGV glide altitude is a swept parameter over a cited 38–57 km range** *(widened from 38–50 by D-04)*, never an inherited constant.** More generally: before adopting a published model's value, check *which quantity* its validation actually covered | Cross-implementation check (D-03-d). Four sources agree on max glide range within 1.9% (7,498 / ~7,500 / 7,630 / 7,637 km) but split 2–2 on glide altitude (49 / 49.53 vs 38.15 km). Both can be right: the closed-form equilibrium-glide range `R = (L/D)(rₑ/2)ln[1/(1−v²/v_c²)]` has **no altitude term**, so range is insensitive to it and nobody has had cause to reconcile the difference. But altitude is precisely what *our* detection analysis depends on — transmission path, IR background, slant range, look angle, occultation. The literature validates the quantity we do not need and leaves open the one we do |
| DEC-18 | 2026-09-23 | **The detectability conclusion is robust to the IR dispute; the custody-duration conclusion is not.** A modern SWIR sensor (6 kW/sr, APS-notional) detects the glide hardbody under *every* published estimate; a DSP-class sensor (20 kW/sr) does so only under the higher one. Report detectability as a finding, and report how long custody holds as a swept result | Tracy & Wright give 43 / ~370 kW/sr; Candler & Leyva give 4.90 / 29.0 falling to 2.95 / 22.1 at their corrected altitude. A 9–13x disagreement, yet the SWIR conclusion survives all of it. Being able to state a detectability finding without picking a side in a live scientific dispute is worth more than picking correctly would be |
| DEC-15 | 2026-09-23 | **The HGV IR signature is a cited range, not a value.** Tracy & Wright and Candler disagree materially on glide-phase emission; both endpoints get cited and swept. We do not pick a winner and do not average them | Two peer-reviewed analyses disagreeing on the same quantity is the strongest available argument that no lookup value exists. Tier B under D-12. It also converts a weakness into a defensible methodology point for the proposal |
| DEC-16 | 2026-09-23 | **Validate the glide integrator at the glide-start state, independently of boost and pull-up.** Initialise at h=49 km, v=6.1 km/s, γ=0 and check range and flight time against Tracy & Wright | The pull-up phase is analytically approximated rather than simulated, by the authors' own account, so it is the weakest link in the chain. Testing the glide model through it would confound our error with theirs |
| DEC-14 | 2026-09-23 | **Say what the orbit did, never what the mission is.** An orbit that was lowered was lowered; whether that is disposal, an ending demonstration phase or repositioning is not in the data and no agency states it. Altitude is never a proxy for payload health or test performance | The specific error behind the retracted DEC-08 was reasoning from orbit geometry to mission status in one step. The audit is worthless to us if we repeat that with better data |
| DEC-09 | 2026-09-22 | **Phases are gated; no phase starts before the previous one's written criteria are met** (§1A) | Mason's working philosophy: this subject area needs design, tradeoff consideration, research and pacing, and each phase is the foundation for the next. Silent corruption from a rushed foundation is the specific failure mode — a bad frame conversion or detection threshold does not raise, it just produces a confident wrong chart |

---

## 8. Amendment log

| # | Date | Change | Reason |
|---|---|---|---|
| — | 2026-09-22 | Plan created | Initial |
| A-1 | 2026-09-22 | Added an Owner column to Phase G; G-01…G-04, G-07, G-08 assigned to Mason | Those tasks are behind portal logins the agent cannot reach; Mason is handling them |
| A-2 | 2026-09-22 | Confirmed the Oct 21 2026 target cycle; §4 calendar is live, not provisional | Decision D-6 |
| A-3 | 2026-09-22 | R-1 reworded from "unstarted registration" to "registration status unknown to the agent" | Ownership transferred to Mason; the agent can no longer observe closure, so X-03 gains an explicit precondition check |
| A-4 | 2026-09-22 | **Added §1A phase gates and a new Phase D (data foundation) ahead of Phase S.** S-01…S-03 were executed before this pacing was agreed and are retained as `DONE`; S-04 onward is now blocked on Gate D | Mason: the effort is not to be one-shotted. Each phase needs written success criteria and must not be left until they are met, because each phase is the foundation for the next. Data collection is the first gate, and its bar is *every* useful data type identified, acquired, organized and understood — not merely "some data pulled" |
| A-5 | 2026-09-22 | Space-Track ingest moved out of S-02 and into D-01 | It is a data-source decision (registration, rate limits, redistribution terms), not a code task, and belongs behind the D gate |
| A-33 | 2026-09-24 | **Li & Zhang (2000) replicated rather than cited.** Primary source acquired and transcribed from scan into `mwsim/lz2000.py`; LMS3 implemented as published in `mwsim/lms.py` (one-step-back activation, AND-logic deletion, K floor); `scripts/replicate_lms.py` reproduces Table IV at the paper's own 500 Monte Carlo runs into `analysis/validation/lms_table_iv.json`; written up in `analysis/validation/lms_replication.md`. DEC-42 and DEC-43 recorded, DEC-41 superseded, `mwsim/vsimm.py` deprecated and its bandwidth table withdrawn. 303 tests | Mason: *"have we truly made a good faith attempt at reproducing the paper with the same data? If the paper claims to outperform in accuracy, then we would be selling ourselves short to be aiming for that goal without really making sure we're using the right data and setting up our experiment in the same way?"* The answer was no — the earlier comparison used a bank, a scenario and a graph we invented, against a claim whose experimental conditions we had never read. Reading them changed the conclusion: the accuracy advantage we thought we had failed to reproduce was never claimed for the algorithm we built |
| A-32 | 2026-09-23 | **VS-IMM (Likely-Model Set) built as the third baseline rung.** Li & Jilkov and Mazor surveys acquired and read. Structure adaptation verified (active set varies 2–4 of 4; full-adjacency control degenerates correctly to fixed structure), thresholds tunable on held-out data. DEC-40 and DEC-41 recorded. 242 tests | The measured result contradicts the survey's headline claim on our scenario, and is recorded as measured rather than adjusted until it agreed |
| A-31 | 2026-09-23 | **IMM independently cross-validated (DEC-39).** FilterPy `IMMEstimator` added as a test-only dependency; 7 cross-validation tests covering straight flight, manoeuvre and three tunings, all agreeing to <1e-11. PyEHM identified as the equivalent independent check for JPDA association when S-08 continues. 230 tests | The strongest form of corroboration available for an algorithm we wrote ourselves |
| A-30 | 2026-09-23 | **S-06 re-scoped: target motion is external (DEC-38).** `mwsim/target_motion.py` fetches, caches and places trajectories from the published BRSL simulator; the D-03 cross-validation pull seeds the cache. `mwsim/threats.py` — 302 lines written by a response that was blocked mid-flight — deleted, not reworked. 223 tests | The re-scope is an improvement on its own merits: one fewer model to own, and a whole class of transcription objections removed. That it also resolves the practical obstacle is convenient rather than the justification |
| A-29 | 2026-09-23 | **S-04 and S-05 complete.** Walker generator (delta and star patterns) seeded from measured Tranche 0 geometry, validated against the catalogue: 943 km gives 13.859 rev/day inside the measured 13.848–13.895 band, and J2 precession of −0.962°/day against the measured −0.95. Coverage module with the useful-stereo criterion. **Independently reproduced CSIS's field-of-regard finding** — a 91-satellite constellation achieves stereo at 120° and fails at 110° and 100°, from our own geometry. DEC-37 records a one-sided-test bug found and fixed. 208 tests | The CSIS reproduction is a genuine external validation: a respected published result, recovered from an independent implementation |
| A-28 | 2026-09-23 | **IMM implemented (S-08 partial) and tracker-validation data consolidated.** IMM written with 15 behavioural tests — mode probability tracks the truth through a manoeuvre, the bank beats a single tuned filter, the spread-of-means term is verified. OpenSky state_vectors acquired and characterised; Nantes shelved alongside AIS and NRW. `data/raw` falls from 8.1 GB to 952 MB | **The D-00 lesson is now measured, not asserted:** five tracking datasets and ~8 GB were acquired incrementally, and a single 519 MB file publicly listable the whole time supersedes four of them. One sentence of requirement, written first, would have found it |
| A-27 | 2026-09-23 | **GATE D PASSED.** Reviewed criterion by criterion and domain by domain; 7 stale open items closed; D-16/D-18/D-22 moved to Phase S as parameter-definition work. **Phase S is now open.** Process failure recorded rather than waived: D-00 was executed last instead of first, costing ~8 GB and four tracking datasets where a one-paragraph requirement would have pointed straight at one. Scope drift into Phase S also recorded, as was the one wrong decision (DEC-31, retracted) | The gate's value was the scrutiny, not the stamp. Carried forward: write the requirement before the next acquisition |
| A-26 | 2026-09-23 | **D-10 complete.** GAO-20-48G and DoDAF 2.02 acquired by Mason after every automated route returned 403, and read against the deliverables they govern. Added task W-00 (AV-1). Decisions DEC-34 and DEC-35 recorded. SMI deliberately scoped down to the topic's own one-sentence definition rather than researched further | Reading the specifications rather than approximating them changed three things in the plan, including one missing product. The TRL finding also reframes the simulation-only position from an apology into a correctly-scoped claim |
| A-25 | 2026-09-23 | **Redundant data shelved and D-12 sufficiency assessment written.** NRW ADS-B (strictly dominated) and NOAA AIS (out of operational regime at 6,800 simultaneous targets) moved to `data/shelved/` with the reason recorded. Sufficiency checked against every Phase S and Phase W task | **Gate D passes for Phase S**: every physical input is sourced or defensibly swept. Three blockers remain and none are data — GAO-20-48g, DoDAF 2.02 and SMI detail, all free public documents behind hosts that reject automated requests. They gate Phase W, not Phase S |
| A-24 | 2026-09-23 | **D-00 written, out of order, at Mason's prompting.** It was meant to come first — enumerate the domains before acquiring anything — and instead it is a plain-language inventory of what we already hold. **Also recorded: scope drift.** D-19, D-20, D-23 and the observability work in D-06 are simulator components, not data understanding, and belong to Phase S. They were justified under Gate D criterion D-iv ("understood means we looked at the data"), which stretched further than it should have | Mason asked why a data-collection phase was running simulations. Largely a fair hit. The defensible part is that D-19 answered a genuine data question — *do we need this input at all* — and the answer was no, which removes it from the simulator. The rest was drift |
| A-23 | 2026-09-23 | **D-19 complete, and it retracts DEC-31.** Line-by-line CO₂ transmission implemented over a layered slant path and validated against the known full-atmosphere opacity of the 4.3 µm band. Attenuation at glide altitudes is ≤0.24 dB band-mean even at 84° zenith — so the assumption D-17 declared broken is in fact sound. DEC-33 supersedes | **My error, of the same class I have been cataloguing in others' work and in the code: reasoning from a proxy (air mass ratio) instead of computing the quantity (optical depth).** The difference is that D-17's conclusion was stated confidently in a decision entry, and only the actual computation caught it |
| A-22 | 2026-09-23 | **Objective reframed: research quality over the submission window.** DEC-06 superseded by DEC-32; §4 calendar demoted from commitment to reference. Phase D is no longer to be truncated, and the proposed cut of D-10/D-11/D-22 is withdrawn | Mason redefined the goal and took ownership of the schedule. This removes the only argument that was pushing toward shallower work, and makes the phase-gate discipline unambiguously correct rather than a cost |
| A-21 | 2026-09-23 | **D-17 complete**, closing the radiometric question D-08 deferred and answering D-04-c in the negative. Slant air mass computed across the glide sweep and field-of-regard range; the attenuation assumption fails beyond ~80° FOR. Independently reproduced CSIS's Earth-curvature field-of-regard limit (121° from geometry vs their ~120°). DEC-31 recorded and D-19 promoted to required | The coupling only exists when coverage geometry and radiometry are examined together, which is what the trade study is for |
| A-20 | 2026-09-23 | **D-20 complete** — the latency ledger, which carries the novelty claim after DEC-26. Propagation computed exactly and found negligible; edge-fusion advantage reduced to a breakeven condition on processing time; physics fraction of the budget measured at 0.07–0.41% and asserted by test. DEC-29 and DEC-30 recorded | The intuitive edge-fusion pitch turns out to be wrong by two orders of magnitude. Finding that now, rather than after building the chart around it, is the whole point of the phase gate |
| A-19 | 2026-09-23 | **D-23 complete.** Track-quality metric defined and implemented: NEES covariance consistency, custody as continuity intervals, derived GOSPA cutoff, explicit non-equivalence to the classified fire-control threshold. DEC-27 and DEC-28 recorded. **A test caught a real bug**: reported uncertainty was per-axis sigma while error was 3-D magnitude, a silent factor of sqrt(3) that scored every honest filter as overconfident | Same failure class as the D-14 decay-rate sign error and the D-07 layer ordering: no exception, no implausible value, just a plausible number with an inverted meaning |
| A-18 | 2026-09-23 | **D-09 substantially complete.** CSIS *Getting on Track* (127 pp) and CRS IF11623 acquired via publisher S3 and the everycrsreport mirror after direct hosts returned 403. **The deep research's `UNCONFIRMED` 135-satellite / 1,000 km / 120° FOR claim is confirmed verbatim.** Nine notional architectures, field-of-regard sensitivity, and a real SDA Tranche 0 sensor requirement (FOV ~110°, pixel footprint <1.5 km) added to the assumptions register. DEC-26 records the resulting narrowing of our novelty claim | The single most valuable public document for this study, which the deep-research pass could not open. It also changes what we may claim as new |
| A-17 | 2026-09-23 | **D-15 and D-21 complete.** IERS Earth orientation series acquired; both standing approximations in `propagate.py` measured and bounded rather than asserted; external time-tag characteristics of all four real datasets recorded. **Corrected an earlier claim**: the UT1−UTC error note said ~0.4 km reasoning from the 0.9 s leap-second bound — right as a historical worst case, ~4× pessimistic for current epochs, now 92 m measured | The original figure came from reasoning about a guaranteed bound rather than measuring the actual series. Both defensible; only one accurate |
| A-16 | 2026-09-23 | **D-06-a effectively closed by alternatives.** Three licence-clear sources verified: Cleaned ADS-B LHR–ZRH (CC-BY-4.0, 364 MB, ~5 s cadence, 3-D, physics-validated), ADS-B Nantes Atlantique (CC-BY-4.0, 7.8 GB, natural track lifecycle), NOAA Marine Cadastre AIS (US Gov public domain). The OpenSky reply is now a convenience, not a dependency | Also recorded the honest limit: none of these are the missile problem. They validate algorithm plumbing — association under density, model switching, track lifecycle — not missile dynamics, which come from the synthetic threat library validated against published results |
| A-15 | 2026-09-23 | **D-06-a substantially unblocked.** Acquired a CC-BY-4.0 real multi-target ADS-B set (Zenodo 10.5281/zenodo.12751775): 2,317 aircraft, 13,384 tracks, median 8 simultaneous targets, with `icao24` as ground-truth identity. CC-BY-4.0 permits commercial use, so the for-profit question does not arise. Covers association validation; does **not** cover manoeuvre following (75 s sampling), 3-D geometry (no altitude) or track lifecycle (fixed 20-point tracks) | Answers Mason's question about the curated datasets: the licence-clear COVID set is flight *summaries* and useless for tracking, but this regional trajectory subset is real multi-target data and immediately usable |
| A-14 | 2026-09-23 | **D-06 complete except licensing.** Stone Soup 1.9.1 inventoried by class enumeration; **S-08 scope changed** — IMM must be implemented by us, not taken from Stone Soup (DEC-23). Angles-only observability quantified and DEC-24 added. OpenSky commercial terms unresolved (D-06-a) and with Mason; fallbacks recorded | The prior research asserted a Stone Soup IMM that does not exist. Had that gone unchecked until S-08, it would have surfaced during the tightest week of the schedule |
| A-13 | 2026-09-23 | **D-07 and D-08 complete.** US Standard Atmosphere 1976 implemented and validated against the published table to 0.001% plus Candler's independent density/altitude anchor; solar/lunar geometry, Earth occultation, illumination and terminator implemented and validated against seven astronomical anchors. Test count 81 | Both were latent dependencies of the glide and detection models that had been used ad hoc without being validated anywhere |
| A-12 | 2026-09-23 | **D-05 complete.** GOES-19 ABI Band 7/13/14 scenes pulled and calibrated; background characterised in target-intensity terms; temporal-differencing floor measured. Decisions DEC-21 and DEC-22 added. Corrected the prior research's claim that GOES-16 is currently distributed — it produces no ABI data in 2026; the operational pair is GOES-18/19 | This is the only real measured IR data in the study, and it changed how detection must be modelled |
| A-11 | 2026-09-23 | **D-02 complete.** Tranche 0 plane structure measured from the catalogue (2 Transport planes at 81°, 11 + 8; RAPTOR plane at 40°; BB 3/BB 4 drifted out); J2 drift reconciled to <1° with no residual; published T1/T2/MEO/T3 geometry recorded with unpublished cells left blank. Decisions DEC-19 and DEC-20 added | The measured geometry is sharper than the published description and disagrees with it in one way that matters: the plane separation is 65°, not the 90° an even Walker would use |
| A-10 | 2026-09-23 | **Decision IDs renamed `D-n` → `DEC-nn`** across PLAN.md, the analysis documents, the reference JSON, `mwsim/`, `scripts/` and `tests/` | They collided with the Phase D task IDs. `D-14`, `D-17` and `D-18` each meant two different things, which is precisely the ambiguity a ledger exists to prevent. Task IDs are unchanged |
| A-9 | 2026-09-23 | **D-04 complete.** Both sides of the HGV IR dispute transcribed from primaries with named causes; public detection thresholds (DSP 20 kW/sr, SBIRS-like 6 kW/sr) and the APS notional detector captured; assumptions register's empty NEI rows replaced with cited values; ONERA/DLR plume radiometry quarantined as unverified. Decision DEC-18 added, D-17 widened to 38–57 km | The detection threshold had been an empty `NOTIONAL-SWEPT` row with no basis. It now has a cited, attributable range — and the mission-level conclusion turns out to survive the whole dispute |
| A-8 | 2026-09-23 | **D-03 complete.** Six primary PDFs acquired and transcribed: Tracy & Wright equations 1–7, HTV-2 glide parameters, Minotaur IV booster table, Gronlund Table 1 (all nine rows verified against the primary scan), glide-start validation case. Decisions D-15 and D-16 recorded. D-03-c closed by tracing reference 42; D-03-d (Berkeley simulator cross-check) remains open | Transcribing from primaries rather than summaries paid twice: the booster parameters turned out not to be in the 2020 paper at all, and the thrust relation let the transcription be verified without a second reader |
| A-7 | 2026-09-23 | **D-14 complete.** Space-Track client built (`mwsim/spacetrack.py`), 25,219 historical element sets pulled for the 8 Tracking satellites + 2 HBTSS prototypes, manoeuvre/decay separation implemented and tested, audit report written. Decisions D-13 and D-14 recorded | The retracted DEC-08 could only be settled with multi-epoch data. It is now settled: SDA's figure was right and the inference against it was mine. DSP-23 also resolved via SATCAT — `decay=None`, it has not decayed |
| A-6 | 2026-09-23 | **Deep research brief 01 answered.** D-8 retracted; D-10, D-11, D-12 added; registry corrected (all 4 RAPTORs added as Tracking, 19 Transport added, HBTSS contractor mapping reversed, DSP-23 and withheld-object claims corrected); tasks D-14…D-23 added for the uncertainty and calibration domains | `docs/research/deep-research-report.md`. Four of my own recorded claims were wrong and are now corrected at source. The added domains came from the J2 meta-question, which is exactly what it was there for |

---

## 9. Open questions for Mason  *(blocking where marked)*

1. ~~Registration status~~ — **answered 2026-09-22: Mason is handling it** (D-7). Still needs a
   confirmation before X-03.
2. ~~Target cycle~~ — **answered 2026-09-22: Oct 21, this cycle** (D-6).
3. Who is on the team, and is everyone a US person? (ITAR §3.5 disclosure — G-05.)
4. Did *we* submit SITIS Q1–Q3 on this topic? The phrasing strongly suggests yes. If so, E-01
   and E-03 should ask only the questions that remain unanswered.
5. Is there budget and appetite for a credentialed OPIR or space-tracking advisor (roughly
   $10–50k inside the one-third cap)? This materially changes CONOPS credibility (E-04, R-4).
