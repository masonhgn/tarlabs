# SBIR/STTR Topic Triage — Results

Source: `stage0_survivors.csv` (87 Stage 0 survivors out of 335 raw topics — see `stage0_screen.py`).
Method: `sbir-topic-triage.md`. Stages 1–3 applied to each survivor below, in CSV order.
No live web/database searches were run for Stage 2 (per instruction) — landscape claims are `[INFERRED]` from general knowledge or marked `UNKNOWN`, never `[SEARCHED]` unless a search was actually performed.

## Addendum 2026-09-20 — corrections from the DSIP Q&A (`sitis_qa.md`)

- **Facility-clearance kills are CONTINGENT, not PERMANENT.** [Q&A, DON26BZ05-NV077, NAVAIR] "A Secret-level Facility Clearance (FCL) is not required at Phase I award. Uncleared small businesses with a credible sponsorship path are viable offerors. FCL sponsorship and processing will be initiated during Phase I if required for Phase II transition." Applies to #2 NV074, #14 NV069, #15 NV072, #18 NV080, #25 NP003, #39 NV070, #41 NV077. The "no foreign influence" (US-owned) condition still applies, and Phase II would require the clearance — a business decision, not a structural bar. Of these, #2 (CCA post-mission re-planning, 16 published questions) and #25 (AEGIS MBSE ingestion, 35 questions) are software-shaped and would be worth re-reading if the team is willing to pursue FCL sponsorship.
- **#41 NV077 specifics** [Q&A]: synthetic 2–3-sensor scenarios acceptable; desktop simulation acceptable for Phase I; performer picks off-the-shelf CPU/GPU/FPGA; success = latency/throughput/track-loss vs. a single-threaded baseline. That is a pure software Phase I.
- **#6 DV031 (F-16 OSE)** [Q&A]: "SPO will continue to own airworthiness and cyber approvals"; "both SIL and lab environments are available"; the intent is "artifact generation as part of an integration partnership." The kill reason (no platform access) was overstated; the accurate reason is posture — this is an integration-partner role, not a small-team prime. Verdict stands, class PERMANENT → CONTINGENT.
- **Stage 0 D2P2 rule was corrected** (`stage0_screen.py`); re-running on this CSV changed nothing here, but it mattered for Release 6 (see `release6_triage.md`).
- **Unread Q&A:** 35 topics with published questions were not expanded in the saved SITIS page, including every PURSUE topic in this file (#7 NV017 12 Qs, #8 NV078 37, #26 NP004 24, #28 DV020 6, #30 NV071 7, #37 DV018 21, #38 NV068 12, #1 DV019 39, #16 NV073 7, #36 NV016 7, #29 NP001 8, #4 NV027 9). These close 2026-09-23.

---

## 1

```
TOPIC:        OSW26BZ05-DV019 — Collaborative Distributed Swarm Radar
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms/simulation — [TOPIC TEXT] "study hardware architectures and develop algorithms to simulate networked sensor configurations"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Coordinate multiple separate sensors to act as a single, higher-resolution radar system for tracking ground or maritime objects.
GAPS:
- [INFERRED] Access to military-grade radar RF signature data.
- [TOPIC TEXT] Phase II requires UAS surrogates carrying physical radar modules.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Commercial SOTA is distributed acoustic sensing and drone mapping; commercial networked radar is nascent.
DELTA:         [INFERRED] Defense requires target tracking in contested RF environments rather than static terrain mapping.
EXPERIMENT:    [INFERRED] Attempt to time-synchronize two COTS mmWave radar boards using public dataset algorithms to measure collaborative beamforming gain.
REUSE:         [INFERRED] Data pipelines, ML for signal processing, and backend infrastructure for simulation.
DUAL USE:      [TOPIC TEXT] Civilian environmental monitoring, surveillance, and emergency response.
DIFFERENTIATOR:[INFERRED] A software-first approach allows faster iteration on synchronization and data-fusion algorithms compared to legacy hardware primes.
CONFIDENCE:    MEDIUM. Would raise if a public dataset of distributed radar signatures exists for algorithm training.
```

---

## 2

```
TOPIC:        DON26BZ05-NV074 — Automated Post-Mission De-Brief and Re-Planning for Collaborative Combat Aircraft (CCA) Missions
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "develop algorithms and tools to analyze mission data... and generate explainable recommendations"
KILL REASON:   [TOPIC TEXT] "contractor and/or subcontractor must be able to acquire and maintain a secret level facility"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Automate the analysis of drone combat mission data to rapidly generate new mission plans for subsequent engagements.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [TOPIC TEXT] Access to classified information on adversary tactics and threat profiles.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 3

```
TOPIC:        DAF26BZ05-NV026 — Automated Lethality
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      HOLD
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "develop a full software stack to create a small footprint lethality software tool for embedded applications"
FLAGS:         T0.4 Registration check | [INFERRED] Likely export-controlled/ITAR in practice despite no literal flag term in text

PLAIN PROBLEM: Given imagery of a structure, automatically build a 3D model of it, estimate what it would take to destroy it, and pick the best way to attack it, fast enough to run on embedded hardware.
GAPS:
- [INFERRED] Reference weaponeering/probability-of-kill (Pk) data (e.g., JMEM-class munitions effectiveness manuals) are normally restricted/FOUO.
- [INFERRED] Domain SMEs in weaponeering methodology, which the team lacks.
- [TOPIC TEXT] Embedded, real-time deployment constraint ("small footprint," "embedded in hardware").
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Likely tied to ongoing JMEM/weaponeering-tool modernization; incumbents are likely munitions-effectiveness labs/primes with existing Pk data access. Realistic posture: sub or displacement on the imagery/structure-modeling slice, not prime.
DELTA:         [INFERRED] Commercial computer-vision "structure from imagery" (construction digital twins, insurance catastrophe modeling) already exists; the defense-specific delta is entirely the Pk/lethality layer, which sits behind a data wall.
EXPERIMENT:    [INFERRED] Fine-tune a public building/structure classification CV model (e.g., on aerial/overhead imagery datasets) to classify structure type and material, and check whether outputs are granular enough to feed a public structural-engineering vulnerability heuristic.
REUSE:         [INFERRED] Existing ML pipelines for image classification and backend infra for simulation.
DUAL USE:      [INFERRED] Structural digital-twin generation from imagery has a civilian market (insurance, construction, disaster response) without the lethality layer.
DIFFERENTIATOR:[INFERRED] A software/ML-first pipeline could outpace legacy static-lookup-table weaponeering tools, contingent on eventually teaming for Pk data access.
CONFIDENCE:    LOW-MEDIUM. Would raise if any unclassified/FOUO-lite weaponeering reference dataset exists that Phase I could use without a cleared partner.
```

---

## 4

```
TOPIC:        DAF26BZ05-NV027 — Integrating Neural Architectures for Brain-Inspired AI with Low SWAP
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms — [TOPIC TEXT] "developing innovative methodologies for... seamlessly interconnecting diverse neural modules"; no physical article required, unstated hardware but framed as research/architecture proposal
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Combine several different types of neural network (CNN, RNN, transformer, spiking net) into one system that shares compute efficiently and uses less power than running them separately.
GAPS:
- [INFERRED] Access to neuromorphic/spiking-neural-network hardware (e.g., Loihi, BrainScaleS) for low-SWAP validation — likely simulatable without it for Phase I.
- [INFERRED] Domain expertise in computational neuroscience/neocortex modeling to ground the "brain-inspired" framing credibly.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Commercial SOTA includes mixture-of-experts (MoE) architectures and heterogeneous multi-model systems (e.g., routing between specialized sub-models), which is conceptually close to what's asked.
DELTA:         [INFERRED] Defense angle is the low-SWAP/embedded constraint and multi-modal battlefield sensor fusion, versus commercial MoE which optimizes for cloud-scale throughput/cost, not power envelope.
EXPERIMENT:    [INFERRED] Build a small heterogeneous model (e.g., CNN + small transformer with a learned gating/routing layer) on public multi-modal data and measure whether dynamic compute allocation reduces FLOPs/power versus a monolithic baseline at matched accuracy.
REUSE:         [INFERRED] Existing ML engineering skills (model training, routing/gating logic) map directly onto this; no defense-specific reuse needed.
DUAL USE:      [INFERRED] Efficient heterogeneous inference architectures are broadly valuable for on-device/edge AI (mobile, robotics, IoT) — a clear non-government market.
DIFFERENTIATOR:[INFERRED] A small software team unencumbered by legacy monolithic-model infrastructure can iterate faster on novel routing/gating architectures than large incumbents invested in single-architecture scaling.
CONFIDENCE:    MEDIUM. Would raise with a concrete target platform/SWAP budget from the topic (none given) to bound feasibility.
```

---

## 5

```
TOPIC:        DAF26BZ05-DV030 — High Temp Semiconductor Transistors for Hot DoW Environments and Electronic Warfare
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "design, develop, and experimentally demonstrate transistors" including "device fabrication, and device characterization" via "cross-sectional SEM imaging, spatially resolved energy dispersive X-ray spectroscopy"
KILL REASON:   [TOPIC TEXT] Requires semiconductor "device fabrication" and characterization via SEM/EDX — a wafer fab and materials-characterization lab, not benchtop-sourceable.
KILL CLASS:    PERMANENT
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build transistors that keep working at extreme heat (500°C+) for radar/electronic-warfare electronics.
GAPS:
- [TOPIC TEXT] Semiconductor device fabrication capability (wafer-scale process).
- [TOPIC TEXT] Materials characterization equipment (SEM, EDX).
- [INFERRED] Wide-bandgap/high-temp materials science domain expertise (SiC, GaN, or diamond-based devices).
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 6

```
TOPIC:        DAF26BZ05-DV031 — F-16 Agnostic Rapid Weapons Integration
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c)-adjacent / unstated — [TOPIC TEXT] "develop a modular and scalable weapons integration architecture, developed on the Open Systems Enclave (OSE) system" for the "F-16... FY26 Air Reserve Component Modernization Book"
KILL REASON:   [INFERRED] Requires integration onto the Open Systems Enclave / F-16 avionics stack, which is proprietary, aircraft-specific, and inaccessible without prime/platform-owner access (no public spec, no test aircraft, no OSE dev environment available commercially).
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a plug-and-play architecture so new weapons can be added to an F-16 in weeks instead of years.
GAPS:
- [INFERRED] Access to F-16 OSE (Open Systems Enclave) hardware/software development environment, which is government/platform-owner controlled.
- [INFERRED] Airworthiness and munitions-integration domain expertise, plus a certification pathway the team has no standing to pursue independently.
- [INFERRED] Relationships with FAMM (Family of Affordable Mass Munitions) program stakeholders.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    MEDIUM. Would raise if OSE has an open/simulated dev kit reachable without a facility clearance or platform-owner relationship — topic text doesn't say either way.
```

---

## 7

```
TOPIC:        OSW26BZ05-NV017 — Sensing Algorithms for Bandwidth Efficient Edge Radars (SABER)
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms — [TOPIC TEXT] "seeks solutions that jointly optimize communications and target inference in a decentralized radar sensing framework"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Decide how much raw sensor data each node in a distributed radar network should process locally versus send over the network, to get the best target-detection accuracy for the least bandwidth.
GAPS:
- [INFERRED] Real radar RF datasets from distributed/networked sensor arrays (likely military-specific, e.g., DMO-relevant scenarios).
- [INFERRED] Domain expertise in radar signal processing and communications-theory co-design (rate-distortion tradeoffs for sensing).
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Overlaps conceptually with commercial "split computing" / edge-cloud inference research (where to place compute in a pipeline to save bandwidth), which is an active academic and industry area (e.g., camera networks, IoT).
DELTA:         [INFERRED] Defense specificity is radar-domain (RF, not vision) and adversarial/contested-RF operation, versus commercial split-computing which assumes benign networks.
EXPERIMENT:    [INFERRED] Using a public radar dataset (e.g., RadarScenes, CARRADA) or synthetic simulated RF returns, compare detection accuracy at multiple compression points (raw IQ vs. features vs. detections-only) to characterize the accuracy-vs-bandwidth curve, which is the topic's core claim.
REUSE:         [INFERRED] Signal-processing and ML pipeline experience; existing data pipeline/backend infrastructure.
DUAL USE:      [INFERRED] Bandwidth-efficient distributed sensing has civilian applications in smart-city sensor networks and environmental monitoring, though not stated in topic text.
DIFFERENTIATOR:[INFERRED] Software-first algorithmic focus (no radar hardware required for Phase I) plays to the team's strengths versus hardware-heavy incumbents.
CONFIDENCE:    MEDIUM. Would raise if a suitable public/synthetic multi-node radar dataset is confirmed to exist.
```

---

## 8

```
TOPIC:        DON26BZ05-NV078 — Tech Data Interactive Electronic Technical Manuals Convertor
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "develop a tool or software that can automate the transformation of these diverse technical manuals into eXtensible Markup Language (XML)"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a converter that ingests old technical manuals in various formats (PDF, various MIL-STDs, S1000D) and outputs standardized XML that a step-by-step AR/tablet instruction viewer can consume.
GAPS:
- [TOPIC TEXT] Sample Navy technical manuals in the named legacy formats (MIL-STD-3001-1, MIL-DTL-81310, S1000D v3.0/v4.0) — likely government-furnished and not publicly available in bulk.
- [INFERRED] Familiarity with DFARS data-rights marking rules to correctly propagate distribution statements.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Commercial SOTA: document-conversion/OCR and structured-authoring tools (e.g., PDF-to-XML pipelines, S1000D authoring/CSDB tools like Adobe FrameMaker+S1000D plugins) already exist for the commercial aerospace/defense tech-pubs industry.
DELTA:         [INFERRED] Defense-specific delta is handling the mix of legacy, non-uniform government formats plus DFARS marking propagation and AR/XR display integration, not the base PDF/XML conversion.
EXPERIMENT:    [INFERRED] Take a public S1000D sample dataset (S1000D publishes public specification examples) plus a scanned/PDF manual, and build a prototype parser that extracts structured step content into XML, to test format-diversity handling before any government data is available.
REUSE:         [INFERRED] Document parsing, ETL pipelines, and structured-data extraction — directly in a backend/data team's wheelhouse.
DUAL USE:      [INFERRED] Legacy-document-to-structured-format conversion (for AR-assisted maintenance) is broadly valuable in industrial/commercial equipment maintenance (aviation MRO, manufacturing), though not stated in topic text.
DIFFERENTIATOR:[INFERRED] A data-pipeline-focused team is well suited to the parsing/normalization core of this problem, which is software engineering rather than domain-specialist work.
CONFIDENCE:    MEDIUM. Would raise if public S1000D/MIL-STD sample manuals are confirmed sufficient to prototype against before Phase I data delivery.
```

---

## 9

```
TOPIC:        DME26BZ05-NV001 — Additive Manufacturing for Flexible Electronics
BRANCH:       DMEA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "DoW is seeking the feasibility of developing a prototype via this effort directly comparable to existing Radio Frequency multichip modules (MCMs)" using additive-manufactured substrates and "obtaining reliability data using MIL-STD quality and reliability metrics"
KILL REASON:   [TOPIC TEXT] Requires physical fabrication and MIL-STD reliability testing of RF multichip-module prototypes using specialized additive-manufacturing/advanced-packaging equipment (vat photopolymerization, aerosol jet printing) the team does not have benchtop access to.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Prove that 3D-printed circuit substrates and interconnects can match the reliability of traditionally manufactured RF circuit boards.
GAPS:
- [TOPIC TEXT] Specialized additive-manufacturing/advanced-packaging equipment (ceramic vat photopolymerization, aerosol jet nanoparticle-ink printing).
- [INFERRED] MIL-STD reliability test lab access (thermal cycling, environmental stress screening).
- [INFERRED] RF/microelectronics packaging domain expertise.
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
TOPIC:        DAF26TZ05-NV005 — Real Time Enhanced Fine Tracking in Directed Energy Applications
BRANCH:       USAF   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      HOLD
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms (Phase I), (c) physical article (Phase II) — [TOPIC TEXT] "Phase I effort will design the 3D measurement technique, corresponding algorithms, and a concept for the integrated hardware"; Phase II is "a prototype demonstration system... deploy such algorithms onto high-speed processors and integrate with hardware"
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Build a fast, accurate way to track a drone's 3D position and orientation using 3D imaging (not just a flat 2D picture), so a directed-energy weapon can keep its aimpoint locked despite atmospheric distortion.
GAPS:
- [INFERRED] Access to digital-holography or coherent 3D-imaging hardware for empirical validation (Phase I is algorithm/simulation-only per topic text, so this may be deferrable).
- [INFERRED] Domain expertise in aero-optics/atmospheric turbulence compensation and directed-energy fine-tracking systems.
- [TOPIC TEXT] STTR structure requires a research-institution partner at ≥30% of the work — team would need to identify and onboard one (likely a university optics/EE lab).
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Digital holography and computational imaging for turbulence compensation is an active academic research area (adaptive optics, phase retrieval); DE-specific fine-tracking integration is a narrower, defense-specific niche likely held by DE program incumbents (e.g., national labs, DE primes).
DELTA:         [INFERRED] Commercial/academic 3D imaging and turbulence-compensation algorithms exist broadly; the defense delta is the >1kHz real-time closed-loop constraint plus non-cooperative extended-target tracking against cluttered backgrounds specific to a weapon aimpoint-maintenance loop.
EXPERIMENT:    [TOPIC TEXT]-adjacent [INFERRED]: implement a published physics-based or ML-based anisoplanatic image-restoration algorithm on public turbulence-degraded imagery datasets (several exist in the adaptive-optics/computational-imaging literature) and benchmark restoration quality and processing latency against the >1kHz throughput requirement.
REUSE:         [INFERRED] ML/signal-processing pipeline experience for the image-restoration and tracking-algorithm software; no existing optics hardware reuse.
DUAL USE:      [INFERRED] Real-time atmospheric-turbulence compensation has civilian applications in free-space optical communications and long-range surveillance/imaging, though not stated in topic text.
DIFFERENTIATOR:[INFERRED] A software/algorithms-first team can prototype and benchmark the processing pipeline on public data before any hardware integration, de-risking the STTR partnership's contribution to the hardware-heavy Phase II.
CONFIDENCE:    LOW-MEDIUM. Would raise if a suitable research-institution optics partner is identified and if a public coherent-3D-imaging/turbulence dataset is confirmed to exist for the decisive experiment.
```

---

## 11

```
TOPIC:        OSW26BZ05-DV023 — Quantum Sensor Gravity Data Production & Analysis for Maritime Floor Mapping
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms — [TOPIC TEXT] "this topic does not involve sensor development"; proposers "describe the quantum sensor(s) to be evaluated, the simulation framework (path integral methods, Monte Carlo), and how real sensor data will be collected, processed into bathymetric products, and validated"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Figure out, mostly through simulation, whether existing quantum gravity sensors could map the ocean floor from a submarine as well as or better than today's sonar/satellite methods.
GAPS:
- [TOPIC TEXT] Access to an actual quantum gradiometer (cold-atom interferometry sensor) to "collect real sensor data" — these are few, expensive, and specialized (not something bought off the shelf casually).
- [INFERRED] Domain expertise in geodesy/gravimetry and submarine-platform sensor integration.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Quantum gravimeters are already commercial products (used in oil/gas exploration and geodesy, e.g., cold-atom gravimeter vendors); incumbents on the defense side are likely those same sensor makers plus GEOINT/bathymetry integrators.
DELTA:         [INFERRED] Defense-specific delta is submarine-platform deployment and integration with NGA GEOINT foundation-data standards, versus stationary/airborne commercial gravimetry.
EXPERIMENT:    [TOPIC TEXT]-permitted [INFERRED]: using publicly available vendor-published sensor noise/sensitivity specs plus public bathymetric datasets (NOAA multibeam echosounder data) and public SWOT satellite altimetry data, build the Monte Carlo/path-integral simulation the topic explicitly allows, and estimate achievable bathymetric resolution without ever needing physical sensor access.
REUSE:         [INFERRED] Existing simulation, data-pipeline, and ML infrastructure transfers directly to building the Monte Carlo/path-integral analysis framework.
DUAL USE:      [INFERRED] Quantum gravimetry already has a civilian market in oil/gas exploration, mining, and geodesy — an existing non-government customer base.
DIFFERENTIATOR:[INFERRED] A simulation-first approach lets the team demonstrate predicted value before needing to secure expensive sensor hardware access, which the topic text itself treats as optional/deferrable.
CONFIDENCE:    MEDIUM. Would raise if public vendor spec sheets for quantum gradiometers are confirmed detailed enough to support a credible simulation.
```

---

## 12

```
TOPIC:        OSW26BZ05-DV014 — In-Situ Metrology for Mesa-Wall Integrity in Large Format Small-Pixel Infrared Detector Array Fabrication
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article/instrument — [TOPIC TEXT] "Proposed solutions must be capable of non-destructively evaluating the integrity of small-pixel mesa-walls by measuring surface current... System should allow measurements of up to 150 mm diameter wafers"
KILL REASON:   [TOPIC TEXT] Requires an in-situ cryogenic metrology instrument operating directly in a T2SL/MCT infrared-detector wafer fabrication line — no fab access, no cryogenic semiconductor test equipment, no III-V/MCT material samples.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build an instrument that can check, without damaging them, whether the tiny walls between pixels on an infrared camera chip are defect-free, while the chip is still cold and mid-fabrication.
GAPS:
- [TOPIC TEXT] Access to Sb-based III-V T2SL / MCT detector wafers and a fabrication line.
- [INFERRED] Cryogenic test equipment and semiconductor-metrology domain expertise.
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
TOPIC:        OSW26BZ05-NV021 — Co-packaging Digital Readout Integrated Circuits and Photonics for Advanced Infrared Imaging
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "demonstrate a tri-service ready capability to either completely integrate electronics and photonics on a single silicon wafer, or perform foundry-level integration"; "demonstrate high-speed, ultra-low-power optical channel operations within cryogenic environments"
KILL REASON:   [TOPIC TEXT] Requires CMOS/PIC foundry tape-out and cryogenic ROIC test/characterization — foundry access and cryogenic photonics test infrastructure the team does not have.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a camera chip readout circuit that sends its data out using light instead of electrical wires, fast and at very low power, while running at cryogenic temperatures.
GAPS:
- [TOPIC TEXT] CMOS/photonic-integrated-circuit foundry access.
- [INFERRED] Cryogenic test setup and ROIC/photonics design expertise.
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
TOPIC:        DON26BZ05-NV069 — Wearable Real-Time Command-and-Control Interface for Enhanced Naval Situational Awareness
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "develop, demonstrate, and deliver a production-ready, wearable, real-time C2 interface utilizing MR technology"
KILL REASON:   [TOPIC TEXT] "The selected contractor and/or subcontractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 ITAR | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Build a rugged, mixed-reality headset system that fuses live sensor/intel data for sailors, tough enough for shipboard/maritime conditions.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [TOPIC TEXT] MIL-STD-810/1472/1425 compliance testing and maritime environmental qualification lab access.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 15

```
TOPIC:        DON26BZ05-NV072 — Digitally Enhanced Weapon System Technical Data
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b) software/service — [TOPIC TEXT] "design, develop, and demonstrate a solution capable of rapidly delivering digitally enhanced weapon system technical data within 24 hours"
KILL REASON:   [TOPIC TEXT] "The selected contractor and/or subcontractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Turn raw maintenance fixes into polished training videos/interactive animations and push them to fleet technicians within a day.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [TOPIC TEXT] Access to the Navy's All Weapon Information System (AWIS) Repository and classified technical data.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 16

