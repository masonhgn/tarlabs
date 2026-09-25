# Deep-research brief 02 — Benchmark design for testing AI/ML tracking against a classical baseline

**For:** a research assistant with web access.
**From:** a small software company building a Phase I SBIR feasibility study.
**Date raised:** 2026-09-24.
**Predecessor:** brief 01 (data foundation), answered 2026-09-23. That brief's answers
corrected one of our decisions and added three tasks; this one is asked in the same spirit.

---

## How to answer this brief

Read the context, then answer the numbered questions in Part 2. Standing instructions, because
this feeds a government proposal that will be evaluated by MITRE and The Aerospace Corporation:

1. **Cite a primary source for every factual claim.** For algorithms and methodology, prefer in
   order: peer-reviewed journals (*IEEE Trans. Aerospace & Electronic Systems*, *IEEE Trans.
   Signal Processing*, *Automatica*), the FUSION / RADAR / AMOS / SPIE Defense conference
   series, textbooks (Bar-Shalom, Li & Kirubarajan; Blackman & Popoli; Mahler), then arXiv,
   then software documentation, then blogs — the last two explicitly flagged as such.
2. **Label every statement** as one of:
   `CONSENSUS` (multiple independent sources agree; name at least two),
   `SINGLE-PAPER` (one source says it; name it),
   `INFERRED` (your reasoning from published material — show the reasoning),
   `UNKNOWN` (you could not find it). An honest `UNKNOWN` is worth more to us than a guess.
3. **Where sources disagree, give both**, with dates. We report disagreements as sensitivity
   parameters; we do not want a silently chosen winner.
4. **Flag anything that looks export-controlled or non-public.** We build exclusively from
   public-domain information (22 CFR 120.34). If a question can only be answered with
   controlled technical data, say that and stop. Do not seek out or reproduce controlled data.
5. **Software you recommend must be MIT, BSD or Apache licensed.** This work may be
   commercialized; GPL/AGPL dependencies are excluded.
6. **For every answer, end with one line: "What this means for your benchmark."** We will act
   on that line. If the honest answer is "nothing changes," say so.
7. **Prioritise.** Questions marked ★ matter most. Answer those fully before the others.

---

## Part 1 — Context

### What we are doing

We are preparing a proposal against **SBIR topic DAF26BX06-NV510, "AI/ML for Next Generation
of Missile Detection, Warning, Tracking, and Reporting"** (USAF/SpaceWERX; Space Systems
Command Space Sensing Delta 84 and the OPIR Tap Lab). Phase I is a **feasibility study and
CONOPS**, $150k, three months, evaluated on four metrics named by the topic: **accuracy,
latency, resilience, coverage**. The topic explicitly requires **explainability and
confidence** in any AI/ML output. Everything is unclassified and public-domain.

### The decision this brief serves

