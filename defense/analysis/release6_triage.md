# Release 6 Triage — DoW SBIR/STTR FY26 (opens 2026-09-23, closes 2026-10-21)

Source: `release6_raw.csv` (43 topics reconstructed from the DSIP BAA/CSO/STTR PDFs; missed entirely by the sbir.gov export).
Stage 0: `release6_stage0.csv` — 21 survivors after the corrected D2P2 rule (22 topics are D2P2-only, see bottom).
Same method and tagging as `triage_results.md`. No SBIR.gov award searches were run; Stage 2 is `[INFERRED]`/UNKNOWN.
Q&A: DSIP Topic Q&A accepts new questions until **2026-10-07 12:00 ET**; direct TPOC contact ends **2026-09-23**.

**Shortlist (PURSUE):** DPA26BZ06-DV026, ARM26BX06-NV012 (+STTR twin NV003), DAF26BX06-NV510, DAF26TZ06-NV007, DAF26TX06-NV514, OSW26BZ06-NV028, OSW26BZ06-DV025.

---

## 1

```
TOPIC:        ARM26BX06-NV012 — Agentic-AI, Schema-Driven Decision Management for Auditable Studies and Acquisition Decisions
BRANCH:       ARMY   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "A decision schema that makes objectives, options, constraints, assumptions, risks, and bias checks first-class objects"; "Agentic AI that: performs structured elicitation into the formal model, then generates decision workflow plans, and executes reproducible evaluation runs"; "Two end-to-end demonstrations"
FLAGS:         T0.4 Registration check | CMMC Level 1

PLAIN PROBLEM: Build a structured schema plus an LLM-agent layer that turns a messy engineering/procurement question into a reproducible, auditable decision package, and show it works for both a one-off trade study and a multi-year decision that gets refreshed as facts change.
GAPS:
- [INFERRED] Ground-vehicle acquisition domain knowledge (PAE Maneuver Ground / PAE Fires context) — but [Q&A] "For Phase I, offeror generic documents are sufficient" and "offeror synthetic modeling is sufficient if PAE or PM data is not forthcoming."
- [INFERRED] SysML 2.0 / digital-engineering tool integration experience (named as an interoperability target).
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] Names DAOSoft as "the current COTS application," but [Q&A] "DAOSoft is not a requirement!... All offerors have complete freedom to base their workflow on their own chosen platform, integrate with DAOSoft, or replace DAOSoft" and the Government "places no restrictions on your software design." [Q&A] Phase II "COTS is better, specific wording than open-source. Offerors will own their own code."
DELTA:         [INFERRED] Commercial decision-intelligence / LLM-agent tooling exists broadly; the delta is the auditable, signer-ready schema (bias checks, assumptions, "what flips the decision") and refresh-cycle semantics for long-horizon acquisition decisions.
EXPERIMENT:    [INFERRED] Build a small decision schema (options/constraints/assumptions/risks as typed objects) and an agent that elicits a public trade-study case (e.g., a published vehicle powertrain trade-off) into it, then re-run with one assumption changed to verify the "what flips the decision" output is deterministic and traceable.
REUSE:         [INFERRED] Backend/data-modeling and LLM-agent orchestration experience map directly; this is a schema + workflow + evaluation-harness build.
DUAL USE:      [TOPIC TEXT] "the vehicle design process for the automotive industry"; [INFERRED] any enterprise product-development trade-study workflow.
DIFFERENTIATOR:[INFERRED] The topic explicitly wants "proof by demonstration (not a full product build)" and is agnostic to platform — a small software team can move faster than an ERP-style integrator, and the Q&A removes the incumbent-tool dependency.
CONFIDENCE:    HIGH. Would raise with a look at the referenced SAE paper (2025-01-0455) to align vocabulary with the topic author.
```

---

## 2