```
TOPIC:        DON26BZ05-NV073 — Portable Digital Metrology System for Measurement of Defects on Optically Transparent Canopies and Windscreens
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (c) physical article (benchtop-sourceable) — [TOPIC TEXT] "Candidate measurement concepts shall be executable on aircraft and capable of performing defect measurements (e.g., scratch defect with length 1”, width << 0.125”, and approx. depth of 0.100”) on optically transparent materials"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a handheld device that measures the length, width, and depth of scratches and pits on curved, clear aircraft canopies while still mounted on the aircraft, without needing removal.
GAPS:
- [INFERRED] Access to real damaged canopies/windscreens with known ground-truth defect dimensions for calibration (substitutable with synthetic scratches machined into scrap acrylic).
- [INFERRED] Access to the actual repair-limit specification thresholds (likely a restricted NAVAIR document), though the topic text already gives representative defect dimensions to design around.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Handheld laser-triangulation and structured-light profilometers are widely commercial for opaque-surface defect inspection (automotive, aerospace MRO), e.g., dent/paint-chip scanners.
DELTA:         [INFERRED] Existing commercial profilometers are built for opaque surfaces; reliably measuring sub-0.1" depth features on/in a transparent, curved acrylic surface is a materially harder optical problem and is the genuine defense-specific (and Navy-canopy-specific) delta.
EXPERIMENT:    [INFERRED] Buy a COTS structured-light or confocal-chromatic sensor, machine known-dimension scratches/pits into a scrap acrylic sheet, and measure detection accuracy against calipers/ground truth.
REUSE:         [INFERRED] Signal-processing and calibration software experience; no existing optical hardware.
DUAL USE:      [INFERRED] Transparent-surface optical defect metrology has civilian markets in automotive windshields, commercial aviation canopies, and optics manufacturing QA.
DIFFERENTIATOR:[INFERRED] Focus on the transparent-material-specific optical/software calibration problem that opaque-surface-focused incumbents haven't solved.
CONFIDENCE:    MEDIUM. Would raise with confirmation that a COTS confocal-chromatic or structured-light sensor has sufficient resolution for ~0.1" depth features on acrylic.
```