We have decided the proposal's contribution is **a learned component inside a classical
multiple-model tracker** — specifically, **learned model-set adaptation**: replacing the
threshold-and-graph heuristic by which a variable-structure Interacting Multiple Model (IMM)
tracker chooses which motion models to run, with a learned selector. The classical filter bank,
the mode probabilities, and the covariance stay; what is learned is *which hypotheses to
entertain*. This keeps the output explainable (mode probabilities are the explanation) and
keeps the covariance consistent (the topic's "confidence").

Before writing any ML we are building a **benchmark**: a seeded simulation that generates
observations in our domain, runs the classical baseline, scores it, and freezes the result as
the number to beat. **This brief is about designing that benchmark so an ML result on it is
credible rather than an artifact.** We know the principle of garbage in, garbage out; we want
to know, specifically, what the tracking community regards as garbage.

### What is already built and verified (so you do not need to re-derive it)

Every item below has been checked against an independent external reference; please do not
spend effort re-establishing them.

| Component | Validated against |
|---|---|
| SGP4/SDP4 orbit propagation | Vallado's 533 published verification vectors, 1.2e-7 km |
| Fixed-structure IMM (Bar-Shalom §11.6) | FilterPy `IMMEstimator`, agreement 8.5e-14 |
| Variable-structure IMM: **Likely-Model Set (LMS3)** | **Li & Zhang, *IEEE T-AES* 36(2) 2000, Table IV replicated**: our IMM lands within 1.2–1.5% of their published RMS position error in all four deterministic cases; LMS/IMM ratios match case by case |
| Walker constellation generator | Live catalogue: 13.859 rev/day vs measured 13.848–13.895; J2 −0.962°/day vs −0.95 |
| Stereo coverage / field-of-regard | Independently reproduced CSIS *Getting on Track* (2023) finding that a 91-satellite LEO layer achieves stereo at 120° FOR and fails at 110°/100° |
| Glide-vehicle trajectories | Consumed from the Berkeley Risk & Security Lab's published simulator (Tracy & Wright model), reproduces published range to 0.09% |
| US Standard Atmosphere 1976; HITRAN line-by-line transmission | Published table to 0.001%; known 4.3 µm band opacity |
| IR background | Real GOES-19 ABI L1b frames (3.9 µm window band — we know this **overstates** background relative to a solar-blind OPIR band and say so) |

**One finding from the replication that shapes this brief.** The survey literature says LMS
"substantially outperforms" fixed-structure IMM. The primary source does not: Li & Zhang's own
Table IV has plain LMS slightly *worse* than IMM on RMS position error in all six cases, at
36–65% of the FLOPs. The accuracy gain belongs only to their forgetting-factor variant, and only
on the sparse model topology. So our baseline is honest and replicated, and the bar for a
learned selector is: **match or beat fixed-structure IMM accuracy at LMS-class cost, on a
benchmark the learner has not been able to memorise.**

### What we do NOT yet have — the gaps this brief is aimed at

- **No measurement generator in our domain.** We can compute who sees what, when, and how good
  a stereo fix would be — but nothing that turns (satellite states, target state, sensor
  parameters) into **angle measurements with noise, missed detections, false alarms and
  timestamps**. The only measurement generator we have is Li & Zhang's 2-D Cartesian one.
- **No public sensor parameters** for angular noise, detection probability vs SNR, IR clutter,
  revisit. Three items were deliberately deferred out of our data phase as "parameter
  definition, not acquisition": sensor angular-noise model, background radiance distributions,
  event-label uncertainty.
- **No angles-only fusion architecture decision** (see Part D).
- **No prior-art sweep on learned IMM / learned model-set adaptation** (see Part E). This
  decides whether our novelty claim is honest.
- **No evaluation protocol** beyond "500 Monte Carlo runs, as the paper did."

### Our problem geometry, for reference

Low-Earth-orbit constellation (~900–1000 km, polar-ish planes, notional, seeded from the
measured SDA Tranche 0 geometry) observing a **manoeuvring glide-phase target at 38–57 km
altitude** with passive infrared sensors: **angles only, no range**. Two or more satellites in
view give a stereo fix; the achievable position error scales as 1/sin(convergence angle).
Single-satellite epochs are common. Target speed several km/s; manoeuvres are lateral
accelerations of order 1–4 g held for tens of seconds. Revisit is seconds to tens of seconds.

We also hold, for real-data anchoring: one hour of **OpenSky ADS-B state vectors** (26 M rows,
13,120 aircraft, 7,353 simultaneous at 1 s cadence, global, with `icao24` as truth identity).

---

## Part 2 — Questions

### A. Sensor / measurement model — what to simulate and at what fidelity

**A1 ★ Angular measurement noise.** What angular measurement accuracies (IFOV, noise-equivalent
angle, centroiding accuracy, in µrad or arcsec) are *publicly* stated or *commonly assumed* for
space-based IR tracking sensors — SBIRS, HBTSS, SDA Tracking Layer wide-field-of-view sensors,
or academic space-based IR tracking studies? Separate what an agency has published from what
simulation papers assume. We need a **defensible range** to sweep, not a point value.

**A2 ★ Detection probability model.** For IR point-source detection in tracking simulations,
what functional forms of Pd vs SNR are used (Marcum/Swerling, Rician, empirical logistic,
constant Pd)? Is a **constant Pd** acceptable for a Phase I benchmark, or does the community
expect SNR-dependent Pd tied to a radiometric model? If the latter, what is the minimum
credible radiometric chain (target intensity → irradiance at aperture → SNR → Pd)?

**A3 ★ False-alarm / clutter model.** Tracking benchmarks almost universally use spatially
uniform Poisson clutter. Real IR clutter is spatially and temporally correlated (cloud edges,
terminator, sun glint, Earth limb). What clutter models are published for space-based IR, what
densities (false alarms per steradian per frame, or per pixel per frame) are stated or assumed,
and — importantly — **do OPIR tracking papers actually use anything beyond uniform Poisson?**
If uniform Poisson is the norm, we want to know that so we can justify it; if not, we want the
model they use.

**A4 ★ Revisit / frame rate.** What revisit intervals or frame rates are public for scanning vs
staring OPIR sensors, and what do LEO tracking-layer simulation studies assume? Does the
literature treat revisit as synchronous across satellites or as independent asynchronous
streams (which changes the fusion problem materially)?

**A5 Measurement biases.** Are sensor pointing-knowledge (attitude) errors and time-tag errors
normally included in angles-only tracking simulations, and at what magnitude relative to the
random angular noise? Do they get modelled as per-measurement noise, per-sensor slowly varying
bias, or ignored? (We have a clock/time-tag error budget already; we need the community's
practice for **attitude** bias.)

**A6 Earth-limb transition.** A target at 40–60 km altitude viewed from LEO is sometimes seen
against space (above the hard Earth limb) and sometimes against the Earth. How do published
simulations treat the change in detectability across that transition — as a Pd step, a
clutter-density step, a separate sensor mode, or not at all?

### B. Benchmark scenario design

**B1 ★ The established benchmarks.** Enumerate the manoeuvring-target tracking benchmark
problems that the community actually cites and reuses: the Blair & Watson IEEE benchmark
(1994; Blair, Watson, Kirubarajan & Bar-Shalom 1998), Li & Bar-Shalom's and Li & Zhang's
13-model acceleration-grid benchmark, and anything **space-based, ballistic, or hypersonic**
with a *published scenario definition*. For each: what are the scenario families, how did the
authors justify them, what noise levels, how many Monte Carlo runs, and is it still in use?

**B2 ★ Manoeuvre generation without artifact leakage.** We are worried about this specific
failure: if the synthetic truth is piecewise-constant acceleration with instantaneous switches
(as in Li & Zhang's Table III), a learned selector will learn *that generator* rather than
manoeuvres, and beat the classical baseline for the wrong reason. What manoeuvre-generation
models does the literature use — semi-Markov acceleration processes, Singer, jerk/Wiener
acceleration, coordinated turn with random rates, trajectory-library sampling — and is there
any published discussion of **a learned tracker exploiting synthetic-generator artifacts**
("benchmark leakage", "generator overfitting") and how to guard against it? We want the
generator family the community would find hardest to argue with.

**B3 ★ Public HGV manoeuvre characterisation.** Beyond Tracy & Wright (*Science & Global
Security* 2020), Acton, and the BRSL simulator — which we hold — what public, unclassified
characterisations exist of glide-phase manoeuvre profiles: bank-reversal period, lateral
acceleration in g, skip amplitude and period, terminal-phase behaviour? We want a scenario
family that spans **what is publicly established as plausible** and nothing more. If the
honest answer is "the public literature has only two or three sources and they are the ones
you have," say so — that itself is a finding we report.

**B4 Held-out scenario families.** How do published ML-tracking evaluations partition scenarios
so a held-out set genuinely tests generalisation rather than interpolation — by manoeuvre
intensity, by geometry, by noise level, by generator family? Are there explicit protocols we
can cite (MOTChallenge for vision tracking; anything from the radar/sonar tracking community;
Stone Soup's own benchmark practice)?

### C. Evaluation protocol for ML-versus-classical comparisons

**C1 ★ Statistical methodology.** Li & Zhang used 500 Monte Carlo runs and reported point
values, no confidence intervals. What is current practice in *IEEE T-AES* and FUSION for
reporting a tracker comparison — run counts and their justification, paired vs unpaired
designs, confidence intervals, significance tests? Is there a recognised standard we can adopt
and cite, so a reviewer cannot say "500 runs, no error bars"?

**C2 ★ Baseline fairness.** When an ML method is compared against IMM, what is the accepted
practice for tuning the classical baseline — grid search on a validation set, the original
paper's parameters, both reported? Are there **documented cases** of an ML-tracking result
later shown to rest on an under-tuned classical baseline? We want to cite them as the failure
mode we are designing against.

**C3 Metrics.** GOSPA (Rahmathullah, García-Fernández & Svensson, FUSION 2017) is the current
multi-target standard; is OSPA still expected alongside it? For a **single-target
manoeuvring** benchmark, is RMSE + NEES (covariance consistency) + peak error still the accepted
trio? Is there any published metric for the **quality of mode-probability outputs** as an
explanation (calibration of mode probabilities, mode-identification percentages as Li & Zhang
report, or anything newer)? The topic requires explainability; we want to measure it, not
assert it.

**C4 ★ Sim-to-real credibility at TRL 3.** For a simulation-only feasibility study, what does
the tracking community accept as evidence that a synthetic benchmark is representative? Is there
precedent for **anchoring a synthetic benchmark with real ADS-B aircraft data** — i.e. showing
that the tracker's measured behaviour (NEES, custody, mode switching) on real aircraft tracks is
consistent with its behaviour on the synthetic set? Any published examples of ADS-B used as a
surrogate truth set for tracker validation?

### D. Angles-only stereo fusion architecture

**D1 ★ Converted measurement vs nonlinear filtering.** For angles-only tracking from two or more
platforms, what does the literature recommend: triangulate stereo pairs into a Cartesian position
with a converted-measurement covariance (Lerro & Bar-Shalom 1993 debiased conversion and
successors) and feed a *linear* filter bank, or run EKF/UKF mode-matched filters on the raw
angles? Specifically at **low convergence angles (5–20°)**, where the range error is large and
non-Gaussian, is converted-measurement acceptable or does it break? We have a verified linear
IMM and would prefer to keep it if the literature permits.

**D2 ★ Single-sensor epochs.** When only one satellite sees the target there is no pair to
triangulate. How do published multi-platform angles-only trackers handle intermittent stereo —
bearings-only update of an existing track, coasting, range-parameterised filters, something
else? Which is standard for the space-based case?

**D3 Cross-validation targets.** Are there open-source (MIT/BSD/Apache) reference
implementations of angles-only or multi-sensor bearings-only tracking that we can validate
against, as we did with FilterPy for IMM? Stone Soup (MIT) has bearings-only measurement
models — is its angles-only path validated anywhere against a published result?

### E. Prior art on learned IMM / learned model-set adaptation — the novelty check

**E1 ★ What exists.** Survey ML-augmented multiple-model tracking: learned transition
probability matrices; LSTM/GRU/transformer-predicted mode probabilities; "neural IMM"; learned
model banks; reinforcement learning for model selection; KalmanNet and derivatives; hybrid
model-based/data-driven filters. For each: **what was learned, what classical baseline, what
gain, on what scenario, and was covariance consistency reported?** Be exhaustive here — this
decides whether our claim is novel, incremental, or already published.

**E2 ★ Variable structure specifically.** Li & Zhang (2000) and the VSMM family (Li & Bar-Shalom
Parts I–V; Li & Jilkov 2005 survey Part V) leave the **model-set design** — the digraph, the
adjacency, the activation/termination thresholds — as a hand task. Has anyone **learned** the
adjacency graph, the thresholds, or the model-set selection policy of an LMS/VSMM algorithm? If
yes, cite it precisely. If no, say so plainly — that absence is our contribution's justification
and we need to be certain of it.

**E3 Explainability-preserving learned trackers.** Any learned-IMM or hybrid work that keeps
mode probabilities as an interpretable output and reports NEES or another covariance-consistency
measure? Most ML tracking papers report only RMSE; we need to know if anyone has held the
learned component to the same confidence standard as the classical one.

**E4 OPIR-specific ML tracking.** Any unclassified published application of ML tracking to
space-based missile warning or OPIR (AMOS, SPIE Defense + Commercial Sensing, AIAA SciTech,
FUSION, MSS if public abstracts exist)? What did they simulate, how, and what did they compare
against?

### F. Real-data anchors

**F1 Angles-only real data.** Beyond ADS-B, is there any **public dataset of angles-only or
bearings-only multi-sensor observations with truth** — optical satellite-tracking observations
with known ephemerides, ground-based telescope angle streams, sonar bearings-only benchmark
sets, astronomy moving-object surveys — usable as a real-data sanity anchor for an angles-only
tracker?

**F2 High-speed manoeuvring vehicle telemetry.** Public datasets or published trajectory
reconstructions of manoeuvring high-speed vehicles — sounding rockets, reusable-booster return
flights, X-plane or hypersonic test flights with released telemetry, re-entry capsule
reconstructions — usable to anchor manoeuvre *statistics* (not to model any specific system)?

---

## Part 3 — What we do not need

To save your effort: do **not** re-derive or re-survey the IMM algorithm, the LMS/VSMM algorithm
family, SGP4, Walker constellation geometry, angles-only observability (1/sin α), atmospheric
transmission, or constellation architecture trades (CSIS 2023 has done that and we cite it).
Do not address network latency or fusion placement — that is a separate thread. Do not attempt
to characterise any specific real weapon system.

## Part 4 — Output format

For each question: the answer; the label (`CONSENSUS` / `SINGLE-PAPER` / `INFERRED` /
`UNKNOWN`); primary citations with year and venue; your confidence (high / medium / low, one
phrase why); and the closing line **"What this means for your benchmark: …"**. Group by section.
Finish with a one-page summary: the five things you would change about our benchmark plan if
you were us, in priority order.