```
TOPIC:        ARM26TX06-NV003 — Agentic-AI, Schema-Driven Decision Management for Auditable Studies and Acquisition Decisions (STTR twin)
BRANCH:       ARMY   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — identical text to ARM26BX06-NV012 (#1)
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Same as #1.
GAPS:
- [TOPIC TEXT] STTR requires a research-institution partner at ≥30% of work — a university digital-engineering / decision-science group.
- Same domain gaps as #1.
LANDSCAPE:     Same as #1. [TOPIC TEXT]-observable: offered in both SBIR and STTR tracks in the same release, which points to a broad, non-wired ask.
DELTA:         Same as #1.
EXPERIMENT:    Same as #1.
REUSE:         Same as #1.
DUAL USE:      Same as #1.
DIFFERENTIATOR:Same as #1; the STTR route is the fallback if an RI partner adds credibility on decision science/MBSE.
CONFIDENCE:    HIGH on fit; MEDIUM on execution pending an RI partner. Submitting to one of the two twins (not both) is the sensible move.
```

---

## 3

```
TOPIC:        DAF26BX06-NV510 — AI/ML for Next Generation of Missile Detection, Warning, Tracking, and Reporting
BRANCH:       USAF (SpaceWERX)   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms/simulation — [TOPIC TEXT] "Phase I deliverables are expected to focus on a feasibility study detailing USSF CONOPS and technical viability, as well as analytical findings"; "a Phase I research plan that can include modeling, simulation, literature review, or trade studies"
FLAGS:         T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Work out, mostly by simulation and trade study, where AI/ML fusion of satellite infrared, radar and other feeds would actually shorten the time from detecting a missile launch to a decision, across mixed GEO/MEO/LEO constellations.
GAPS:
- [INFERRED] OPIR sensor data and threat scenarios are classified/ITAR; Phase I must run on synthetic constellation geometry and open literature.
- [INFERRED] Orbital-mechanics / sensor-geometry modeling expertise (revisit, latency, observational geometry).
- [TOPIC TEXT] Foreign nationals restricted under ITAR — staffing constraint.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] Transition target is the OPIR Tap Lab (boulderlab.org) and SSC Space Sensing / SMI. [Q&A] TPOC confirmed a "deterministic simulation that screens the multi-orbit OPIR sensing trade space" is responsive, that "in-space edge compute architecture(s) would be considered," and that "mission-aware orchestration and AI-assisted trade-space decision management" is "an appropriate submission" — i.e., no new detection algorithm is required in Phase I.
DELTA:         [INFERRED] Commercial multi-sensor fusion/tracking (autonomy, ATC) exists; the delta is multi-orbit OPIR geometry, hypersonic/maneuvering target dynamics, and explainability for a mission-assurance kill chain.
EXPERIMENT:    [INFERRED] Build a constellation/revisit simulator from public TLE-style orbits and a synthetic boost-phase trajectory set, then measure warn-to-decision latency under different fusion placements (ground vs. edge) — this is the exact trade-space study the TPOC said is responsive.
REUSE:         [INFERRED] Simulation, data pipelines, ML — direct reuse; no existing space-domain assets.
DUAL USE:      [INFERRED] Multi-orbit sensor tasking/fusion has commercial analogues in Earth-observation constellation scheduling and space-traffic management, though the topic text names none.
DIFFERENTIATOR:[INFERRED] Feasibility-study framing rewards analytical rigor over platform heritage; a software team can deliver a defensible CONOPS + simulation without any hardware.
CONFIDENCE:    MEDIUM-HIGH. ITAR staffing is the main practical constraint; would raise with a reading of the OPIR Tap Lab's public onboarding material.
```

---

## 4