---

## 17

```
TOPIC:        DON26BZ05-NV076 — Open, Layered, Yielding Modular Platform for Unified Systems
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b)/(d) architecture & software — [TOPIC TEXT] "PMA-213 is developing a portfolio-wide architecture, referred to as Zeus... OLYMPUS is a sub-project of Zeus focusing on the below deck ship infrastructure"
KILL REASON:   [TOPIC TEXT] "With government ownership of the majority of data rights for the affected portfolio, the technology developed through this SBIR effort can be gradually fielded over time via Engineering Change Proposals (ECPs)" — the interfaces/specs of the diverse legacy shipboard systems this must integrate are government-owned and non-public; a system-of-systems integration architecture cannot be designed without them.
KILL CLASS:    CONTINGENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Design a common, modular hardware/software framework so the Navy's many different below-deck ship systems can share parts, data, and software instead of each being a one-off.
GAPS:
- [TOPIC TEXT] Government-owned interface specs/data rights for the existing "large and diverse set of systems" — not publicly available.
- [INFERRED] The level of naming detail (Zeus, OLYMPUS, existing ECP transition process) suggests an already-underway program with an established integrator, raising incumbency risk beyond the data wall.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    MEDIUM. Would raise if a teaming partner with existing PMA-213/Zeus program access and GFI data rights were identified.
```

---

## 18

```
TOPIC:        DON26BZ05-NV080 — Submarine Cabinet Sound Dampening Alternative
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "The final product desired is a structureborne noise mitigation material with a defined efficient attachment method... reproduced in sheet sizes equivalent to 53711-3203197 baseline material"
KILL REASON:   [TOPIC TEXT] "The selected contractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"; also a materials-science/acoustics product entirely outside team competency (no lab, no fab).
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Invent a longer-lasting, easier-to-replace sound-deadening material for submarine electronics cabinets than the lead foam currently used.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [INFERRED] Acoustics/materials-science lab and MIL-STD-740-2 structureborne-noise test capability.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 19

```
TOPIC:        DPA26BZ05-DV020 — Universal Cell Culture Platform for Rapid Establishment of Species-Agnostic Cell Lines and Autonomous Culture Operations
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "a generalizable platform that fundamentally changes this paradigm by combining (1) species-agnostic biological methods... (2) autonomous, closed-loop automation... and (3) the cellular substrate and engineering workflows needed to build and validate in vitro testbeds for gene-drive technologies"
KILL REASON:   [INFERRED] Requires a wet-lab cell-culture/biosafety facility, biological reagents, and gene-drive engineering capability — entirely outside a software/systems/ML team's competency and equipment, with no benchtop-sourceable path.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check | [INFERRED] Topic text repeatedly self-describes as "This Phase II SBIR topic," which may indicate a Phase-II-oriented scope despite not tripping the literal Stage 0 D2P2 string match

PLAIN PROBLEM: Build an automated lab platform that can figure out, for any animal species, how to grow its cells in culture, and use those cell lines to test gene-drive constructs.
GAPS:
- [TOPIC TEXT] Wet-lab cell-culture and biosafety facility.
- [TOPIC TEXT] Biology/genetic-engineering domain SMEs (iPSC reprogramming, gene-drive construct design).
- [INFERRED] Bioreactor/lab-automation hardware (liquid handlers, imaging systems) integrated with the software stack.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 20

```
TOPIC:        DAF26BZ05-DV033 — Dynamic Open Systems Enclave
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b)/(c) hybrid — [TOPIC TEXT] "a software and hardware toolkit... open-architecture, high-speed computing enclave engineered to rapidly augment field aircraft with next-generation sensor and data processing capabilities"
KILL REASON:   [INFERRED] Same structural barrier as DAF26BZ05-DV031 (topic #6): requires integration into the F-16 Open Systems Enclave and legacy airworthiness/OFP certification process, which is platform-owner/government-controlled and inaccessible to an outside software team without a prime/platform relationship.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a plug-in computing box for legacy jets that can pull in outside sensor/intel data and hand pilots only what matters, without waiting years for a full avionics recertification.
GAPS:
- [INFERRED] Access to F-16 OSE hardware/software development environment (government/platform-owner controlled).
- [INFERRED] Airworthiness certification pathway and beyond-line-of-sight (BLOS) data-link integration expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    MEDIUM. Would raise if OSE has an accessible unclassified dev kit/simulator reachable without a platform-owner relationship — topic text doesn't confirm either way.
```

---

## 21

```
TOPIC:        DPA26TZ05-DV003 — Scalable Platform for Enterprise Engineering and Deployment towards Mathematics for the Discovery of Algorithms and Architectures (SPEED DIAL)
BRANCH:       DARPA   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "creating a framework to transition both previously discovered algorithms and the algorithm discovery engines themselves from curiosities to commodities... embed these tools directly into standard workflows"
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Turn research demos of AI systems that can rediscover known algorithms (like the Kalman filter) into an actual tool engineers can use to discover new algorithms for their own problems.
GAPS:
- [INFERRED] Access to the actual DARPA DIAL program's discovery engines/codebase, if not already published — likely at least partially public given the topic cites specific published results (Transformers rediscovering the Kalman filter, etc.).
- [INFERRED] Domain-expert partnerships across engineering/physics fields to validate real-world embedding, which the STTR RI-partner requirement partly supplies.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] "AI for scientific/algorithmic discovery" tools already exist (symbolic regression, program synthesis); incumbents are likely the original DIAL-program academic performers.
DELTA:         [INFERRED] The delta is productization — turning single-use research demonstrations into a workflow-embedded tool with domain-expert-in-the-loop refinement — which is not what academic DIAL performers are typically built to do.
EXPERIMENT:    [INFERRED] Take a published open-source symbolic-regression/program-synthesis tool (e.g., PySR) and apply it to a public engineering dataset to see whether it can rediscover a known non-trivial formula from data alone, as a proxy for the DIAL claims.
REUSE:         [INFERRED] ML/optimization pipeline and software-productization experience is directly applicable.
DUAL USE:      [INFERRED] Commercial engineering/physics/simulation software vendors are a plausible non-government customer for algorithm-discovery-as-a-tool.
DIFFERENTIATOR:[INFERRED] Software-engineering/productization strength fills the specific "curiosities to commodities" gap the topic names, which academic-only DIAL performers likely can't fill alone.
CONFIDENCE:    MEDIUM. Would raise if a specific open-source DIAL-adjacent codebase is confirmed publicly available to build on.
```

---

## 22

