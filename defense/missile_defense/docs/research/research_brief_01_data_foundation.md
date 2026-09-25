# Deep-research brief 01 — Data foundation

**For:** a research assistant with web access.
**From:** a small software company building a Phase I SBIR feasibility study.
**Date raised:** 2026-09-22.

---

## How to answer this brief

Read the context, then answer the numbered questions in Part 2. A few standing
instructions, because this work feeds a government proposal that will be evaluated by
MITRE and The Aerospace Corporation:

1. **Cite a primary source for every factual claim.** Prefer, in order: the operating
   agency's own publication (SDA, SSC, MDA, USSF fact sheets and press releases), GAO/CRS
   reports, peer-reviewed literature, then reputable trade press (Breaking Defense,
   SpaceNews, Defense News), then hobbyist/aggregator sites (Gunter's Space Page,
   n2yo, Wikipedia) **last and explicitly flagged as such**.
2. **Label every statement** as one of: `PUBLISHED` (a primary source says it),
   `REPORTED` (trade press says it, agency has not confirmed), `INFERRED` (your reasoning
   from published facts — show the reasoning), or `UNKNOWN/CLASSIFIED` (you could not find
   it publicly). An honest `UNKNOWN` is worth more to us than a confident guess.
3. **Where sources conflict, say so and give both**, with dates. Do not silently pick a
   winner. Conflicts are useful to us — we report them as sensitivity parameters.
4. **Flag anything that looks export-controlled or non-public.** We are building
   exclusively from public-domain information (22 CFR 120.34). If a question can only be
   answered with non-public data, say that, and stop. Do not seek out or reproduce
   controlled technical data.
5. **Dates matter.** Constellation counts, contractor assignments and launch dates change
   monthly. Give the as-of date for every figure.

---

## Part 1 — Context

### What we are doing

We are preparing a proposal against **SBIR topic DAF26BX06-NV510, "AI/ML for Next
Generation of Missile Detection, Warning, Tracking, and Reporting"** (SpaceWERX, with Space
Systems Command's Space Sensing Delta 84 and the OPIR Tap Lab). Phase I is $150,000 over
three months; the deliverable is a feasibility study, a USSF CONOPS, and simulation
results — not a fielded algorithm.

Our approach, which the government has already confirmed in the solicitation's public Q&A
is responsive: build an **open, reproducible, deterministic simulation that screens the
multi-orbit OPIR sensing trade space**. The question it answers is *which* constellation,
revisit, detection-threshold and fusion-placement parameters actually drive
**warn-to-decision time** and **track continuity** against ballistic and maneuvering
threats — and therefore where AI/ML fusion would have real leverage, measured against a
quantified classical baseline. The headline artifact is a warn-to-decision-time versus
track-accuracy Pareto frontier across three fusion placements: ground-centralized,
on-orbit (edge), and hybrid.

We are **not** proposing a new detection algorithm in Phase I.

### Where we are

We are in the **data foundation phase**, which we will not leave until every data type and
source of use has been identified, acquired, organized and *understood*. We are
deliberately not building simulation components yet.

We have built and validated an orbital propagation stack: SGP4/SDP4 agreeing with Vallado's
published verification vectors to 1.2e-7 km (0.12 mm) across 533 state vectors, plus
TEME→ECEF→WGS-84 geodetic conversion. We pull orbital elements from the CelesTrak GP API
(OMM/JSON).

### The problem that triggered this brief

We seeded our object registry from a prior research document that mapped NORAD catalog
numbers to SDA/MDA missions. **We now doubt that mapping**, and we cannot proceed until it
is right — a wrong object→mission assignment would silently corrupt coverage geometry,
stereo availability and the headline chart.

The prior document told us:

| NORAD | COSPAR | Claimed to be |
|---|---|---|
| 56171, 56170 | 2023-050K, 2023-050J | SDA Tranche 0 Tracking Layer, SpaceX-built ("BB 1", "BB 2" / T0TR 1-2) |
| 57760, 57757 | 2023-133D, 2023-133B | SDA Tranche 0 Tracking Layer, SpaceX-built ("BB 3", "BB 4" / T0TR 3-4) |
| 58959 | 2024-028E | SDA Tranche 0 Tracking Layer, L3Harris-built ("Raptor 2" / T0TR 6) |
| 58955, 58960 | 2024-028A, 2024-028F | MDA HBTSS prototypes SV2, SV1 |

It also told us the Tranche 0 Tracking Layer flies at **1000 km, 80° inclination** (citing
SDA's own "On Orbit" page), with Gunter's Space Page giving 950 km, 80–89.5°.

### What we actually measured

We pulled the full launch manifests and propagated the real elements. Measured
2026-09-22/23, over a 12-hour grid, altitude is WGS-84 geodetic:

**Launch 2023-050** (10 cataloged objects, all at i ≈ 81.00°):

| COSPAR | NORAD | CelesTrak name | Mean motion (rev/day) | Ecc | n-dot |
|---|---|---|---|---|---|
| 2023-050A | 56162 | CHECKMATE 8 | 13.8497 | 0.00073 | +6.6e-07 |
| 2023-050B | 56163 | CHECKMATE 5 | 13.8500 | 0.00073 | +7.0e-07 |
| 2023-050C | 56164 | CHECKMATE 4 | 13.8482 | 0.00065 | +2.6e-07 |
| 2023-050D | 56165 | CHECKMATE 6 | 13.8875 | 0.00194 | +2.7e-07 |
| 2023-050E | 56166 | CHECKMATE 7 | 13.8945 | 0.00217 | +2.0e-07 |
| 2023-050F | 56167 | CHECKMATE 2 | 13.8517 | 0.00078 | +6.9e-07 |
| 2023-050G | 56168 | CHECKMATE 1 | 13.8496 | 0.00122 | +3.1e-07 |
| 2023-050H | 56169 | CHECKMATE 3 | 13.8515 | 0.00075 | +1.9e-07 |
| 2023-050J | 56170 | **BB 2** | **14.4654** | 0.00080 | **+4.08e-06** |
| 2023-050K | 56171 | **BB 1** | **14.3428** | 0.00162 | **+2.02e-06** |

**Launch 2023-133** (13 cataloged objects, all at i ≈ 81.00°):

| COSPAR | NORAD | CelesTrak name | Mean motion | Ecc | n-dot |
|---|---|---|---|---|---|
| 2023-133A | 57756 | WILDFIRE 4 | 13.8637 | 0.00111 | +6.9e-07 |
| 2023-133B | 57757 | **BB4** | **14.8373** | 0.00107 | **+1.094e-05** |
| 2023-133C | 57758 | WILDFIRE 3 | 13.8629 | 0.00097 | +8.9e-07 |
| 2023-133D | 57760 | **BB3** | **14.8655** | 0.00089 | **+9.66e-06** |
| 2023-133E | 57761 | WILDFIRE 7 | 13.8511 | 0.00063 | +6.4e-07 |
| 2023-133F | 57762 | CHECKMATE 10 | 13.8548 | 0.00075 | +6.8e-07 |
| 2023-133G | 57763 | WILDFIRE 6 | 13.8577 | 0.00075 | +6.0e-07 |
| 2023-133H | 57764 | WILDFIRE 1 | 13.8575 | 0.00076 | +1.02e-06 |
| 2023-133J | 57765 | WILDFIRE 9 | 13.8544 | 0.00071 | +6.4e-07 |
| 2023-133K | 57766 | WILDFIRE 10 | 13.8565 | 0.00077 | +6.2e-07 |
| 2023-133L | 57767 | WILDFIRE 2 | 13.8550 | 0.00063 | +6.1e-07 |
| 2023-133M | 57768 | WILDFIRE 8 | 13.8546 | 0.00071 | +9.1e-07 |
| 2023-133N | 57769 | WILDFIRE 5 | 13.8581 | 0.00072 | -4.2e-07 |

**Launch 2024-028 (USSF-124)** (6 cataloged objects, all at i ≈ 39.99°):

| COSPAR | NORAD | CelesTrak name | Mean motion | Ecc | n-dot |
|---|---|---|---|---|---|
| 2024-028A | 58955 | HBTSS-SV2 | 13.7049 | 0.00178 | +5.6e-07 |
| 2024-028B | 58956 | RAPTOR4 | 13.7440 | 0.00136 | -3.2e-07 |
| 2024-028C | 58957 | RAPTOR1 | 13.7425 | 0.00107 | -3.3e-07 |
| 2024-028D | 58958 | RAPTOR3 | 13.7049 | 0.00100 | -5.4e-07 |
| 2024-028E | 58959 | RAPTOR2 | 13.7056 | 0.00103 | -5.9e-07 |
| 2024-028F | 58960 | **HBTSS-SV1** | **15.0378** | 0.00098 | **+3.297e-05** |

Derived mean geodetic altitudes for the objects we had seeded:

| Object | Mean altitude | Inclination |
|---|---|---|
| BB 1 (56171) | 789 km | 81.01° |
| BB 2 (56170) | 749 km | 81.00° |
| BB 4 (57757) | 629 km | 81.00° |
| BB 3 (57760) | 621 km | 80.99° |
| RAPTOR2 (58959) | 1001 km | 39.99° |
| HBTSS-SV2 (58955) | 1001 km | 39.99° |
| HBTSS-SV1 (58960) | 558 km | 39.99° |
| SBIRS GEO-1…6 | 35,781–35,792 km | 2.26–4.99° |

**Our observations, offered as hypotheses for you to confirm or refute — not as findings:**

- The `CHECKMATE` and `WILDFIRE` objects are tightly clustered (n = 13.848–13.895, i =
  81.00°, low and consistent drag terms). That is what an operational constellation plane
  looks like: members sharing a semi-major axis.
- The `BB` objects are outliers on every axis — higher mean motion (lower altitude),
  altitudes scattered across ~170 km, and n-dot 3–20× larger than their launch-mates. High
  n-dot means the orbit is contracting.
- `HBTSS-SV1` has by far the largest n-dot in the whole set (+3.3e-05) and sits 443 km
  below its launch-mate `HBTSS-SV2`.
- **Hypothesis A:** `BB` are the SpaceX-built Tranche 0 *Tracking* satellites and
  `CHECKMATE`/`WILDFIRE` are the *Transport* Layer. Counts fit roughly (9 CHECKMATE + 10
  WILDFIRE ≈ 20 Transport; 4 BB + 4 RAPTOR = 8 Tracking, matching the published Tranche 0
  Tracking count). The scattered low altitudes would then be explained by end-of-demo
  disposal or degradation, not by SDA's published figure being wrong.
- **Hypothesis B:** the `BB` objects are not payloads at all (deployment hardware, adapters
  or debris), and the tracking payloads are among the `CHECKMATE`/`WILDFIRE` set.
- **Hypothesis C:** the prior document's NORAD mapping is simply wrong.

We do not know which is right, and the distinction changes what we can legitimately claim.

---

## Part 2 — Questions

Priority 1 questions block our current phase. Priority 2 shape the simulation design.
Priority 3 strengthen the proposal narrative.

### A. Catalog object identification — **PRIORITY 1, blocking**

**A1.** For launches 2023-050 (SDA Tranche 0, ~2 April 2023) and 2023-133 (~2 September
2023): what was the actual manifest? How many Transport Layer and how many Tracking Layer
satellites flew on each, and who built them? Was there a third Tranche 0 launch?

**A2.** What do the catalog names `CHECKMATE`, `WILDFIRE`, `BB` and `RAPTOR` designate? Are
these SDA program nicknames, contractor names, or catalog conventions? Which contractor and
which layer (Transport vs Tracking) does each correspond to?

**A3.** **The central question:** is there an authoritative, citable mapping from NORAD
catalog number to SDA Tranche 0 payload and layer? If a definitive public mapping does not
exist, say so plainly — that itself is a finding we would report.

**A4.** SDA's Tranche 0 Tracking Layer is stated as 8 satellites. Which 8 catalog objects
are they? Are the 4 `RAPTOR` objects on USSF-124 (i = 40°) part of the Tranche 0 Tracking
Layer, and if so why are they at 40° inclination when SDA describes the Tracking Layer as
near-polar?

**A5.** Are the `BB` satellites still operational? Have they been deorbited, lowered for
disposal, or degraded? Is there any public reporting on Tranche 0 satellite health,
end-of-mission, or disposal? (Their high and rising drag terms suggest orbital decay.)

**A6.** Is there public reporting on HBTSS-SV1's orbit? It sits ~443 km below HBTSS-SV2
with a very large drag term. We have seen it reported that one of the two HBTSS prototypes
(Northrop Grumman's) did not meet requirements while the other (L3Harris's) did — can you
confirm which NORAD ID is which contractor's, and whether the orbit difference is related?

**A7.** Which US missile-warning satellites are *withheld* from the public catalog (no
published elements)? We believe SBIRS, DSP, SDA Tracking and HBTSS are all published and
that the withheld set is chiefly NRO payloads — is that correct and current?

**A8.** DSP-23 (NORAD 32287) returned no GP data from CelesTrak. Is it decayed, retired,
removed from the active catalog, or renumbered? Are any DSP satellites still cataloged
with published elements?

### B. Constellation geometry — **PRIORITY 1**

**B1.** What are the authoritative, agency-published Walker parameters (number of planes,
satellites per plane, altitude, inclination, phasing) for: Tranche 0 Tracking, Tranche 1
Tracking, Tranche 2 Tracking? Give the SDA source and its date for each.

**B2.** Same question for the SSC **MEO Resilient Missile Warning / Missile Tracking**
program ("Epoch 1", "Epoch 2"). How many satellites, what orbital planes, what altitude,
what inclination — and how much of this is published versus planned-but-unstated? What has
actually launched as of late 2026?

**B3.** Is any field-of-view or field-of-regard figure published in degrees for the WFOV
and MFOV OPIR sensors (SDA Tracking, HBTSS, MEO)? We expect this to be classified and plan
to parameterize it — we want to know whether *any* citable public number exists, including
notional ones used in think-tank studies.

**B4.** The CSIS study "Getting on Track: Space and Airborne Sensors for Hypersonic Missile
Defense" (Masao Dahlgren, Dec 2023) reportedly uses a notional 135-satellite LEO
constellation at 1000 km with a 120° field of regard. Can you confirm those parameters and
extract the full set of notional sensor and constellation assumptions that study uses? It
is our most valuable citable proxy, because it is public, analytical, and written by people
our evaluators respect.

**B5.** What ground stations does the OPIR ground segment use, and are their locations
public? This drives the downlink-latency term in our fusion-placement comparison.

### C. Latency and architecture — **PRIORITY 1** (this drives the headline chart)

**C1.** What public figures exist for any part of the missile-warning timeline —
detection-to-alert, alert-to-dissemination, warn-to-decision? We have seen ~30 s
legacy detect-to-alert (INSS, 2025) and "on the order of 1 minute to detect and
characterize" (National Academies). What else is citable, and how firm is each?

**C2.** What is published about the SDA Transport Layer's optical crosslink data rates,
latency, and Link 16 injection? Ground-versus-orbit latency deltas are the core of our
trade study, so any published per-hop number is valuable.

**C3.** Is there any public description of on-orbit processing capability for OPIR
satellites — processor class, power budget, whether processing is done on board at all?
This bounds what "edge fusion" can plausibly mean.

**C4.** What does "fire-control quality" track mean, quantitatively, in any public source?
We expect the numeric thresholds to be classified and will say so — but we want to know if
anyone has published even an order-of-magnitude figure.

### D. Threat trajectory models — **PRIORITY 2**

**D1.** Confirm availability and give working URLs for: Tracy & Wright, "Modeling the
Performance of Hypersonic Boost-Glide Missiles" (*Science & Global Security* 28, 2020);
Acton (*S&GS* 23); Wright (*S&GS* 23); Candler (*S&GS* 30); Fetter, "A Ballistic Missile
Primer"; Gronlund & Wright, "Depressed Trajectory SLBMs" (*S&GS* 3, 1992); Wilkening
(*S&GS* 12, 2004).

**D2.** From Tracy & Wright specifically: the full set of equations of motion, the state
variables, the integration scheme, and every numeric parameter given (ballistic
coefficient, lift-to-drag ratios, vehicle mass, reference area, initial conditions). We
intend to re-implement and validate against their published results.

**D3.** Is the Berkeley BRSL web-based Hypersonic Glide Vehicle Simulator still online?
What are its URL, inputs, outputs, and published validation cases? We want to use it as a
reference oracle for our own integrator.

**D4.** From Gronlund & Wright: the complete Table 1 (or equivalent) of trajectory
parameters. We have burnout velocity 6.3 km/s, apogee 1340 km, flight time 29.2 min for a
7400 km minimum-energy trajectory — confirm and give the rest of the table.

**D5.** What open-source implementations of ballistic or boost-glide trajectory integration
exist, with what licenses? We must avoid GPL/AGPL for commercialization reasons.

**D6.** What are credible public parameter sets for the threat classes we need — SRBM,
MRBM, ICBM, HGV, and a depressed-trajectory SLBM? Range, burn time, burnout velocity,
apogee, flight time, and typical maneuver authority for the glide vehicle.

### E. Infrared signatures and phenomenology — **PRIORITY 2**

**E1.** What is genuinely public on rocket-plume infrared radiant intensity? We have
references to an ONERA soot-plume study (MWIR ≈ 491–593 W/sr, SWIR ≈ 987–1518 W/sr, LWIR ≈
96–103 W/sr, bench scale) and DLR launch-vehicle plume measurements (~1500 K). Confirm
these, give full citations, and find anything better — particularly anything at full scale
rather than bench scale.

**E2.** What is published on the *hardbody* (non-plume) infrared signature of a hypersonic
glide vehicle in the glide phase? This is the hard case — dim, no plume — and it sets when
custody becomes possible. Candler's CFD paper may be relevant.

**E3.** Which infrared bands are used or recommended for space-based missile warning, and
why? We have 2.7 µm and 4.3 µm (CO2 and CO emission bands) from open literature, and the
MWIR 3–5 µm atmospheric window. Confirm with sources.

**E4.** What public models or datasets exist for atmospheric transmission in those bands
(MODTRAN alternatives, HITRAN-derived tools) with permissive licensing?

**E5.** What is the state of public knowledge on infrared *background* clutter for
space-based sensors — cloud tops, Earth limb, sun glint, terrain? What magnitudes, and what
public data could characterize it?

### F. Infrared background imagery and detection data — **PRIORITY 2**

**F1.** Confirm the current access path, bucket naming and file schema for GOES-R ABI
Level-1b radiances on AWS Open Data. Which channels are the MWIR/LWIR ones, what is the
temporal cadence, and what Python tooling is current?

**F2.** Is there *any* public dataset of space-based infrared launch detections? We believe
the answer is no and plan to say so in the proposal. Confirm or refute.

**F3.** The SDA TAP Lab "Project Apollo" reportedly included GOES-16-based launch detection
by CU Boulder. Is the method published in enough detail to reproduce? Is any code or data
released? Give the AMOS paper citation.

**F4.** What public data exists on observed launches that could serve as truth for a
detection experiment — launch times, locations, vehicle types — that could be correlated
against GOES imagery?

### G. Tracking benchmarks and tooling — **PRIORITY 2**

**G1.** What are the current OpenSky Network access terms for a **for-profit company**
(not a university)? Specifically: live REST API, historical Trino/SQL access, and the
curated scientific datasets. What can we legally use, and does anything require a license?

**G2.** What published benchmark results exist for Stone Soup's IMM, JPDA and MHT
implementations that we could validate our pipeline against?

**G3.** Is there published work on angles-only or bearings-only target tracking from
space-based infrared sensors, particularly on observability limits and the stereo geometry
required for a 3-D fix? What convergence angle is needed for a usable range estimate?

**G4.** What is the state of the art in learned data association and learned model
selection for maneuvering-target tracking? We need to know the honest ceiling on the ML
claim, and where ML has been shown to beat IMM/JPDA on maneuvering targets.

### H. Program and proposal context — **PRIORITY 3**

**H1.** What is the **Space Modernization Initiative (SMI)** within SSC's Space Sensing
portfolio? The topic names it as the Phase III transition pipeline. How does it work, what
has transitioned through it, and how should a Phase I proposal describe a path into it?

**H2.** What is the current, verified OPIR Tap Lab (boulderlab.org) engagement model —
registration, cohorts, briefing cadence, clearance requirements, and what an SBIR awardee
actually does there? Note that reporting frequently conflates the **OPIR** Tap Lab
(Boulder) with the **SDA** Tap Lab (Colorado Springs, "Project Apollo"); please keep them
distinct and say which is which.

**H3.** For an offeror with no cleared personnel and no facility clearance, what is the
realistic path to working with the OPIR Tap Lab? Are there documented cases of uncleared
small businesses onboarding?

**H4.** What is the current status of the Next-Gen OPIR program, the FORGE ground segment,
and Golden Dome as they relate to missile warning sensing and data processing? We need
enough to write an accurate "existing solutions" section — the topic requires us to
identify benefits over existing solutions.

**H5.** Who are the incumbent contractors in OPIR ground processing and missile-warning
data fusion, and what have they publicly delivered? We must not claim novelty for something
a prime already fields.

### I. Doctrine and format — **PRIORITY 3**

**I1.** For DoDAF 2.02, give the authoritative definition and expected content of AV-1,
OV-1, OV-2, OV-5b, OV-6c and SV-1. What does a *good* OV-1 for a space sensing system look
like, and are there public examples?

**I2.** From the GAO Technology Readiness Assessment Guide (GAO-20-48g), which the topic
cites: what is the expected structure for identifying Critical Technology Elements, and
what evidence does GAO expect for a TRL claim?

**I3.** Are there publicly available examples of successful SpaceWERX or SBIR Phase I
feasibility studies and CONOPS documents we could study for structure and register?

### J. Meta — **PRIORITY 1**

**J1.** We are working from two prior research documents that we now suspect contain
errors (the NORAD mapping being one). **Which specific factual claims listed in Part 1
above are wrong, outdated, or unsupported?** Be blunt. We would rather find errors now than
have an Aerospace Corporation reviewer find them.

**J2.** What important data sources, datasets, tools or bodies of literature has this brief
failed to ask about? The purpose of our current phase is to enumerate every data domain we
need *before* we build, so a gap in this brief is itself the most valuable thing you could
find.

---

## Part 3 — What we will do with the answers

Everything above feeds a data inventory with, per source: what it is, provenance, units and
conventions, accuracy and failure modes, license and redistribution terms, which downstream
task consumes it, and what it does *not* contain. Quantities that are classified in reality
become swept parameters in our simulation, never sourced values, and the proposal states
that boundary explicitly.

We are not asking you to find classified information, and we will not use it if offered.
The value of this work is precisely in showing how far a credible analysis can be taken on
entirely public data — and in being honest about where that stops.