```
TOPIC:        DAF26BZ06-NV034 — Low Noise & Low-SWaP High-Repetition Rate Mode-Locked Lasers for High-Speed Photonics
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "Develop a proof-of-concept for the necessary components... a breadboard 6 to 12 GHz mode-locked laser... Component development is to include semiconductor gain medium, saturable absorber... and necessary fabrication steps"
KILL REASON:   [TOPIC TEXT] Semiconductor laser component fabrication in Phase I — no fab, no photonics lab.
KILL CLASS:    PERMANENT
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build a compact laser that pulses 6–12 billion times per second with very low timing jitter.
GAPS:
- [TOPIC TEXT] Semiconductor gain-medium and saturable-absorber fabrication.
- [INFERRED] Ultrafast-optics measurement lab.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 5

```
TOPIC:        DAF26BZ06-NV035 — Quantum Memory for Secure Communication
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (a) study, leading to (c) — [TOPIC TEXT] "develop a conceptual design for a functional quantum memory prototype... Demonstrate Technology Readiness Level 3 by drafting a feasibility report and a detailed architecture plan for a Phase II prototype of a lab-based test bench"
KILL REASON:   [INFERRED] Phase I is paper-only, but a credible quantum-memory feasibility report requires quantum-optics domain expertise the team lacks, and Phase II is a lab test bench — no viable path without a quantum-photonics partner.
KILL CLASS:    CONTINGENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Design a device that stores photonic qubits long enough to extend quantum key distribution over long distances.
GAPS:
- [INFERRED] Quantum-optics domain SMEs.
- [INFERRED] Phase II quantum-photonics lab.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH. Re-open only with a quantum-photonics partner in hand.
```

---

## 6

```
TOPIC:        DAF26BZ06-NV036 — Flightline Radio Network
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      HOLD
STAGE REACHED: 3