```
TOPIC:        DTR26TZ05-NP001 — Novel Technologies for CWMD and Related Threats
BRANCH:       DTRA   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a)/(b) algorithms/software using existing hardware — [TOPIC TEXT] "solutions that can help to detect the storage, transfer, or use of WMD... through the novel use of signals from existing general-purpose deployed military hardware or non-specialized commercial equipment. Examples could include microphones, cameras, motion detectors, passive infrared"
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Detect signs that someone is storing, moving, or using weapons of mass destruction, using patterns from everyday sensors (cameras, microphones, motion/IR detectors) rather than dedicated radiation/chemical detectors.
GAPS:
- [INFERRED] Real WMD-signature ground-truth data (radiological/chemical/biological handling signatures) is almost certainly classified/restricted and unavailable for Phase I.
- [INFERRED] CBRN detection-physics domain expertise.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched), though [TOPIC TEXT]-observable: an identically-worded SBIR twin of this topic (DTR26BZ05-NP001, item #29 below) appears in the same release, indicating this is a broad, recurring "open topic" DTRA runs across both tracks rather than a narrowly wired one-winner call. [INFERRED] Commercial anomaly/activity-detection from commodity sensors (security/surveillance analytics) is mature; dedicated radiological-detection hardware makers (e.g., national labs, specialty sensor firms) are the likely incumbents on the hardware side, but this topic explicitly avoids new hardware.
DELTA:         [INFERRED] Applying mature commercial anomaly-detection techniques to the (unpublished, sensitive) signature domain of WMD-handling activity, rather than general security anomalies.
EXPERIMENT:    [INFERRED] Using public video/audio anomaly-detection benchmark datasets, test whether an anomaly-detection pipeline can pick up a plausible proxy signature (e.g., unusual heavy/shielded-object handling patterns) as a stand-in for WMD-related activity, since real WMD-handling data is unavailable.
REUSE:         [INFERRED] ML/anomaly-detection and multi-sensor fusion pipeline expertise is directly reusable.
DUAL USE:      [INFERRED] General multi-sensor anomaly detection/fusion has broad civilian security and industrial-monitoring markets.
DIFFERENTIATOR:[INFERRED] Software/ML-first approach targeting existing, ubiquitous sensor infrastructure (no new hardware) matches a small software team's strengths and the topic's own framing.
CONFIDENCE:    LOW. This is a very open-ended topic; would raise with clearer guidance on what specific physical signature is actually being targeted.
```

---

## 23

```
TOPIC:        OSW26TZ05-NV003 — High Throughput Wafer Scale Manufacturing of Custom Achromatic Infrared Meta Optics
BRANCH:       OSD   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "the Army seeks a cost-effective, high-throughput manufacturing process compatible with standard semiconductor fabrication infrastructure to produce wafer-scale achromatic meta-optic components"
KILL REASON:   [TOPIC TEXT] Requires semiconductor nanofabrication (electron-beam/UV/nanoimprint/deep-UV lithography) on a cleanroom fab line — no fab or cleanroom access.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Find a faster, cheaper way to mass-manufacture flat lenses (meta-optics) for infrared cameras that work across a wide range of wavelengths without the color-fringing that flat lenses normally suffer from.
GAPS:
- [TOPIC TEXT] Semiconductor fabrication infrastructure and nanolithography equipment.
- [INFERRED] Nanophotonics/metasurface design domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 24

```
TOPIC:        ARM26BX05-NP011 — xTech|Search 10 Competition
BRANCH:       ARMY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 0

DELIVERABLE:   (d) unstated — this is a prize-competition eligibility gateway, not a technical topic. [TOPIC TEXT] "Finalists selected from the xTech|Search 10 prize competition will be the only firms eligible to submit a SBIR proposal under the topic listed above."
KILL REASON:   [TOPIC TEXT] "August 26, 2026: White paper submission deadline" — that eligibility deadline has already passed relative to today (2026-09-20); there is no path to qualify for this specific cycle regardless of technical fit.
KILL CLASS:    CONTINGENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: N/A — administrative competition-entry topic, not a technical R&D ask.
GAPS:          N/A
LANDSCAPE:     N/A
DELTA:         N/A
EXPERIMENT:    N/A
REUSE:         N/A
DUAL USE:      N/A
DIFFERENTIATOR:N/A
CONFIDENCE:    HIGH. Re-evaluate when the next xTech|Search cycle opens with a live whitepaper window.
```

---

## 25

```
TOPIC:        DON26BX05-NP003 — NAVSEA Open Topic for Model-Based Systems Engineering (MBSE) Acceleration via Artificial Intelligence or Machine Learning Data Ingestion
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "A model that can use AI/ML to ingest multiple forms of technical documentation... and auto generate Systems Modeling Language (SYSML) models"
KILL REASON:   [TOPIC TEXT] "The selected contractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Automatically turn decades of scattered AEGIS combat-system paperwork and legacy files into structured SysML system models using AI.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [INFERRED] Access to actual legacy AEGIS documentation, which is government-furnished and almost certainly restricted/classified regardless of clearance.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 26

```
TOPIC:        DON26BX05-NP004 — NAVWAR Open Topic for Unified Assured Positioning, Navigation, and Timing Operational Awareness and Decision Support
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "the Department seeks expertise in software architecture, data integration, information management, user experience (UX), human-machine interface (HMI) design, analytics, visualization, and decision-support technologies"; explicitly, "This topic does not seek development of new... PNT... hardware systems"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a single dashboard that pulls GPS and backup-navigation/timing system health, confidence levels, and threat data from many different sources into one clear picture with recommended actions for Navy operators.
GAPS:
- [INFERRED] Access to real GPNTS/fleet APNT data feeds and system-specific schemas for full integration — but see LANDSCAPE: open-source reference tools are explicitly named, reducing this gap for Phase I.
- [INFERRED] Domain familiarity with APNT/GPS-denied navigation operational concepts.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] Sponsor explicitly names commercial analogues: "autonomous transportation, cloud operations, telecommunications, logistics, and industrial automation face similar challenges" and open-source tools "All-Source Positioning and Navigation (ASPN) and PNT operating system (pntOS)" already exist as building blocks.
DELTA:         [INFERRED] Contested/GPS-denied military operating environment, security/containerization requirements, and PNT-specific confidence semantics, versus benign commercial ops-monitoring dashboards.
EXPERIMENT:    [TOPIC TEXT]-enabled [INFERRED]: pull the open-source ASPN/pntOS project, feed it synthetic multi-source PNT status data, and build a prototype "single pane of glass" dashboard visualizing system health/confidence/degradation — fully testable with public tools before any government data or award.
REUSE:         [INFERRED] Strong reuse — this is a data-integration/dashboard/UX engineering problem, squarely matching a systems/backend/data-pipeline team's core strength.
DUAL USE:      [TOPIC TEXT] Sponsor itself names non-government analogues (autonomous transportation, telecom, logistics, industrial automation ops centers) as directly relevant, strongly implying an existing commercial market for a generalized platform.
DIFFERENTIATOR:[INFERRED] Direct reuse of commercial ops-monitoring/data-fusion dashboard patterns, competing on integration/UX quality rather than PNT-sensing expertise, which the topic explicitly excludes from scope.
CONFIDENCE:    HIGH. No clearance/data-wall barriers evident in text, explicit open-source starting point, and sponsor-stated commercial analogues make this one of the strongest-fitting topics reviewed.
```

---

## 27

```
TOPIC:        ARM26TX05-NP002 — xTech|Search 10 Competition
BRANCH:       ARMY   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 0

DELIVERABLE:   (d) unstated — prize-competition eligibility gateway, not a technical topic. [TOPIC TEXT] "Finalists selected from the xTech|Search 10 prize competition will be the only firms eligible to submit a SBIR or STTR proposal under the topic listed above."
KILL REASON:   [TOPIC TEXT] "August 26, 2026: White paper submission deadline" — already passed relative to today (2026-09-20).
KILL CLASS:    CONTINGENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: N/A — administrative competition-entry topic (STTR twin of #24).
GAPS:          N/A
LANDSCAPE:     N/A
DELTA:         N/A
EXPERIMENT:    N/A
REUSE:         N/A
DUAL USE:      N/A
DIFFERENTIATOR:N/A
CONFIDENCE:    HIGH. Re-evaluate when the next xTech|Search cycle opens with a live whitepaper window.
```

---

## 28

```
TOPIC:        OSW26BZ05-DV020 — Joint Radar & Communication Waveforms
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms — [TOPIC TEXT] "Phase I is to design chirp/phase-modulated schemes that encode additional information into a radar pulse. Testing would verify that a receiver can decode this embedded data while correctly processing the radar data"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Design a radar pulse that secretly also carries a data message, so a receiver can extract both the radar return and the hidden data without a separate radio link.
GAPS:
- [INFERRED] RF/radar signal-processing domain expertise (waveform design, joint radar-communications literature).
- [INFERRED] Whether Phase I "testing" requires real over-the-air demonstration or simulation only is ambiguous in the text; COTS SDR hardware (e.g., USRP) would make either benchtop-feasible.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Joint Radar-Communications (JRC/DFRC) is an active, well-published academic and industry research field, meaning substantial open prior art exists rather than a narrow, wired ask.
DELTA:         [TOPIC TEXT] Sponsor names the civilian analogue directly: "embedding vehicle ID or geolocation in automotive radar pulses, or providing redundancy to... ADS-B for FAA radars." The defense-specific delta is applying this to reduce reliance on secure datalinks in contested/adversarial RF environments, versus benign civilian ID-embedding.
EXPERIMENT:    [INFERRED] Implement a published DFRC chirp/phase-modulation scheme (widely available in open IEEE literature) on a pair of COTS SDRs and measure bit-error-rate of the embedded data channel alongside standard chirp radar ranging performance.
REUSE:         [INFERRED] Signal-processing/DSP pipeline experience is directly applicable; SDR experimentation is a natural extension.
DUAL USE:      [TOPIC TEXT] "Civilian networks, such as embedding vehicle ID or geolocation in automotive radar pulses, or providing redundancy to... ADS-B for FAA radars."
DIFFERENTIATOR:[INFERRED] An SDR/algorithms-first approach lets a small team demonstrate feasibility on COTS hardware, riding the active open JRC literature, without needing a defense radar prime's hardware access.
CONFIDENCE:    MEDIUM-HIGH. Would raise with confirmation of a specific open DFRC waveform design suitable for SDR implementation, and clarity on the real-hardware-vs-simulation question for Phase I testing.
```

---

## 29

```
TOPIC:        DTR26BZ05-NP001 — Novel Technologies for CWMD and Related Threats
BRANCH:       DTRA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a)/(b) algorithms/software using existing hardware — identical text to STTR twin DTR26TZ05-NP001 (#22): [TOPIC TEXT] "solutions that can help to detect the storage, transfer, or use of WMD... through the novel use of signals from existing general-purpose deployed military hardware or non-specialized commercial equipment"
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Same as #22 — detect WMD storage/transfer/use signatures using existing commodity sensors rather than dedicated radiological/chemical detectors.
GAPS:
- [INFERRED] Real WMD-signature ground-truth data is almost certainly classified/restricted and unavailable for Phase I.
- [INFERRED] CBRN detection-physics domain expertise.
LANDSCAPE:     [TOPIC TEXT] This SBIR topic is textually identical to the STTR topic DTR26TZ05-NP001 (#22) offered in the same release, confirming DTRA runs this as a broad, recurring "open topic" across both tracks rather than a single wired call.
DELTA:         [INFERRED] Same as #22 — applying mature commercial anomaly-detection techniques to the (sensitive) WMD-signature domain.
EXPERIMENT:    [INFERRED] Same as #22 — test an anomaly-detection pipeline on public video/audio benchmark datasets against a plausible proxy signature.
REUSE:         [INFERRED] ML/anomaly-detection and multi-sensor fusion pipeline expertise.
DUAL USE:      [INFERRED] General multi-sensor anomaly detection has broad civilian security/industrial-monitoring markets.
DIFFERENTIATOR:[INFERRED] Software/ML-first approach targeting existing sensor infrastructure matches the topic's own framing.
CONFIDENCE:    LOW. Same open-endedness caveat as #22; no STTR RI-partner overhead makes this the slightly easier of the two twins to pursue.
```

---

## 30

```
TOPIC:        DON26BZ05-NV071 — Dynamically Generated, Articulated 3-Dimensional Training Content
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b) software artifact — [TOPIC TEXT] "a low-code/no-code software platform for the automated generation of AR/MR training content that requires minimal source media (e.g., smartphone photos, video, Computer-aided design model, or schematics)"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Turn a handful of photos or a CAD file of a piece of equipment into an interactive, poseable 3D training simulation automatically, instead of spending months on manual 3D modeling.
GAPS:
- [INFERRED] Domain expertise integrating with Navy-specific AR/MR HMDs and LVC training export standards — learnable, not a hard blocker given COTS-adjacent tools (Unity/Unreal) are explicitly named.
- [TOPIC TEXT] Minimal source media (photos/video/CAD) is explicitly sufficient, meaning Phase I does not require real classified/restricted Navy data to prototype the core generative pipeline.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] Sponsor names the exact relevant SOTA directly: "neural radiance fields, 3-D Gaussian Splatting, and 3-D model diffusion" — increasingly open-source techniques already used commercially in gaming, real-estate/VR, and industrial digital twins.
DELTA:         [TOPIC TEXT] "existing solutions often lack the dynamic articulation, physics, and logic necessary for hands-on procedural practice" — the defense/training-specific delta is adding interactive articulation, procedural logic, and no-code SME authoring on top of static 3D-reconstruction techniques.
EXPERIMENT:    [INFERRED] Take an open-source 3D Gaussian Splatting pipeline, reconstruct a mechanical object from smartphone photos, and test whether an off-the-shelf part-segmentation model can infer movable sub-component boundaries without manual CAD rigging.
REUSE:         [INFERRED] ML pipeline experience (generative 3D models) and data-pipeline/backend skills for the authoring tool and export pipeline.
DUAL USE:      [INFERRED] Auto-rigged, photorealistic 3D content generation from photos has a large civilian market (industrial training/maintenance, e-commerce, VR content, real estate) — likely the largest dual-use market seen so far.
DIFFERENTIATOR:[INFERRED] A small ML/software team can build directly on rapidly advancing open-source 3D generative techniques faster than legacy training/simulation primes built around manual 3D-modeling pipelines.
CONFIDENCE:    MEDIUM-HIGH. Would raise with confirmation that a mature open-source articulation/part-segmentation method exists to layer on top of 3DGS/NeRF reconstructions.
```

---

## 31

```
TOPIC:        DPA26BZ05-DV019 — Semantically-Aware ISR
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (b)/(c) embedded software+hardware — [TOPIC TEXT] "Phase II prototypes shall demonstrate... an onboard, real-time, low-power information-processing layer"; targets named COTS edge hardware: "NVIDIA Jetson Orin Nano... Hailo-8L, Coral Edge TPU, AMD Kintex UltraScale+ FPGA... ARM Cortex-M-class microcontrollers"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a small, low-power onboard AI system for a surveillance drone that watches for behaviorally unusual events (not just recognizable objects) and radios back only a tiny, explainable summary, instead of streaming full video over a jammed/bandwidth-starved link.
GAPS:
- [INFERRED] Real mission-relevant ISR/pattern-of-life imagery is government-specific, though public proxy datasets exist (aerial surveillance anomaly-detection benchmarks such as VIRAT/UAVDT).
- [INFERRED] Domain expertise in vector-symbolic/hyperdimensional computing and neurosymbolic reasoning — a specialized ML subfield the topic explicitly calls for, with a shallower talent pool than mainstream deep learning.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] The sponsor explicitly excludes the easy/obvious commercial approaches — "solutions relying solely on conventional video compression," "object detection with a fixed taxonomy," or "large vision-language models that cannot execute onboard" — a strong signal this is a genuinely open, non-wired R&D ask rather than a call written around an existing incumbent's product.
DELTA:         [INFERRED] Open-world behavioral/temporal anomaly detection under a 2–5W power budget with traceable symbolic reasoning has no mature commercial analogue yet; academic "semantic communication" research is the closest precedent.
EXPERIMENT:    [INFERRED] Buy a COTS Jetson Orin Nano or Coral Edge TPU dev kit, implement a lightweight anomaly/temporal-change detector on a public aerial-surveillance dataset (e.g., VIRAT or UAVDT) combined with a simple vector-symbolic scene-memory layer, and measure both detection quality and actual power draw against the stated 2–5W threshold.
REUSE:         [INFERRED] ML/edge-inference pipeline experience is directly reusable; multimodal fusion, compression, and traceability logging map onto backend/data-pipeline strengths.
DUAL USE:      [INFERRED] Bandwidth-constrained edge AI/semantic compression has civilian markets in remote industrial/pipeline-inspection drones, wildlife-conservation monitoring, and bandwidth-limited satellite IoT.
DIFFERENTIATOR:[INFERRED] A software/ML team unencumbered by legacy heavy-VLM or fixed-taxonomy object-detection product lines can iterate faster on the neurosymbolic/hyperdimensional approaches this topic explicitly calls for, which conventional-CV-pipeline defense ISR primes are less likely to have in-house.
CONFIDENCE:    MEDIUM. Technically deep and well-specified with clear COTS hardware targets; would raise with confirmation of a suitable public aerial pattern-of-life/anomaly dataset.
```

---

## 32

```
TOPIC:        DAF26BZ05-DV032 — F-35 Agnostic Rapid Weapons Integration
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b)/(c) hybrid — [TOPIC TEXT] "a solution that will enable rapid airframe integration of new munitions to reduce the timeline from three to five years to one to two months"
KILL REASON:   [INFERRED] Requires access to the F-35 operational flight program (OFP)/avionics integration environment, controlled by Lockheed Martin and the F-35 Joint Program Office under extremely tight security controls — even more locked down than the F-16 cases (#6, #20) given the F-35's 5th-generation classification posture.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check | [INFERRED] Very likely unstated classification/ITAR requirements given standard F-35 program norms, despite no literal flag term matched in text

PLAIN PROBLEM: Build a way to add new weapons to Air National Guard/Reserve F-35s in weeks instead of years.
GAPS:
- [INFERRED] Access to F-35 OFP/avionics integration environment (Lockheed/JPO-controlled).
- [INFERRED] Airworthiness certification pathway and standing relationship with the F-35 program office.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 33

```
TOPIC:        DON26TZ05-NV023 — Detection and Classification of Low Probability of Intercept radar waveforms using Field-Programmable Gate Array with Cognitive Techniques
BRANCH:       NAVY   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/report — [TOPIC TEXT] "The final deliverable will be a report assessing the feasibility and effectiveness of implementing advanced cognitive techniques on RFSoCs"; prototyped on a named COTS kit: "An evaluation kit of the... AMD (formerly Xilinx) RFSoC is proposed"
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Build an FPGA-based system that can detect and classify sneaky, low-power adversarial radar signals fast enough to inform real-time jamming decisions.
GAPS:
- [TOPIC TEXT] Requires an STTR RI partner with an actual working relationship to NAWCWD's ATSO facility, which the topic states "has access to extensive LPI waveform data" — the team doesn't have this itself, but the STTR structure is explicitly built to supply it via the right RI partner.
- [INFERRED] Domain expertise in RF/radar detection signal processing and FPGA/HDL development.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched), though naming a specific facility (ATSO/NAWCWD Point Mugu) and describing an RI point-of-contact role in detail suggests possible incumbency toward whichever RI already holds that relationship. [INFERRED] RF modulation/signal classification via deep learning is an active commercial/academic field (e.g., RF-fingerprinting products); the defense delta is applying it specifically to low-SNR LPI waveforms for real-time DRFM jamming.
DELTA:         [INFERRED] Same as above — LPI-specific, FPGA-real-time-constrained detection for a jamming application, versus general RF classification research.
EXPERIMENT:    [INFERRED] Using a public RF modulation-classification dataset (e.g., RadioML) as a proxy, train a lightweight CNN and benchmark detection performance/latency against a classical cyclostationary-feature detector in software, before committing to FPGA/HDL implementation.
REUSE:         [INFERRED] ML/signal-processing pipeline skills are directly transferable; FPGA/HDL is a real gap but learnable or coverable by the RI partner.
DUAL USE:      [INFERRED] RF signal classification/spectrum sensing has civilian markets in spectrum monitoring and cognitive radio.
DIFFERENTIATOR:[INFERRED] Validating the algorithm choice on COTS/public data before FPGA porting reduces risk and complements an academic RI partner's FPGA/HDL expertise.
CONFIDENCE:    MEDIUM. Would raise if a specific, reachable RI partner with an actual ATSO relationship can be identified; without one, the topic may be effectively pre-wired to whichever team already has that connection.
```

---

## 34

```
TOPIC:        DON26TZ05-NV024 — Lightweight, Modular Fuel Cell Systems for Unmanned Aircraft Systems
BRANCH:       NAVY   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "a modular fuel cell system where the stack and balance-of-plant can be adjusted to meet a range of electrical power outputs from an initial 1kW to 20kW"; must meet "500 W/kg," "50% or greater" efficiency, "200 full on/off cycles," MIL-STD-810H environmental testing
KILL REASON:   [TOPIC TEXT] Requires fuel-cell stack design/fabrication, thermal management engineering, and environmental qualification testing (altitude, hot/cold, shock/vibration) — electrochemistry lab and specialized test-chamber access the team does not have.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build a lightweight, swappable hydrogen fuel-cell power system for drones that's rugged enough for military use.
GAPS:
- [TOPIC TEXT] Fuel-cell stack fabrication and balance-of-plant engineering capability.
- [TOPIC TEXT] MIL-STD-810H environmental test chambers (altitude, thermal, shock/vibration).
- [INFERRED] Electrochemistry/thermal-management domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 35