DELIVERABLE:   (a) study + (b)/(c) small prototype — [TOPIC TEXT] "Phase I will assess the feasibility of an Open RAN network for flight line use at Edwards AFB. It will outline network architecture, components, deployment strategy, and address potential interference with aircraft systems. Deliverables include security analysis, use cases, and integration plans... demonstrating proof-of-concept through a preliminary prototype"
FLAGS:         T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Design a private 5G network (using open, vendor-neutral radio software) for an airbase flight line so maintainers get real-time aircraft data and AR guidance, and prove it won't interfere with aircraft.
GAPS:
- [INFERRED] RF spectrum/regulatory and aircraft-EMI analysis expertise ("address potential interference with aircraft systems").
- [INFERRED] Access to Edwards AFB / 412th MXG stakeholders for requirements.
- [INFERRED] Phase II is base infrastructure deployment (base stations, user equipment) — an integrator's job, not a software team's.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Open RAN stacks (srsRAN, OpenAirInterface, ONF SD-RAN) are open source and run on COTS SDR, so a benchtop Phase I prototype is feasible; incumbents are private-5G integrators already selling to DoD bases.
DELTA:         [INFERRED] Flight-line EMI constraints, security posture (CMMC/ATO), and AR-maintenance integration versus generic private-5G deployments.
EXPERIMENT:    [INFERRED] Stand up an open-source 5G core + gNB on a COTS SDR in the lab, attach a maintenance-data/AR client, and measure latency and throughput — proves the software side; the EMI analysis would still need an RF partner.
REUSE:         [INFERRED] Backend/network software; nothing on the RF/EMI side.
DUAL USE:      [TOPIC TEXT] "Commercial use spans complex logistics in aerospace sectors."
DIFFERENTIATOR:[INFERRED] Weak — the Phase II is an infrastructure build where integrators with base-deployment track records will be preferred.
CONFIDENCE:    LOW-MEDIUM. Would raise with an RF/EMI partner and a stakeholder contact at the 412th.
```

---

## 7

```
TOPIC:        DAF26TX06-NV514 — Space Domain Operational Environment Assessment
BRANCH:       USAF (USSF)   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/design — [TOPIC TEXT] TA2: "Design a concept for a workable and scalable prototype to address the basic capabilities and technical feasibility of the stated objective as well as data and information sources and the timeliness of their solution... Define a set of metrics and success criteria for a Phase 2 prototype... GFE will not be provided."
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Design software that fuses many data sources (tracking, intelligence, environmental) to tell space operators, in near real time, what is happening in orbit, whether an action worked, and what the adversary is doing.
GAPS:
- [INFERRED] Multi-INT data is classified; Phase I must use public catalogs (space-track TLEs, conjunction data, open-source news/intel proxies).
- [INFERRED] Astrodynamics / space-operations domain expertise — an RI partner (university space-systems lab) covers this.
- [TOPIC TEXT] TA1 (new sensing phenomenologies) is out of reach; propose TA2 only.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Commercial SDA analytics firms (LeoLabs-class, Slingshot-class) hold the sensor-data side; the TA2 "assessment/decision" layer is less crowded. [TOPIC TEXT] Phase III explicitly wants "a commercial product for commercial SDA."
DELTA:         [INFERRED] Operations *assessment* (did the task achieve its effect?) and adversary-intent reasoning versus commercial conjunction/catalog services.
EXPERIMENT:    [INFERRED] Using public TLE histories, build an anomaly detector for unexpected maneuvers / pattern-of-life breaks and measure detection lead time against known, publicly reported maneuvers — a concrete TA2 metric.
REUSE:         [INFERRED] Data pipelines, anomaly detection, dashboards — strong reuse (cf. Release 5 #26).
DUAL USE:      [TOPIC TEXT] "health and operational status of commercial satellites and their services in relation to adversaries' actions."
DIFFERENTIATOR:[INFERRED] A software team paired with an astrodynamics RI can own the analytics/assessment layer without sensors, which the topic explicitly allows ("GFE will not be provided").
CONFIDENCE:    MEDIUM. Would raise with a named RI partner and confirmation that public catalog data suffices for a credible TA2 demo.
```

---

## 8

```
TOPIC:        DAF26TZ06-NV007 — Automated Combat Assessment at the Edge
BRANCH:       USAF   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a)/(b) analysis, design, lab model — [TOPIC TEXT] "Phase I will focus on the analysis and design of an automated combat assessment at the edge system... with preliminary laboratory model testing. Awardees must demonstrate an innovative approach to physical and functional combat assessment, and novel or under-utilized data modalities."
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Build software that runs on a drone or field sensor and decides, minutes after a strike, whether the target was physically destroyed and whether it still works, with a confidence level, so planners can re-strike.
GAPS:
- [TOPIC TEXT] "the lack of real time pre- and post-event satellite imagery for model training" — the sponsor names the data gap itself.
- [INFERRED] Military damage-assessment doctrine (CJCSI 3162.02, ICD 203 confidence language) — readable public documents, cited in the topic.
- [INFERRED] Edge-hardware deployment experience (low SWaP) — COTS Jetson-class boards suffice for Phase I lab testing.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Public building-damage datasets (xBD / xView2, pre/post disaster imagery) are the standard academic benchmark for exactly this task; commercial catastrophe-damage models exist for insurance.
DELTA:         [INFERRED] Functional (not just physical) damage, novel modalities (SAR, thermal, acoustic), doctrinal confidence reporting, and edge execution under contested comms versus cloud-based disaster mapping.
EXPERIMENT:    [INFERRED] Fine-tune a lightweight segmentation model on xBD pre/post pairs, quantize it for a Jetson/Coral board, and measure accuracy and latency against the ICD-203-style confidence bands — directly answers "can this run at the edge with usable confidence."
REUSE:         [INFERRED] ML/edge-inference pipeline work (cf. Release 5 #31) — strong reuse.
DUAL USE:      [TOPIC TEXT] "urban surveillance, disaster and humanitarian response."
DIFFERENTIATOR:[INFERRED] Open benchmark data plus edge-ML competence lets a small team show a working lab model in Phase I; an RI partner in remote sensing strengthens the "novel modalities" requirement.
CONFIDENCE:    MEDIUM-HIGH. Would raise with a remote-sensing RI partner and a check of the referenced AFRL BAA FA8750-25-S-7002 for incumbent signals.
```

---

## 9

```
TOPIC:        DPA26BZ06-DV025 — Noninvasive Detection and Localization of Occult Hemorrhage
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/clinical — [TOPIC TEXT] "develop a proof-of-concept sensing and artificial intelligence framework capable of accurately identifying the anatomical source of bleeding and estimating hemorrhage rate"
KILL REASON:   [INFERRED] Requires a physical sensing modality (ultrasound/RF/optical) and clinical or animal-model validation — medical-device development outside the team's competency and facilities.
KILL CLASS:    PERMANENT
FLAGS:         T0.1 D2P2 also accepted | T0.4 Registration check

PLAIN PROBLEM: Build a field device that tells a medic where someone is bleeding internally and how fast.
GAPS:
- [INFERRED] Medical sensing hardware and clinical validation pathway.
- [INFERRED] Trauma-medicine domain SMEs.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 10

```
TOPIC:        DPA26BZ06-DV026 — Influence Benchmarks for AI Systems
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "develop and define the architecture of the test environment and demonstrate a functional proof of concept for a simulated auction or market... develop classifiers to detect biases in AI agent behavior... By Month 9, proposers must demonstrate a suite of 'stock' AI agents... drawn from at least 10 different LLMs... By Month 12... allocative efficiencies of >90%"
FLAGS:         T0.1 D2P2 also accepted (Phase I still open) | T0.4 Registration check | CMMC Level 1

PLAIN PROBLEM: Build a simulated marketplace where many LLM agents bid against each other and against human-like agents, so you can measure an AI's hidden biases, deception, or collusion from its behavior alone — without access to its weights.
GAPS:
- [INFERRED] Experimental/behavioral economics expertise to calibrate "human baseline" bidding models (the topic cites auction-theory literature) — advisor-level, not a blocker.
- [INFERRED] LLM API budget for ≥10 models × repeated market runs.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] Names an open-source starting point: "Magentic Marketplace (Bansal et al. 2026)"; cites OpenAgentSafety and NVIDIA agent-evaluation guidance. [INFERRED] AI-safety evals are a crowded academic space, but market-mechanism-based behavioral testbeds are a narrow niche.
DELTA:         [TOPIC TEXT] "economic frameworks do not rely on a priori definitions of 'harmful' or 'helpful' traits" — the delta versus existing red-team/eval suites is black-box, behavior-only measurement under dynamic information.
EXPERIMENT:    [INFERRED] Run Magentic Marketplace (or a minimal double-auction) with 3–4 open-weight and API LLM agents plus a scripted rational bidder, inject a "news feed" shock, and check whether (a) allocative efficiency reaches ~90% and (b) a simple classifier separates agent types from bid streams — this is the Month-2 milestone in miniature.
REUSE:         [INFERRED] Backend simulation, ML classifiers, LLM orchestration — near-total reuse.
DUAL USE:      [TOPIC TEXT] "AI firms have strong market demand for the capability to benchmark the influence of their systems" (liability/reputational risk).
DIFFERENTIATOR:[INFERRED] Pure software, open-source seed, fixed monthly milestones — the best-defined and lowest-friction fit in either release for this team.
CONFIDENCE:    HIGH. Would raise by confirming Magentic Marketplace's license and how much of the Month-2 mechanics it already provides.
```

---

## 11

```
TOPIC:        OSW26BZ06-DV025 — Compact Passive Radar
BRANCH:       OSD (Reliance 21)   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study + (c) benchtop-sourceable lab prototype — [TOPIC TEXT] "The desired end product is a robust simulation and a basic laboratory prototype that validates the feasibility of detecting targets using signals of opportunity while strictly adhering to the SWaP-C metrics"; "developing proof-of-concept signal processing algorithms for reference signal isolation, clutter cancellation, and target detection and/or tracking"
FLAGS:         T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Detect and track aircraft or vehicles using only other people's radio/TV/cell signals bouncing off them — with a receiver small and cheap enough to throw away on a small drone.
GAPS:
- [INFERRED] RF/radar signal-processing expertise (bistatic geometry, clutter cancellation, cross-ambiguity processing).
- [INFERRED] Phase II requires a miniaturized X-band multi-channel receiver and outdoor demonstration — hardware engineering beyond benchtop.
- [TOPIC TEXT] X-band illuminators of opportunity are scarce; the topic's SAR/GMTI at X-band is a much harder ask than the FM/DVB-T passive radar demonstrated by hobbyists.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Passive bistatic radar is a mature academic field; multi-channel COTS SDRs (KrakenSDR-class, USRP) have public passive-radar demos, so a Phase I lab prototype is credible. Incumbents are ESM/SIGINT houses the topic itself criticizes as "bulky, expensive."
DELTA:         [INFERRED] Attritable SWaP-C, X-band, and SAR/GMTI products versus academic FM-band detection demos.
EXPERIMENT:    [INFERRED] With a 4-channel COTS SDR and a public passive-radar toolchain, detect a cooperative moving target using a local broadcast illuminator, then measure processing load to size the edge-compute budget — establishes the algorithm chain before any custom hardware.
REUSE:         [INFERRED] Signal-processing and edge-compute software; no RF hardware reuse (cf. Release 5 #7, #28 overlap).
DUAL USE:      [TOPIC TEXT] "low-cost air traffic monitoring, counter-UAS (cUAS) surveillance for critical infrastructure, and general airspace monitoring."
DIFFERENTIATOR:[INFERRED] Software-defined approach on COTS SDR lowers unit cost, which is the topic's central metric; Phase II hardware would need a partner.
CONFIDENCE:    LOW-MEDIUM. The X-band/SAR requirement may exceed what signals of opportunity support; would raise after a short literature check on X-band illuminators.
```

---

## 12

```
TOPIC:        OSW26BZ06-NV024 — Engineered Microstructures for Enhanced IR Aperture Performance
BRANCH:       OSD (Reliance 21)   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "demonstrate the potential to produce the target IR-transparent composite ceramic with sub-100 nm microstructural features in all phases and porosity below 0.1%"
KILL REASON:   [TOPIC TEXT] Ceramic materials synthesis and processing — no materials lab.
KILL CLASS:    PERMANENT
FLAGS:         T0.1 D2P2 also accepted | T0.4 Registration check

PLAIN PROBLEM: Make a new see-through-to-infrared ceramic for missile domes that survives 1200°C.
GAPS:
- [TOPIC TEXT] Ceramic processing and characterization facilities.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 13

```
TOPIC:        OSW26BZ06-NV026 — Defect Metrology and Charge Trapping Dynamics in Transfer-Doped Diamond Transistors
BRANCH:       OSD (Reliance 21)   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (a) 6-month study leading to (c) — [TOPIC TEXT] "Conduct a 6-month study to establish the scientific and technical feasibility of the proposed defect metrology technique... describe the hardware equipment requirement needed to perform the measurement... preliminary experimental demonstrations"
KILL REASON:   [INFERRED] Semiconductor device physics and cryogenic/optical characterization of diamond transistors — no lab, no domain expertise.
KILL CLASS:    PERMANENT
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Invent a non-destructive way to find and characterize the defects that make diamond transistors lose current.
GAPS:
- [INFERRED] Semiconductor characterization lab and diamond-device samples.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 14

```
TOPIC:        OSW26BZ06-NV028 — 5G Signature Tracking Mitigation via Cyber Deception
BRANCH:       OSD (FutureG)   PROGRAM: SBIR   CLOSES: October 21, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a)/(b) concept design, feasibility study, design document — [TOPIC TEXT] "proposers are required to present a comprehensive concept design and feasibility study for a digital exhaust deception system. Solutions should outline the proprietary software required to conduct AI-enabled mission planning and operations"; Phase I deliverables: "Preliminary Design Document detailing AI-persona generation and ID-swapping mechanics"
FLAGS:         T0.3 ITAR | T0.4 Registration check | CMMC Level 2 (Self)

PLAIN PROBLEM: Build software (and later a small decoy device) that generates fake but realistic cell-phone activity so an adversary watching a foreign mobile network can't work out where a unit is or what it's about to do.
GAPS:
- [INFERRED] Cellular protocol / SIM-identity engineering (ID-swapping mechanics, IMSI/IMEI behaviour) and the legal envelope for operating decoy identities on third-party networks.
- [INFERRED] Phase II hardware ("puck-sized personal devices", 12–36 h battery) — COTS modems/SBCs are benchtop-sourceable, but ruggedization is not core competence.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Commercial adjacent tech: privacy VPN/eSIM products and honeypot/deception platforms for enterprise networks; nothing commercial generates AI pattern-of-life decoys on cellular metadata.
DELTA:         [TOPIC TEXT] The KPMs — "AI-powered personas broadcasted simultaneously per decoy device" and "Defeats advanced ML-based behavioral tracking" — are the delta: generative pattern-of-life traffic rather than mere encryption/anonymization.
EXPERIMENT:    [INFERRED] Train a generative model on a public mobility/CDR-style dataset (e.g., open GPS-trajectory datasets), synthesize decoy personas, and test whether a standard pattern-of-life classifier can distinguish real from synthetic traces — a direct test of the "obfuscation realism" KPM without touching a live network.
REUSE:         [INFERRED] ML (generative sequence models, anomaly detection) and backend orchestration — strong; the RF/cellular device layer is not reusable.
DUAL USE:      [TOPIC TEXT] "protecting high-value corporate assets, personnel, and intellectual property from commercial espionage and tracking."
DIFFERENTIATOR:[INFERRED] The hard part is realism against ML trackers — an ML problem — not radios; a software team can lead and sub out the device.
CONFIDENCE:    MEDIUM. Would raise with a cellular-protocol partner and a read of the cited DoDI 8520.02 for operating constraints.
```

---

## 15

```
TOPIC:        OSW26TZ06-NV004 — Telecom Band Geometric Amplifier
BRANCH:       OSD (Basic Research)   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (a) design/simulation — [TOPIC TEXT] "Produce a complete design for a prototype telecom-band geometric amplifier based entirely on commercial off-the-shelf components. The design should be based on quantitative simulations"
KILL REASON:   [INFERRED] Phase I is simulation-only, but it is a Berry-phase optical-physics design task; without a photonics RI partner leading, the team cannot produce a credible design, and Phase II is an optical bench build.
KILL CLASS:    CONTINGENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Design a laser amplifier that uses a geometric-phase trick instead of gain media.
GAPS:
- [INFERRED] Optical-physics domain SMEs; Phase II optics lab.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH. Re-open only if a photonics RI wants a software/simulation partner.
```

---

## 16–20

```
TOPIC:        OSW26TZ06-NV005 — Ultrafast Nonvolatile Memory Based on Sliding Ferroelectricity in Moiré Polar Homostructures
BRANCH:       OSD   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1
DELIVERABLE:   (c) — [TOPIC TEXT] "nanostructured polar moiré superlattice fabrication... readout schemes using graphene field-effect transistors"
KILL REASON:   [TOPIC TEXT] 2D-material nanofabrication and device characterization — no fab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check
CONFIDENCE:    HIGH
```

```
TOPIC:        OSW26TZ06-NV006 — Room Temperature THz and Infrared Sensing Devices Using Non-Toxic, Supply-Chain Secure Material Platform
BRANCH:       OSD   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1
DELIVERABLE:   (c) — [TOPIC TEXT] "Synthesis of oxychalcogenide thin film materials... demonstration of direct absorption in the LWIR and antenna-coupled rectification at THz frequencies"
KILL REASON:   [TOPIC TEXT] Thin-film materials synthesis and THz/IR device measurement — no lab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check
CONFIDENCE:    HIGH
```

```
TOPIC:        OSW26TZ06-NV007 — Scalable Processing of Large Area, Oriented 2-Dimensional Polymer Films
BRANCH:       OSD   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1
DELIVERABLE:   (c) — [TOPIC TEXT] "Develop a continuous process to produce 2DP ensemble films... 100 feet per minute of a film that is at least 1 foot wide"
KILL REASON:   [TOPIC TEXT] Polymer chemistry and roll-to-roll film processing — no lab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check
CONFIDENCE:    HIGH
```

```
TOPIC:        OSW26TZ06-NV009 — Expeditionary Solar Refinery for Direct Synthesis of Methanol Feedstock from Water and Air
BRANCH:       OSD   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1
DELIVERABLE:   (c) — [TOPIC TEXT] "Feasibility will be established by light harvesting toward methanol synthesis (catalytic or otherwise) and kinetics/turnover/selectivity evaluation"
KILL REASON:   [TOPIC TEXT] Photocatalysis chemistry and reactor engineering — no lab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check
CONFIDENCE:    HIGH
```

```
TOPIC:        OSW26TZ06-NV010 — Architected Energy Dissipation Structures With Tunable Rigid-Flexible Behaviors
BRANCH:       OSD   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1
DELIVERABLE:   (c) — [TOPIC TEXT] "Design architected structures with individual linked grains in the following approximate rectangular configuration, 82 mm x 87 mm x 19.5 mm" with measured "through-thickness compression response"
KILL REASON:   [TOPIC TEXT] Mechanical-metamaterial fabrication and impact testing — no lab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check
CONFIDENCE:    HIGH
```

---

## 21

```
TOPIC:        OSW26TZ06-NV008 — Bio-inspired Underwater Teams
BRANCH:       OSD (Basic Research)   PROGRAM: STTR   CLOSES: October 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (a)/(c) — [TOPIC TEXT] "demonstrate the feasibility of the concept... via model-scale experiments, computation, previous results and data, or fabrication of components"; Phase II: "fabricate a prototype team of UUVs... in-water tests"
KILL REASON:   [TOPIC TEXT] Phase II requires fabricating 1–5 m untethered underwater vehicles with novel bio-inspired propulsors and running in-water speed/acoustic trials — vehicle hardware and test facilities far beyond benchtop scale. Phase I CFD alone would not be credible without a vehicle-design partner.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Design a school of fish-like robot submarines that swim faster and quieter by drafting off each other's wakes.
GAPS:
- [TOPIC TEXT] UUV fabrication and in-water test facility.
- [INFERRED] Hydrodynamics/CFD and marine-vehicle design expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## D2P2-only topics in Release 6 (not triaged — need prior Phase-I-equivalent work)

Logged because several are software-shaped and the "Phase I-type" evidence bar was clarified in Q&A; worth a look if the team ever has a fielded prototype to point at.

| Topic | Title | Why it's interesting | Bar |
|---|---|---|---|
| DAF26BX06-DV513 | Autonomous On Orbit Logistics and Sustainment Architecture | [Q&A] ~20 awards targeted; software-centric systems-of-systems explicitly asked about (answers pending); DAF/USSF stakeholder engagement "with other DAF/USSF organizations" suffices | prior validated architecture |
| DAF26BX06-DV512 | Cyberspace Warfare for Space | Focus Area 5 (adaptive data parsers / normalization engine) and 8 (portable DCO kit) are pure software; [Q&A] "prior evaluation or demonstration with an identified USAF/USSF stakeholder is not required" | test results on representative formats |
| OSW26BZ06-DV034 | VLM for SAR target search and classification (SICD) | Public SAR data exists; [TOPIC TEXT] requires ">95% accuracy... single SAR image chips in SICD format" and PhD-level SAR expertise | existing classifier + SAR SME |
| DPA26BZ06-DV027 | Casualty Operations & Resource Prediction Software (CORPS) | Pure software; feasibility may be "conceptual characterization... use cases... proposed approach" — a low bar | conceptual package |
| OSW26BZ06-DV033 | Agentic AI Cognitive Radar for GEOINT | Software + radar; needs demonstrated interference mitigation | working demo |
| DAF26TZ06-DV008 | Counter Adversarial GPS Jamming (STTR) | ML + stochastic resonance; algorithmic | prior concept + results |
| OSW26BZ06-DV031/DV032 | Open-source private 5G (venues / manufacturing) | Open-source stack integration | mature prototype |
| DAF26BX06-DP027 | Proliferated Low-Altitude C-sUAS Detection | Sensor hardware + software | working sensor prototype |

Remaining D2P2-only (hardware/medical): DAF26BX06-DV026, DV511, DAF26BZ06-DV037, DON26BZ06-DV088, DPA26BZ06-DV023, DV024, DV029, DPA26TZ06-DV004, DV005, DV006, OSW26BZ06-DV027, SOC26BZ06-DV006.