```
TOPIC:        DAF26BX05-DV509 — Power the space: high-voltage radiation hardened power switches for space power and propulsion
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "it is desired to reduce the electrical field within the device through innovations with minimal penalty for the on resistance," targeting rad-hard power switches beyond "350 V maximal" derating
KILL REASON:   [INFERRED] Requires radiation-hardened power-semiconductor device design/fabrication and heavy-ion radiation test facilities (for single-event-burnout characterization) — no fab or rad-hard test facility access.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a high-voltage power switch for spacecraft that won't fail when hit by cosmic radiation.
GAPS:
- [INFERRED] Power-semiconductor device fabrication capability.
- [INFERRED] Heavy-ion/radiation test facility access.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 36

```
TOPIC:        OSW26BZ05-NV016 — Desktop Instrument for Measuring Boresight Error as a Function of Incident Angle
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (c) physical article, explicitly benchtop — [TOPIC TEXT] "This solicitation seeks to develop and deliver a desktop testing apparatus that would allow for iterative testing of the BSE and BSES of unmounted and mounted window materials... without high-speed air flow"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a tabletop machine that measures how much a heated, tilted window in front of a heat-seeking sensor bends the sensor's aim, without needing a wind tunnel or flight test.
GAPS:
- [INFERRED] Optomechanical instrumentation build skills (precision goniometric mounts, thermal-gradient generation, IR position-sensing) — a real gap outside the team's stated ML/backend strength, though buildable from COTS optics/photonics parts (blackbody IR sources, translation stages, thermoelectric heaters, IR cameras).
- [INFERRED] Access to real ceramic IR dome/window materials, substitutable with surrogate IR-transmissive materials (e.g., sapphire, ZnSe) for Phase I proof-of-concept.
- [INFERRED] Missile-seeker aero-optics/BSE physics domain expertise.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Optical boresight/beam-steering metrology instruments exist in commercial photonics/laser-system test equipment, but a combined thermal-gradient-plus-incidence-angle IR boresight bench specifically for hypersonic dome materials is a narrow, likely non-commercial niche.
DELTA:         [INFERRED] The defense-specific delta is the combined thermal-gradient + incidence-angle test methodology tailored to hypersonic/supersonic seeker dome materials, which general-purpose optical metrology tools don't address.
EXPERIMENT:    [INFERRED] Build a proof-of-concept rig with a COTS IR source, a surrogate IR-transmissive window sample, a controllable one-sided heater/cooler, and an IR position-sensing detector on a rotation stage, and test whether apparent line-of-sight shift changes measurably and repeatably with induced thermal gradient and incidence angle.
REUSE:         [INFERRED] Data-acquisition and calibration-algorithm software is reusable; the optomechanical hardware build itself is not core team strength.
DUAL USE:      [INFERRED] Optical boresight/beam-steering metrology has civilian markets in telescope and laser-system calibration and photonics R&D equipment.
DIFFERENTIATOR:[INFERRED] Few companies build a dedicated combined thermal-gradient/incidence-angle IR boresight bench; a hardware-partner-plus-software team could add value in the data-acquisition/calibration-algorithm layer.
CONFIDENCE:    LOW-MEDIUM. Optomechanical instrumentation sits outside the team's core strength; would raise with an optics-hardware partner or published precedent for a similar benchtop BSE rig.
```

---

## 37

```
TOPIC:        OSW26BZ05-DV018 — Artificial Intelligence / Machine Learning (AI/ML)-Based Radar Data Compression
BRANCH:       OSD   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/algorithms — [TOPIC TEXT] "Phase I is to explore autoencoder architectures for radar data... Phase I will benchmark compression ratios vs. classical methods"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a neural network that shrinks raw radar data down to a fraction of its size while losing as little detection-relevant detail as possible, so it fits over limited-bandwidth links.
GAPS:
- [INFERRED] Access to representative raw-pulse/range-Doppler SAR datasets — public SAR datasets exist (e.g., MSTAR, Sentinel-1 SLC, Capella Space open data) though possibly not at true raw-pulse fidelity.
- [INFERRED] Domain expertise in complex-valued neural networks and SAR signal processing.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [TOPIC TEXT] The sponsor itself states "Recent work extends neural compression to the complex SAR domain," acknowledging this builds on existing open academic literature rather than being a from-scratch or classified-only problem.
DELTA:         [INFERRED] Real-time embedded deployment (Phase II) for defense radar/data-link bandwidth reduction, versus academic proof-of-concept compression papers.
EXPERIMENT:    [INFERRED] Using a public SAR dataset (e.g., MSTAR or Sentinel-1 SLC complex data), train a complex-valued autoencoder and measure compression ratio vs. reconstruction fidelity and, where labels exist, downstream detection accuracy after decompression.
REUSE:         [INFERRED] Directly matches ML/data-pipeline strength — squarely an ML research-and-benchmarking task.
DUAL USE:      [TOPIC TEXT] "valuable for any high-rate sensor (remote lidar, sensor webs)... compressing UAS radar streams or... weather radar data for comms."
DIFFERENTIATOR:[INFERRED] Strong ML/data-engineering fit on a topic explicitly built on recent open academic literature, with public datasets available to demonstrate the Phase I benchmarking ask directly.
CONFIDENCE:    HIGH. Would raise further with a confirmed public complex-valued raw-pulse SAR dataset, though public SAR imagery alone likely suffices for the Phase I benchmark.
```

---

## 38

```
TOPIC:        DON26BZ05-NV068 — Intelligent Tools for Naval Aircrew Performance and Readiness
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a)/(b) research + software — [TOPIC TEXT] "Proposed solutions should focus on fundamental research into innovative tools for intelligent human performance monitoring and prediction, along with methods for rigorously evaluating their impact"
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build a system that continuously reads a pilot's physiological signals, eye movements, and voice to predict overload, fatigue, or mistake risk, giving flight surgeons early warning and personalized recommendations.
GAPS:
- [INFERRED] Real naval aircrew physiological/performance data is likely restricted (privacy and operational-security reasons); public human-factors/fatigue/cognitive-load datasets (e.g., wearable physiological datasets, aviation human-factors eye-tracking studies) can substitute for early algorithm development.
- [INFERRED] Aeromedical/human-factors science domain expertise and IRB-governed human-subjects research experience, which the team lacks.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Consumer/enterprise fatigue-monitoring and cognitive-load wearables already exist broadly (driver-drowsiness systems, recovery-tracking wearables, trucking/aviation fatigue-risk-management systems) — meaningful existing commercial SOTA.
DELTA:         [INFERRED] Clinical/aeromedical-officer-in-the-loop workflow integration, aviation-specific risk factors (spatial disorientation, vibration-induced injury), and the validated Military Readiness Scale (MRS-15) are the defense-specific delta versus generic consumer wellness wearables.
EXPERIMENT:    [INFERRED] Using a public physiological/cognitive-load dataset (e.g., WESAD or a driver-fatigue dataset with EEG/HR/eye-tracking), train a classifier for generic cognitive-overload/fatigue states and evaluate whether accuracy is high enough to plausibly generalize to the aviation-specific states named in the topic.
REUSE:         [INFERRED] ML/data-pipeline experience for multi-modal physiological signal processing is directly reusable.
DUAL USE:      [INFERRED] Large civilian markets in commercial-aviation pilot fatigue monitoring, trucking/rail operator fatigue-risk management, and consumer wearable health/performance analytics.
DIFFERENTIATOR:[INFERRED] A software/ML team could adapt existing consumer fatigue/cognitive-load detection approaches to the aviation/aeromedical clinical workflow faster than typically slower-moving academic/government human-factors research contractors.
CONFIDENCE:    MEDIUM. Would raise with confirmation of a suitable public dataset with aviation-relevant labels and clarity on IRB requirements for any team-collected validation data.
```

---

## 39

```
TOPIC:        DON26BZ05-NV070 — Multi-Frequency Coverage Unit with Broad Band Interference and Designed Canceller
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "An innovative canceller unit is sought after in a CNI (Communications, Navigation, Identification) system"
KILL REASON:   [TOPIC TEXT] "The selected contractor and/or subcontractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Build a high-power interference canceller for an aircraft radio system so it can keep talking to other aircraft even while frequency-hopping through jamming.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [INFERRED] RF hardware design and high-power UHF transmit/receive test capability.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 40

```
TOPIC:        DON26BZ05-NV075 — High Performance Electrolytic Coating Touch-Up Repairs for Aluminum
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article/process — [TOPIC TEXT] "This topic seeks the development of a portable touch-up method for applying electrolytic conversion coatings"; must meet "corrosion performance requirements of MIL-DTL-81706"
KILL REASON:   [INFERRED] Pure materials-chemistry/electrochemistry process development and corrosion testing — entirely outside a software team's competency and equipment, with no benchtop-sourceable path via COTS components.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Invent a portable way for flight-line technicians to re-apply a corrosion-resistant electrolytic coating to aluminum aircraft parts without needing a full depot chemical shop.
GAPS:
- [INFERRED] Electrochemistry/materials-science lab and corrosion test capability (salt-spray, MIL-DTL-81706 qualification).
- [INFERRED] Aerospace coatings domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 41

```
TOPIC:        DON26BZ05-NV077 — Multi-Core Parallel Processing for Sensor Fusion Architecture
BRANCH:       NAVY   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (b)/(c) architecture+hardware — [TOPIC TEXT] "develop a modular, platform-agnostic sensor fusion architecture that utilizes multi-core parallel processing to optimize data throughput and minimize latency"
KILL REASON:   [TOPIC TEXT] "The selected contractor and/or subcontractor must be able to acquire and maintain a secret level facility and Personnel Security Clearances"
KILL CLASS:    PERMANENT
FLAGS:         T0.3 CLASSIFIED | T0.3 NO FOREIGN INFLUENCE | T0.3 FACILITY CLEARANCE | T0.3 32 U.S.C. § 2004.20 | T0.4 Registration check

PLAIN PROBLEM: Redesign a jet's sensor-fusion software to run fully in parallel across multiple processor cores instead of one step at a time, so no target tracks get dropped under heavy load.
GAPS:
- [TOPIC TEXT] Secret level facility clearance.
- [INFERRED] Access to real AESA radar/DAS/EOTS sensor data streams and 5th-gen platform integration specs, which are classified/government-controlled.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 42

```
TOPIC:        DPA26BZ05-DV018 — Hoboken - SBIR XL
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "Design, build, and demonstrate a fully submersible 3D concrete printer" (Track 1); "characterize a representative library of locally available sediment types... concrete printability" and "validate formulations through printing trials" (Track 4)
KILL REASON:   [TOPIC TEXT] Every track requires marinized hardware fabrication, a materials-testing lab, and physical underwater printing trials — even the most software-adjacent track (Track 4, AI concrete-formulation tool) explicitly requires "collaborate with hardware performers to validate formulations through printing trials," which the team cannot do without lab/fab/marine-hardware access.
KILL CLASS:    PERMANENT
FLAGS:         T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build an underwater robot system that can harvest seafloor sediment and 3D-print concrete structures with it, near-shore.
GAPS:
- [TOPIC TEXT] Materials-testing lab for sediment/concrete characterization.
- [TOPIC TEXT] Marinized hardware fabrication and underwater deployment/test capability.
- [INFERRED] Civil/materials engineering and underwater robotics domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 43

```
TOPIC:        DPA26BZ05-DV021 — Open Architecture Platform for Underwater Vehicles for Rapid Adaptation, Collaborative Sensing, Navigation, and Autonomy
BRANCH:       DARPA   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article (best available reading) — [TOPIC TEXT] "The architecture must demonstrate the following critical capabilities:[Insert chart]" — note: the source topic text is truncated/malformed (a template placeholder was left unfilled), so the full requirements list is not available from this data source.
KILL REASON:   [INFERRED] The available text emphasizes "reduces mechanical complexity," "strict control across the water column, including fixed-depth stationkeeping," and vehicle stability/reliability — strongly implying a physical AUV hull/propulsion/stationkeeping hardware deliverable requiring open-water or pool testing, which is not benchtop-sourceable.
KILL CLASS:    CONTINGENT
FLAGS:         T0.4 Registration check | [DATA QUALITY] Topic description is truncated at source ("[Insert chart]"); re-pull the full topic text before treating this verdict as final.

PLAIN PROBLEM: Build an open, modular autonomous-underwater-vehicle platform that can be quickly reconfigured, hold station, and share data across a fleet.
GAPS:
- [TOPIC TEXT] AUV hull/propulsion hardware and open-water or pool test access.
- [INFERRED] Underwater robotics and navigation/autonomy domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    LOW. Verdict is based on incomplete source text — re-triage once the full topic description (with the missing capability chart) is obtained.
```

---

## 44

```
TOPIC:        DAF26BZ05-NV028 — Ultra-Sensitive Quantum Telemetry Receiver
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      HOLD
STAGE REACHED: 3

DELIVERABLE:   (a) study/report, with supporting lab work — [TOPIC TEXT] "Phase I Minimum Deliverables: Technical report detailing requirements definition, simulation results, and initial experimental findings... Performance evaluation against baseline classical telemetry systems... Preliminary design concept document"; also requires "Perform initial laboratory experiments to validate core concepts"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a quantum-sensor-based radio receiver that can pick up faint, wide-band telemetry signals using unlicensed spectrum, instead of needing scarce, expensive licensed frequency bands.
GAPS:
- [INFERRED] Access to a Rydberg atomic RF-sensor hardware kit for the required "initial laboratory experiments" — commercially available from specialty quantum-sensing vendors (e.g., Rydberg Technologies), but expensive and niche rather than in-house buildable.
- [INFERRED] Atomic/quantum physics (Rydberg spectroscopy) domain expertise.
- [INFERRED] RF telemetry systems engineering and ABMS/JADC2 integration expertise.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Rydberg atomic RF sensors are an emerging but real commercial/academic technology category already marketed for RF sensing/EW applications; incumbents are likely specialty quantum-sensing vendors plus legacy telemetry providers (e.g., Quasonix-class firms).
DELTA:         [INFERRED] Applying Rydberg RF sensing specifically to MRTFB range-telemetry and ABMS/JADC2 integration, versus general-purpose RF sensing.
EXPERIMENT:    [TOPIC TEXT]-aligned [INFERRED]: using published Rydberg-sensor performance data (vendor spec sheets, academic papers) plus known classical telemetry receiver specs, build the comparative simulation the topic's own Phase I explicitly asks for ("develop models and simulations to predict system performance"), without needing to buy hardware first.
REUSE:         [INFERRED] Simulation/modeling and RF systems-engineering software skills are reusable; no existing quantum-sensing hardware.
DUAL USE:      [INFERRED] Quantum RF sensing has emerging civilian markets in spectrum monitoring and 5G/6G interference detection.
DIFFERENTIATOR:[INFERRED] A simulation-first approach can satisfy the explicit Phase I deliverable without first securing specialized Rydberg hardware, deferring the harder hardware-access problem to Phase II/partnership.
CONFIDENCE:    LOW-MEDIUM. Would raise with confirmation that a commercial Rydberg RF-sensor eval kit is affordably accessible for the "initial laboratory experiments" requirement, or clarity on whether that requirement can be satisfied by partnership/subcontract.
```

---

## 45

```
TOPIC:        DAF26BZ05-NV029 — Cost-Effective Composite Joints with Tailorable Performance and Geometry
BRANCH:       USAF   PROGRAM: SBIR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "Design and fabricate initial carbon fiber pi-joint test articles, demonstrating novel fiber architectures and/or manufacturing processes"; "Conduct standard joint mechanical testing to validate performance specifications"
KILL REASON:   [TOPIC TEXT] Requires composite fabrication (carbon-fiber preforming, resin impregnation) and mechanical failure-envelope testing — no composites lab, no fab, no materials-engineering domain expertise.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Invent a cheaper, more flexible way to manufacture the structural joints that hold composite aircraft airframes together, without sacrificing strength.
GAPS:
- [TOPIC TEXT] Composite fabrication equipment (fiber preforming, resin impregnation).
- [TOPIC TEXT] Mechanical testing lab (failure-envelope testing under various loads).
- [INFERRED] Composites/materials-engineering domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 46

```
TOPIC:        DME26TZ05-NP001 — Cable Connector Enhancement
BRANCH:       DMEA   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article/process — [TOPIC TEXT] "a more versatile and efficient solution is needed to address this deficiency" (regarding cable-to-board connector reliability under thermal/mechanical stress)
KILL REASON:   [INFERRED] Requires electronics-manufacturing/rework equipment (Hot Bar Soldering tooling, potting materials, thermal-cycling test equipment) and PCB assembly/mechanical-engineering domain expertise — no lab, no fab.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.4 Registration check

PLAIN PROBLEM: Find a better way to attach cables to circuit boards so the connection survives heat and vibration better than today's connectors or solder-rework methods.
GAPS:
- [INFERRED] Electronics-manufacturing/rework equipment (Hot Bar Soldering, potting, thermal-cycling test).
- [INFERRED] PCB assembly and mechanical-reliability engineering domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 47

```
TOPIC:        DON26TZ05-NV022 — Compact Efficient High Energy Pulsed Laser
BRANCH:       NAVY   PROGRAM: STTR   CLOSES: September 23, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "The final deliverable will be a laser system provided to the Navy to explore the feasibility and military utility of this technology," meeting "Pulse Energy: 10 J or greater... Repetition Rate: Tunable up to 40 kHz"
KILL REASON:   [TOPIC TEXT] Requires "novel laser engineering" to integrate high-power laser components into a compact, field-ready system — needs a laser/photonics engineering lab and high-power optics test infrastructure the team does not have, even though COTS components are permitted.
KILL CLASS:    PERMANENT
FLAGS:         STTR: Requires RI partner | T0.3 ITAR | T0.4 Registration check

PLAIN PROBLEM: Build a compact, high-power pulsed laser system for airborne material-ablation missions that non-specialists can operate and maintain.
GAPS:
- [TOPIC TEXT] Laser/photonics engineering lab and high-power optics test infrastructure.
- [INFERRED] Laser-system integration and thermal-management domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

_(Note: entries 48 onward leave the DoD-specific defense domain — these are NIH/ARPA-H/NSF listings in the same source CSV. The triage framework's clearance/ITAR/defense-delta questions mostly don't apply; noted where relevant. Several ARPA-H entries below are one-paragraph topic blurbs, not full solicitations, so many Stage 2/3 fields are UNKNOWN by necessity, not by omission.)_

---

## 48

```
TOPIC:        1 — Development of therapeutic or preventative technologies for treatment or prevention of Pediatric Cancers and/or Rare Cancers.
BRANCH:       NIH   PROGRAM: SBIR   CLOSES: September 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/biological article — [TOPIC TEXT] "Target validation • Optimized drug candidate screening • Identification of lead and lead candidate optimization • In vivo efficacy studies • Preliminary PK/PD studies"
KILL REASON:   [TOPIC TEXT] Requires wet-lab drug discovery, in vivo animal efficacy studies, and PK/PD studies — a pharmaceutical/biology research lab and vivarium access the team does not have, with no benchtop-sourceable path.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Discover and validate a new drug or therapy for a childhood or rare cancer.
GAPS:
- [TOPIC TEXT] Pharmaceutical/biology wet lab and drug-screening capability.
- [TOPIC TEXT] In vivo animal-study (vivarium) access.
- [INFERRED] Oncology/pharmacology domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 49

```
TOPIC:        2 — Development of devices, diagnostic technologies, or digital health tools for treatment, detection, and diagnosis of Pediatric Cancers and/or Rare Cancers.
BRANCH:       NIH   PROGRAM: SBIR   CLOSES: September 21, 2026
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article, with a software sub-track — [TOPIC TEXT] "Product concept and protype development • Early feasibility studies • Phantom validation • In vivo validation studies • Software development (if needed) • Biocompatibility, sterility, and safety studies"; or "Biomarker optimization and qualification • Assay development... Validation studies in deidentified clinical samples"
KILL REASON:   [TOPIC TEXT] Even the most software-adjacent path (a "digital health tool") is offered alongside device/diagnostic tracks requiring biocompatibility/sterility testing, phantom/in vivo validation, or wet-lab assay development and clinical sample access — none benchtop-sourceable, and the topic gives no indication a software-only submission (with no device/diagnostic/clinical-sample component) is a realistic path to the stated clinical need.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a medical device, lab test, or digital tool to detect or diagnose childhood or rare cancers.
GAPS:
- [TOPIC TEXT] Biocompatibility/sterility/safety testing and clinical (phantom/in vivo) validation capability.
- [TOPIC TEXT] Access to deidentified clinical samples for assay validation.
- [INFERRED] Clinical/regulatory (FDA device or diagnostic) pathway expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    MEDIUM. Would raise if NCI would accept a pure "digital health tool" proposal (e.g., an ML diagnostic-support software layer on top of existing, already-cleared imaging/lab hardware) without requiring the team to also develop or validate a physical device/assay — the topic text doesn't rule this out but doesn't confirm it either.
```

---

## 50

```
TOPIC:        ARPA-H 02 — Versatile Bioadhesives
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical article — [TOPIC TEXT] "develop next-generation bioadhesive platforms that can safely and reliably seal, bond, and repair a wide range of tissues"
KILL REASON:   [INFERRED] Pure biomaterials/wet-lab chemistry (adhesive formulation, biocompatibility, tissue-bonding testing) — entirely outside a software team's competency and equipment, no benchtop-sourceable path.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Invent a better surgical glue that works in wet, bloody, moving tissue and can also deliver drugs.
GAPS:
- [INFERRED] Biomaterials/wet-lab chemistry capability.
- [INFERRED] Biocompatibility and tissue-adhesion testing capability.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 51

```
TOPIC:        ARPA-H 07 — Virtual Human Brain for the Development of Neurosurgical Robotics
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      PURSUE
STAGE REACHED: 3

DELIVERABLE:   (a) study/simulation — [TOPIC TEXT] "creating a high-resolution, physically and anatomically accurate virtual human brain"
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a realistic, physics-based computer simulation of a human brain — how it looks, moves, and deforms when touched or cut — accurate enough to train and test AI-assisted brain-surgery robots on, without needing a real patient.
GAPS:
- [INFERRED] Access to high-resolution structural brain imaging and mechanical tissue-property data — public datasets exist (e.g., Human Connectome Project, IXI dataset, BrainWeb phantom) and published brain-tissue biomechanics literature, reducing this gap for Phase I.
- [INFERRED] Computational neuroanatomy/biomechanical (FEM soft-tissue) simulation domain expertise, and eventual neurosurgical-robotics integration expertise.
- [INFERRED] The topic text itself is a one-paragraph blurb, not a full solicitation — actual Phase I deliverable requirements are unstated and may change the picture materially.
LANDSCAPE:     UNKNOWN recurring topic/winner (not searched). [INFERRED] Surgical digital-twin/simulation research is active for other organs (cardiac, liver); brain-specific real-time deformable simulation is a narrower niche given the brain's unusually low-stiffness, highly heterogeneous tissue properties. Existing clinical neuronavigation software (e.g., Brainlab, Medtronic) models brain anatomy from MRI but typically with simplified/rigid deformation, not the dynamic fidelity implied here.
DELTA:         [INFERRED] The fidelity/dynamics bar (real-time, physically accurate deformation for robotic AI training) is meaningfully higher than existing clinical neuronavigation tools' simplified models.
EXPERIMENT:    [INFERRED] Using a public brain MRI dataset (e.g., a Human Connectome Project subject) and published brain-tissue viscoelastic property values, build a basic finite-element or mass-spring deformable brain model in an open surgical-simulation framework (e.g., SOFA) and compare simulated probe-indentation response against published brain-tissue indentation experiment results in the literature.
REUSE:         [INFERRED] Simulation/ML/3D-modeling pipeline experience (physics simulation, mesh generation, ML-based tissue-property estimation) is directly transferable.
DUAL USE:      [INFERRED] Anatomically accurate deformable-brain simulation has broad non-government value in neurosurgical training/education, pre-op planning software, and other surgical-robotics R&D.
DIFFERENTIATOR:[INFERRED] A computational/ML-first team can iterate quickly on the modeling/simulation software layer, though would likely need a neurosurgery/biomechanics domain partner for clinical validation and credibility.
CONFIDENCE:    LOW-MEDIUM. The topic text is unusually sparse for a funding solicitation; would raise significantly with the full topic description and confirmation of a domain-expert partner for anatomical/biomechanical grounding.
```

---

## 52

```
TOPIC:        ARPA-H 04 — Breaking Ground: The First Curative, Durable, Non-Surgical Therapy for Endometriosis
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/biological article — [TOPIC TEXT] "develop novel, non-surgical therapies to decrease the size or deactivate endometrial implants, to decrease inflammation... and/or prevent growth or regrowth of the lesions"
KILL REASON:   [INFERRED] Pure pharmaceutical/biomedical drug development requiring wet-lab and eventually clinical trial capability — entirely outside a software team's competency and equipment.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Discover a drug or non-surgical treatment that cures endometriosis.
GAPS:
- [INFERRED] Pharmaceutical/biomedical wet lab and drug-development capability.
- [INFERRED] Clinical trial pathway and gynecology/endocrinology domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 53

```
TOPIC:        ARPA-H 06 — Rapid Comprehensive Diagnostic Test for Multi-System Autoimmune Disease
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/biological article — [TOPIC TEXT] "spur the development of novel, rapid diagnostic assays for multi-system autoimmune disease"
KILL REASON:   [INFERRED] Requires wet-lab assay/biomarker development and clinical sample validation — outside a software team's competency and equipment.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build a fast lab test that lets a regular doctor diagnose and predict autoimmune disease affecting multiple organ systems.
GAPS:
- [INFERRED] Wet-lab assay/biomarker-development capability.
- [INFERRED] Access to clinical patient samples for validation.
- [INFERRED] Immunology/autoimmune-disease domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 54

```
TOPIC:        ARPA-H 05 — ARPA-H Lineage Topic
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 0

DELIVERABLE:   (d) unstated — this is an eligibility gate, not a technical topic. [TOPIC TEXT] "supports the advancement, commercialization, and translation of technologies that originated from ARPA-H funded efforts... to help small businesses and startups develop viable products based on these technologies"
KILL REASON:   [INFERRED] Restricted to businesses whose technology "originated from ARPA-H funded efforts" — the team holds no prior ARPA-H award, so there is no eligible technology to submit.
KILL CLASS:    CONTINGENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: N/A — follow-on funding gate for existing ARPA-H awardees only.
GAPS:          N/A
LANDSCAPE:     N/A
DELTA:         N/A
EXPERIMENT:    N/A
REUSE:         N/A
DUAL USE:      N/A
DIFFERENTIATOR:N/A
CONFIDENCE:    HIGH. Re-evaluate only if the team ever holds a prior ARPA-H award.
```

---

## 55

```
TOPIC:        ARPA-H 01 — Development of an annual test to inform women about their future fertility
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/biological article — [TOPIC TEXT] "discover new biomarkers that provide women with actionable data for fertility planning... develop a diagnostic test that can assess fertility status and generate an estimated timeline for the onset of infertility"
KILL REASON:   [INFERRED] Requires biomarker discovery, wet-lab assay development, and human-subjects clinical validation — outside a software team's competency and equipment.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Build an annual test that tells a woman how much longer she has before natural fertility declines.
GAPS:
- [INFERRED] Wet-lab biomarker discovery and assay-development capability.
- [INFERRED] Human-subjects clinical study infrastructure (IRB, longitudinal cohort access).
- [INFERRED] Reproductive endocrinology domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 56

```
TOPIC:        ARPA-H 03 — Universal Platform for Living Adaptive Toxin-removal (UNI-PLAT)
BRANCH:       ARPA-H   PROGRAM: BOTH   CLOSES: September 30, 2027
VERDICT:      KILL
STAGE REACHED: 1

DELIVERABLE:   (c) physical/biological article — [TOPIC TEXT] "catalyze the development of a universal, 'plug-and-play' synthetic biology platform that enables next-generation microbial chassis capable of performing a broad array of programmable functions"
KILL REASON:   [INFERRED] Pure synthetic-biology/wet-lab platform development (engineered microbial chassis) — same category of barrier as the DARPA cell-culture topic (#19): requires a biology lab and genetic-engineering capability the team does not have.
KILL CLASS:    PERMANENT
FLAGS:         T0.4 Registration check

PLAIN PROBLEM: Engineer a reprogrammable microbe platform, initially demonstrated by having it remove toxins from the body for chronic-disease management.
GAPS:
- [INFERRED] Synthetic-biology wet lab and genetic-engineering capability.
- [INFERRED] Microbiology/synthetic-biology domain expertise.
LANDSCAPE:     UNKNOWN
DELTA:         UNKNOWN
EXPERIMENT:    UNKNOWN
REUSE:         UNKNOWN
DUAL USE:      UNKNOWN
DIFFERENTIATOR:UNKNOWN
CONFIDENCE:    HIGH
```

---

## 57–87 — NSF generic technology-area categories (not individually triaged)

The remaining 31 CSV rows (topic numbers `M`, `CA`, `N`, `PH`, `R`, `W`, `AG`, `BM`, `DL`, `ET`, `MO`, `QT`, `AM`, `AA`, `AV/VR/MR`, `CH`, `EN`, `HC`, `LC`, `PT`, `CT`, `SP`, `AI`, `BT`, `DH`, `IH`, `I`, `MD`, `OT`, `PM`, `S`) are NSF's standing technology-area categories under its general SBIR/STTR program ("America's Seed Fund"), not specific solicited topics. Each is a one-paragraph umbrella description with no branch, no Phase I deliverable sentence, and no defense angle — a company pitches its own specific project idea and picks the closest-matching category, rather than responding to a fixed ask. The Stage 1–3 machinery (quote the deliverable, government data wall, defense-specific delta) doesn't apply because there is no fixed deliverable to quote. Instead: fit for a small software/backend/ML team with no lab, no fab, and only benchtop-scale physical prototyping.

| Category | Fit | Why |
|---|---|---|
| AI — Artificial Intelligence | Good | Directly matches team's core ML strength; broadest, most natural category. |
| CA — Cybersecurity and Authentication | Good | Pure software; matches backend/systems strength. |
| AA — Advanced Systems for Scalable Analytics | Good | Data pipelines/ML at scale — a direct match. |
| CH — Cloud and High-Performance Computing | Good | Backend/systems engineering is squarely this category. |
| DL — Distributed Ledger | Good | Software-only; no lab required. |
| QT — Quantum Information Technologies | Borderline | The algorithms/software side (quantum-adjacent simulation, error correction, networking protocols) fits; the physical qubit-hardware side does not. |
| AV/VR/MR — Augmented Virtual and Mixed Reality | Good | Software/content-generation fit, similar to topic #30 above. |
| HC — Human-Computer Interaction | Good | Software/UX fit, similar to topic #26 above. |
| LC — Learning and Cognition Technologies | Borderline | Ed-tech software fits; some subtopics lean into cognitive-science research requiring human-subjects study infrastructure the team lacks. |
| I — Internet of Things | Borderline | The data/analytics/orchestration layer fits; new sensor-hardware development does not. |
| DH — Digital Health | Borderline | Software/algorithms layer (e.g., clinical decision support) fits if paired with an existing cleared device; new hardware or wet-lab diagnostics does not. |
| W — Wireless Technologies | Borderline | Waveform/protocol algorithm work (like topic #28 above) fits; RF hardware fabrication does not. |
| R — Robotics | Borderline | The AI/perception/software-stack layer fits (per topics #31, #33 above); building robot hardware does not. |
| OT — Other Topics | Depends entirely | Catch-all with no content of its own — fit is whatever the underlying idea is. |
| M — Advanced Manufacturing | Poor | Physical manufacturing-process R&D; no fab. |
| N — Nanotechnology | Poor | Requires nanofabrication/cleanroom access. |
| PH — Photonics | Poor | Requires optics/photonics fabrication and lab. |
| AG — Agricultural Technologies | Poor | Requires field/biology trial infrastructure. |
| BM — Biomedical Technologies | Poor | Requires wet lab and clinical validation. |
| ET — Environmental Technologies | Poor | Mostly hardware/sensing and materials; software-only slice is narrow. |
| MO — Mobility | Poor | Vehicle/infrastructure hardware focus. |
| AM — Advanced Materials | Poor | Requires materials-science lab/fab. |
| EN — Energy Technologies | Poor | Requires hardware/materials lab. |
| PT — Pharmaceutical Technologies | Poor | Requires wet lab and drug-development pathway. |
| CT — Chemical Technologies | Poor | Requires chemistry lab. |
| SP — Space | Poor | Propulsion/vehicle hardware focus; software/mission-planning slice is narrow. |
| BT — Biological Technologies | Poor | Requires wet lab. |
| IH — Instrumentation and Hardware Systems | Poor | Hardware by definition. |
| MD — Medical Devices | Poor | Requires device fabrication, biocompatibility, clinical validation. |
| PM — Power Management | Poor | Requires power-electronics hardware lab. |
| S — Semiconductors | Poor | Requires fab access. |

**Bottom line:** if the team develops a concrete software/ML/data product idea independent of any specific defense topic, `AI`, `CA`, `AA`, `CH`, or `DL` are the readiest NSF umbrellas to file it under — but none of these 31 rows are actionable on their own; they require the team to originate the idea first.
