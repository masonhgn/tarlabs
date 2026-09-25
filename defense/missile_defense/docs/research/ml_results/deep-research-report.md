# Benchmark Design for Credible AI/ML-versus-Classical Maneuvering-Target Tracking

## Executive judgment

This review addresses the benchmark-design questions in the submitted brief, with emphasis on the starred items and on preserving an auditable classical baseline. The project context, existing validations, and the intended learned model-set selector are taken from the brief. fileciteturn0file0

**[INFERRED] The benchmark plan is directionally strong, but I would change five things before freezing it.** First, do **not** make an instantaneous piecewise-constant-acceleration generator the learner's principal training and test world; hold out entire maneuver-generator families. Second, make the measurement layer a two-tier benchmark: a deliberately simple constant-\(P_D\)/Poisson-clutter core plus a geometry/background-dependent radiometric stress suite. Third, do not use naive stereo triangulation as though its Cartesian error were Gaussian at low convergence angle; either use a bias-aware converted-measurement front end whose covariance is empirically validated or preserve raw LOS information. Fourth, pair every ML/classical comparison by random seed and report uncertainty and covariance consistency, not point RMSE alone. Fifth, **change the novelty language now**: a 2025 IFAC-PapersOnLine paper explicitly proposes a Deep-Q-Network-based model-set-adaptation policy for a variable-structure IMM, so “first learned VSIMM model-set selector” is not defensible. citeturn2search3turn18search12turn5search7

**[CONSENSUS] The public U.S. program material supports the architectural premises—SBIRS scanner/starer payloads, SDA wide-field-of-view missile-warning/tracking sensors, HBTSS-derived medium-field-of-view tracking, and the importance of stereoscopic coverage—but the official sources I found do *not* publish the numeric angular error, centroiding accuracy, detector frame cadence, \(P_D(\mathrm{SNR})\), or false-alarm density needed to instantiate your simulator.** The Space Force SBIRS fact sheet describes scanner and step-starer functions and “fast revisit”; SDA identifies WFOV tracking sensors; MDA describes HBTSS as producing fire-control-quality tracking data. None of those public pages supplies the numerical measurement parameters you are asking for. citeturn8search5turn8search1turn8search17

**[INFERRED] That is not a reason to invent “SBIRS-like” numbers.** For the proposal, separate **published sensor facts** from **benchmark sensitivity parameters**. Call the latter “notional unclassified sweep values,” freeze them before ML development, and make the conclusion robust across them. That is much harder for a reviewer to attack than assigning a classified system a seemingly precise public performance number that no agency actually published. citeturn8search5turn8search17

**[INFERRED] Export-control/public-data boundary:** nothing below relies on non-public technical data. Where detailed OPIR performance appears to be absent from public official sources, I mark it `UNKNOWN` rather than reverse-engineering a real system. Public NASA flight-reconstruction records used later are explicitly marked public/public-use-permitted by NASA. citeturn21search0turn21search8turn21search9

## Sensor and measurement model

### A1 ★ Angular measurement noise

**Answer — `UNKNOWN` for official operational sensor accuracy; `SINGLE-PAPER` for the useful public academic design points. Confidence: high on the absence from the official sources reviewed; medium on the representativeness of academic values.**

**[CONSENSUS] Agency-published information establishes sensor *type and mission*, not the numerical angular-noise budget.** The current public SDA material calls the Tracking Layer payloads WFOV missile-warning/missile-tracking IR sensors, while MDA describes HBTSS as providing fire-control-quality tracking data and links HBTSS-derived technology to the medium-field-of-view portion of the proliferated architecture. The Space Force SBIRS fact sheet describes a continuously scanning sensor plus an agile step-starer with high sensitivity and fast revisit. None of these sources states IFOV, noise-equivalent angle, centroiding \(\sigma\), or an arcsecond/µrad track-error figure. citeturn8search1turn8search17turn8search5

**[SINGLE-PAPER] A public 2026 space-based IR system-design study—not an official U.S. OPIR specification and not a missile-tracking performance disclosure—does put concrete angular-resolution values in the same engineering regime.** Its parametric space-based infrared calculation discusses 7 µrad angular resolution for a 2.8 m aperture and reports sensitivity optima at 1.5 µrad for a 2.8 m aperture and 2.2 µrad for a 1.6 m aperture. Treat those as published **academic design points**, not as SBIRS/HBTSS/SDA performance. citeturn23search4

**[SINGLE-PAPER] Public ballistic-target IR tracking literature also warns against reducing a focal plane automatically to “true angle + Gaussian noise.”** Zhao and Huang's 2017 space-based early-warning study models finite focal-plane pixels as ambiguous measurements and reports materially different tracking behavior than the usual point-angle approximation. That is a useful warning for a learned selector because pixel quantization/centroid behavior can otherwise become an unmodeled source of train/test mismatch. citeturn23search0

**[INFERRED] I would therefore freeze a *logarithmic sensitivity grid*, not a claimed OPIR specification: \(\sigma_\theta\) or equivalent centroid error at roughly 1–3, 10, 30, and 100 µrad per angular axis, with the first points explicitly linked to the public academic design scale and the upper points explicitly labeled stress cases rather than real-system estimates.** Also keep IFOV separate from centroiding standard deviation: a point source can be localized to a fraction of a pixel under favorable SNR, while finite-pixel/PSF effects make “one pixel = one Gaussian sigma” unjustified. The purpose of the 30–100 µrad cases is robustness testing, not an assertion about an operational sensor. citeturn23search0turn23search4

**What this means for your benchmark: do not publish a single “HBTSS/SBIRS accuracy”; publish a notional 1–100 µrad sensitivity sweep, identify the 1.5–7 µrad region as publicly demonstrated academic design territory, and label everything else a stress parameter rather than a real-system specification.**

### A2 ★ Detection probability versus SNR

**Answer — `CONSENSUS` that both abstractions exist at different layers; `INFERRED` that your benchmark should contain both. Confidence: high.**

**[CONSENSUS] Tracker-level studies often abstract detection as a fixed probability, whereas sensor/detection studies derive detection performance from radiometry, SNR, threshold, and false-alarm probability.** A space-target tracking study, for example, simply sets \(P_D=0.98\) while supplying a clutter model; by contrast, an Applied Optics IRST paper builds a detection-performance model around target radiation, atmospheric transmission, signal-to-noise ratio, detection angle, \(P_D\), and \(P_{FA}\). A separate infrared detection study uses a Neyman-Pearson detection formulation connecting \(P_D\), \(P_{FA}\), and SNR. citeturn3search0turn3search7turn3search9

**[INFERRED] A constant \(P_D\) is therefore entirely defensible as a *controlled tracking benchmark abstraction*, but not as the only realism claim in this geometry.** Its virtue is experimental isolation: you can ask whether model-set selection improves tracking independently of sensor detection physics. Its defect is that it intentionally destroys correlations among range, atmospheric path, Earth/space background, target intensity, geometry, and missed detections—the very correlations a LEO OPIR system encounters. The clean solution is to maintain a “core” constant-\(P_D\) suite and a separate radiometric suite. citeturn3search7turn14search12

**[CONSENSUS] The minimum credible radiometric chain is not especially exotic:** target spectral intensity/radiance and range, atmospheric transmission, optical collection/bandpass, focal-plane signal, background and detector noise, a detection statistic/SNR, a threshold fixed by \(P_{FA}\), then the resulting \(P_D\). The 2023 Applied Optics IRST model follows this target-radiation → atmospheric-transmission → SNR → detection-performance structure, while a 2025 full-link space-IR simulation explicitly includes orbit geometry, sensor noise, optical-axis disturbance, scenery noise, radiation modeling, and system-noise calculation. citeturn3search7turn14search12

**[SINGLE-PAPER] One recent public space-IR model gives a particularly transparent noise decomposition: point-source energy is propagated through atmospheric transmission, aperture/optical efficiency, energy concentration, quantum efficiency and integration time, while background photon shot noise and read noise determine the noise term.** That is close to the minimum chain your existing HITRAN/background foundation is already able to support. citeturn23search4

**[UNKNOWN] I did not find a primary public OPIR tracking source in this search that establishes Marcum/Swerling statistics or an empirical logistic \(P_D(\mathrm{SNR})\) as the accepted space-IR standard.** Swerling terminology is strongly associated with fluctuating radar-target models; I would not import it into passive-IR point-source detection merely to make the model look more sophisticated.

**[INFERRED] Use a simple Neyman-Pearson/ROC-compatible detector in the realism suite rather than fitting an arbitrary logistic curve.** The precise detector can remain deliberately generic: calculate the detection statistic from the photon/background/read-noise model, set its threshold from a benchmark \(P_{FA}\), and evaluate \(P_D\) under the assumed signal/noise law. Then sweep uncertainty in target radiance instead of pretending it is known. citeturn3search7turn3search9turn23search4

**What this means for your benchmark: retain constant \(P_D\) as the clean algorithmic benchmark, but add an operational-stress suite in which your existing radiometry drives SNR and hence \(P_D\); conclusions about the learned selector should survive both.**

### A3 ★ False alarms and clutter

**Answer — `CONSENSUS` that simple tracking studies use uniform/Poisson-style clutter while real IR backgrounds are structured; `UNKNOWN` for a public, authoritative OPIR false-alarm density. Confidence: high.**

**[CONSENSUS] The simple model really is common in tracking work.** A space-target tracking example uses Poisson random-finite-set clutter with a fixed spatial intensity and a fixed \(P_D\); a dedicated infrared point-target/PDAF study represents false-alarm feature locations with uniform distributions. These are precisely the kinds of assumptions you propose. citeturn3search0turn3search1

**[CONSENSUS] Real infrared imagery is not spatially homogeneous.** IRST image-processing work explicitly separates regional clutter from clouds, horizon, sea and glint; space-based star-field work identifies stars as dominant interference/false-alarm sources for dim moving IR targets. SDA's PIRPL flight experiment was created specifically to characterize infrared background noise from the Earth's surface, ocean and atmosphere, further underscoring that the background field depends on scene type rather than behaving as stationary white clutter. citeturn3search10turn9search10turn8search8

**[UNKNOWN] I did not find a credible public U.S. OPIR source that gives an operational false-alarm density in false alarms/sr/frame or false alarms/pixel/frame for SBIRS, HBTSS, or the SDA Tracking Layer.** Nor did I find evidence that a particular correlated spatial point-process model is the established OPIR-tracking benchmark. That parameter should stay explicitly notional.

**[INFERRED] Use **uniform Poisson clutter as the baseline**, because it is recognizable and isolates the tracker, then make the harder test a held-out structured-clutter suite.** You already possess the right raw material: real GOES background frames. Estimate a spatial intensity map after whatever preprocessing constitutes your notional detector and draw false plots conditionally on that map, or inject detections directly from a thresholded background pipeline. That becomes an inhomogeneous/Cox-like process without claiming that such a process is an operational OPIR model. The important benchmark property is that training on homogeneous clutter cannot guarantee performance on the real-background suite. citeturn3search1turn3search10turn8search8

**[INFERRED] Specify clutter in angular units—false plots/sr/frame and the corresponding expected count in the instantaneous FOV—rather than “N false alarms per scan.”** That makes density transferable across FOV choices and prevents a change in sensor footprint from silently changing problem difficulty.

**What this means for your benchmark: make homogeneous Poisson clutter the published baseline, declare the density a sensitivity parameter, and add a frozen real-background-derived structured-clutter holdout; do not claim an operational OPIR false-alarm density that public sources do not support.**

### A4 ★ Revisit and frame timing

**Answer — `UNKNOWN` for public numeric cadence of the named U.S. systems; `CONSENSUS` that asynchronous multisensor processing is a real and established tracking problem. Confidence: high.**

**[CONSENSUS] Official sources give qualitative timing, not the requested numbers.** SBIRS is publicly described as combining a continuously scanning sensor with an agile step-starer and “fast revisit”; SDA describes persistent, stereoscopic LEO tracking coverage; MDA describes birth-to-death HBTSS tracking. I found no official public frame-rate or per-target revisit number for these sensors. citeturn8search5turn8search1turn8search17

**[CONSENSUS] Treating multisensor bearings as asynchronous is well established in the tracking literature.** A 2007 FUSION paper is explicitly devoted to multiple-target tracking with **asynchronous bearings-only measurements** and uses a range-parameterized UKF; a 2023 IEEE T-AES paper jointly handles asynchronous multisensor measurements plus spatial/temporal sensor biases in a maneuvering-target IMM/UKF framework. Out-of-sequence measurements have likewise been treated as a general multisensor estimation problem in T-AES. citeturn14search1turn15search12turn14search4

**[UNKNOWN] I found no primary source establishing that LEO OPIR simulation studies conventionally synchronize all satellites to a common frame clock.** Published studies frequently simplify sampling for simulation, but that is not sufficient evidence to call synchronization the community norm.

**[INFERRED] Your benchmark should therefore have two timing modes.** Use common-time synchronous observations for the regression/unit-test suite because they make failures diagnosable. Use independent phase offsets and event timestamps for the headline operational benchmark, with each measurement propagated/updated at its own timestamp. A learned selector that depends on a perfectly periodic common cadence has learned another simulator artifact. citeturn14search1turn15search12

**What this means for your benchmark: do not advertise a public HBTSS/SDA frame rate; sweep notional cadence and make independent asynchronous sensor clocks the primary generalisation test, while retaining synchronous data only as a controlled subcase.**

### A5 Measurement biases

**Answer — `CONSENSUS` that spatial/temporal biases and optical-axis disturbances are legitimate estimator states/systematic errors; `UNKNOWN` for a defensible public OPIR attitude-bias magnitude. Confidence: medium-high.**

**[CONSENSUS] Tracking literature does not require sensor misalignment to be represented as fresh white measurement noise.** The 2023 T-AES spatiotemporal-bias paper explicitly augments sensor biases into the state and estimates them jointly with a maneuvering target; a 2025 full-link space-infrared simulator explicitly includes optical-axis disturbance as part of the sensor imaging/error chain. citeturn15search12turn14search12

**[UNKNOWN] I did not find a public operational pointing-knowledge/attitude-error allocation for SBIRS, HBTSS or SDA Tracking that can responsibly be quoted against your random angular noise.**

**[INFERRED] For benchmark credibility, model attitude/boresight error as a **per-sensor correlated bias**, not by folding it entirely into iid \(\sigma_\theta\).** A minimal process is a constant offset over a pass; a harder variant is a random walk or first-order correlated drift. Give the learner no direct access to the true bias. If the baseline and learner share the same bias estimator—or both deliberately omit one—the comparison stays fair. This follows the bias-state practice of the multisensor literature while avoiding a fake operational magnitude. citeturn15search12turn14search12

**What this means for your benchmark: add a frozen per-sensor boresight-bias/drift stress parameter separate from white centroiding noise, but label its magnitude notional because a public OPIR allocation was not found.**

### A6 Earth-limb transition

**Answer — `UNKNOWN` for an established OPIR tracker-level “limb transition” convention; `INFERRED` for the recommended treatment. Confidence: medium.**

**[CONSENSUS] The physical background difference is real enough that the U.S. government has flown a dedicated experiment to characterize Earth infrared backgrounds.** SDA describes PIRPL as measuring background noise associated with the Earth's surface, ocean and atmosphere; image-level IR literature independently demonstrates strong scene-dependent clutter. citeturn8search8turn3search10

**[UNKNOWN] I found no public OPIR tracking benchmark that establishes a standard hard limb rule such as “multiply \(P_D\) by X below the limb” or “multiply clutter density by Y.”** A specific numerical step would therefore be harder to defend than the underlying radiometry.

**[INFERRED] Because you already calculate geometry, atmosphere and real Earth-background radiance, use a *continuous radiometric transition* in the higher-fidelity suite: classify each LOS by its background intercept, assign space/Earth/limb-background radiance, calculate SNR, then obtain \(P_D\).** Keep a two-state step model only as an ablation because it is easy to reason about. That avoids adding an arbitrary discontinuity the learner could memorize. citeturn8search8turn3search7

**What this means for your benchmark: make Earth/space background change through the SNR chain, not through a hand-coded \(P_D\) cliff; retain a binary limb-step case only as a transparent sensitivity test.**

## Benchmark scenario design

### B1 ★ Established benchmark problems

**Answer — `CONSENSUS` that the Blair/Watson family and Li/Zhang multiple-model problems are genuine reusable classical benchmarks; `SINGLE-PAPER` for newer space/hypersonic scenarios; `UNKNOWN` for any equivalently canonical OPIR/HGV benchmark. Confidence: high.**

**[CONSENSUS] Blair, Watson, Kirubarajan and Bar-Shalom's radar-management/tracking benchmark is an actual benchmark rather than merely one paper's synthetic example.** The 1998 T-AES benchmark includes six target trajectories, highly maneuvering targets, missed detections, false alarms, ECM, finite sensor resolution and beam-management effects; the associated IMMPDAF solution paper evaluates tracking/radar-resource performance on the same benchmark. An earlier conference treatment states that the trajectory set includes lateral accelerations as high as roughly 7 g and longitudinal accelerations up to roughly 2 g. citeturn1search2turn1search0turn1search1

**[SINGLE-PAPER] Li and Zhang's 2000 T-AES paper is the central published source for the 13-model acceleration-grid/LMS family you have already reproduced.** Its importance for *your* benchmark is not that its deterministic switch cases should be reused as the only truth generator, but that it gives you an externally reproducible classical cost/accuracy reference. citeturn1search4 Your successful replication and the specific “fixed IMM accuracy at LMS-class cost” decision are documented in the submitted brief. fileciteturn0file0

**[SINGLE-PAPER] There are public space/hypersonic scenario definitions, but I would not call them community benchmarks in the Blair/Li sense.** A 2024 Aerospace Science and Technology study tracks an HGV with three space-based infrared sensors using explicit satellite orbital elements and an azimuth/elevation measurement model; a 2017 space-based IR focal-plane paper defines a ballistic-target simulation and compares point-angle versus finite-pixel observations. They are useful scenario references but I found no evidence of repeated reuse by independent groups as a standardized benchmark. citeturn23search6turn23search0

**[CONSENSUS] Singer's 1970 exponentially correlated acceleration process remains a foundational stochastic maneuver model, but it is a *model class*, not a single frozen benchmark scenario.** Li and Jilkov's T-AES multiple-model survey documents the broader maneuvering-target multiple-model tradition and the variable-structure branch. citeturn13search0turn15search5

**[UNKNOWN] I found no public, unclassified space-based-IR/HGV tracking benchmark with the same status as Blair/Watson—i.e., a frozen scenario definition, agreed measurement model, public truth, and repeated independent algorithm comparisons.**

**What this means for your benchmark: preserve Li–Zhang and Blair-style cases as regression/canonical tests, but present your OPIR/HGV suite as a new public benchmark definition rather than implying that an established space-based benchmark already exists.**

### B2 ★ Maneuver generation without artifact leakage

**Answer — `CONSENSUS` on using multiple physically/stochastically distinct motion models; `UNKNOWN` for a tracking-specific published “generator leakage” standard; `INFERRED` for the strongest protocol. Confidence: high on models, medium on leakage literature.**

**[SINGLE-PAPER] Singer's model replaces instantaneous deterministic acceleration switching with a stochastic, temporally correlated acceleration process.** Its central feature is finite acceleration correlation time, which makes maneuver evolution smoother and less trivially identifiable from a switch timestamp than piecewise-constant acceleration. citeturn13search0

**[SINGLE-PAPER] Semi-Markov multiple-model work explicitly treats mode sojourn time as information rather than assuming memoryless Markov switching.** That gives you a natural way to randomize maneuver duration and transition timing without a fixed Table-III-like script. citeturn13search16

**[CONSENSUS] Coordinated-turn models are also mainstream alternatives to Cartesian acceleration grids for curved motion.** Modern T-AES work still describes constant-turn motion as a standard maneuvering-target model and concentrates on estimating/adapting the turn-rate parameter, while the Li/Jilkov survey places such model diversity in the established multiple-model framework. citeturn15search1turn15search5

**[UNKNOWN] I did not locate a radar/sonar maneuvering-tracker paper that has become the canonical citation for “a neural tracker exploited artifacts of the synthetic truth generator.”** The concern is methodologically sound, but it appears ahead of the standard reporting practice in this subfield rather than codified by one tracking benchmark standard.

**[INFERRED] The least arguable design is a **generator matrix with whole-family holdout**.** Train on, for example, randomized semi-Markov acceleration segments plus Singer-like correlated acceleration; validate on disjoint parameter ranges; and reserve at least one qualitatively different family—smooth jerk-limited/coordinated-turn trajectories or a real/reconstructed trajectory library—for final test. Never let train and test differ only by RNG seed. That converts your concern from “did we randomize enough?” into the stronger question “does the policy survive a truth-generating mechanism it never saw?” citeturn13search0turn13search16turn15search1

**[INFERRED] Also randomize nuisance structure independently of maneuver state.** If every bank reversal coincides with a sensor handoff, low SNR, a fixed duration, or a specific acceleration amplitude, the learned selector can exploit that proxy. Factor maneuver parameters, constellation phase, measurement noise, clutter seed, detection seed and timing phase independently wherever physics does not require correlation.

**What this means for your benchmark: your headline held-out test should contain an entire maneuver-generator family absent from training; a fresh random seed from the same piecewise-constant generator is not enough.**

### B3 ★ Public HGV maneuver characterization

**Answer — `CONSENSUS` that the public weapon-specific technical literature is sparse; `SINGLE-PAPER` for useful additions; confidence: medium-high because absence claims are inherently difficult.**

**[CONSENSUS] The public literature I found beyond the Tracy/Wright and Acton material in your possession adds useful *constraints and qualitative behavior*, but not a rich empirical distribution of bank-reversal periods, lateral-g histories or skip-cycle timing.** Acton's 2015 Science & Global Security work uses an analytic boost-glide model and public HTV-2 test information; Wright and Tracy's 2023 follow-on explicitly studies maneuvering costs in range and glide speed. These are strong public technical sources, but neither provides a representative stochastic maneuver-telemetry database. citeturn19search12turn19search3

**[SINGLE-PAPER] Wright and Tracy's 2023 analysis is especially useful as a *physics guardrail*: maneuvering is not free; it incurs range/speed penalties.** That argues against a benchmark generator that draws sustained lateral acceleration independently of energy state. citeturn19search3

**[SINGLE-PAPER] Public NASA entry literature independently demonstrates the generic aerodynamic-control mechanism of periodic bank reversals in hypersonic entry flight.** NASA describes bank-angle magnitude controlling longitudinal motion and periodic sign reversals limiting lateral error in guided atmospheric entry. That is useful for establishing that reversal-like maneuvering is physically conventional for lifting hypersonic vehicles, but it should **not** be represented as data about any weapon. citeturn19search5turn19search11

**[UNKNOWN] I did not find a trustworthy public source establishing a weapon-generic bank-reversal period distribution, a validated “1–4 g for N seconds” distribution, or a public skip amplitude/period distribution suitable for treating as ground truth.** I would therefore not make such numbers proposal facts unless they come directly from the BRSL/Tracy-Wright model you already hold.

**[INFERRED] Use the public HGV literature as an **envelope constraint**, not an empirical prior.** Generate trajectories through a physically consistent glide model, vary control histories within public plausible envelopes, enforce the energy/range consequences of maneuver, and report the control-law distribution as a benchmark choice. The held-out family can use a different control-history generator while satisfying the same public dynamics. citeturn19search12turn19search3

**What this means for your benchmark: do not invent a “public HGV maneuver distribution”; keep BRSL/Tracy-Wright/Acton as the weapon-relevant public basis and use NASA hypersonic-entry reconstructions only as generic maneuver-shape sanity checks.**

### B4 Held-out scenario families

**Answer — `SINGLE-PAPER` evidence exists for out-of-distribution trajectory splits in newer ML tracking; `UNKNOWN` for an established radar/sonar standard equivalent to MOTChallenge; `INFERRED` protocol recommended. Confidence: medium.**

**[UNKNOWN] I did not find a radar/sonar target-tracking counterpart to MOTChallenge that mandates a universal train/validation/test partition by maneuver family, geometry, SNR and sensor timing.** Stone Soup is a tracking-development framework rather than a governing benchmark standard. Its current upstream repository describes it as a framework for developing/testing tracking algorithms. fileciteturn2file0L2-L10

**[SINGLE-PAPER] Recent learned-tracking papers are beginning to test beyond the precise trajectory distribution used for training, but protocols remain paper-specific rather than standardized.** That makes a stronger split an opportunity for your proposal rather than a departure from an existing norm. citeturn5search6

**[INFERRED] Use four orthogonal holdouts, with the first two mandatory:** **generator-family holdout**; **geometry holdout** by convergence-angle/constellation-phase regions; noise/background extrapolation; and maneuver-intensity extrapolation. Reserve one final “sealed” Cartesian product of unseen generator × geometry × sensor condition and do not use it for model selection.

**[INFERRED] Report interpolation and extrapolation separately.** A learner that wins only on unseen seeds inside the training envelope has demonstrated sample efficiency, not broad scenario generalisation. A learner that remains competitive on unseen dynamics families and low-convergence geometries supports the stronger feasibility claim you need.

**What this means for your benchmark: define the split in terms of latent scenario families before generating samples, not by randomly splitting individual trajectories after generation.**

## Evaluation protocol

### C1 ★ Statistical methodology

**Answer — `CONSENSUS` that Monte Carlo uncertainty and covariance consistency are evaluated statistically; `UNKNOWN` for a single IEEE/FUSION-mandated run count; `INFERRED` for the recommended paired protocol. Confidence: high.**

**[CONSENSUS] There is no evidence of a universal “500 runs” rule.** Published work uses substantially different counts according to computational burden and the problem being evaluated: a current IET tracking study uses 200 Monte Carlo runs and explicitly evaluates NEES against finite-sample confidence limits; another IEEE control study uses 1,000 iterations per configuration “to provide statistical confidence.” The meaningful requirement is therefore uncertainty of the reported effect, not a ritual sample count. citeturn18search12turn18search6

**[CONSENSUS] NEES/ANEES with \(\chi^2\)-based bounds is established practice for testing whether filter-reported covariance is statistically credible.** Recent tracking/fusion papers continue to use RMSE plus NEES and finite-sample confidence bounds, rather than accepting a covariance matrix merely because the filter emits one. citeturn18search12turn18search5

**[INFERRED] Run the ML selector and every baseline on **the same Monte Carlo realization**: identical truth, sensor availability, measurement-noise draws, detection/miss draws, clutter draws and timestamps.** Then compute per-run differences. This paired design isolates algorithmic differences far more cleanly than giving each method independent random worlds.

**[INFERRED] Freeze a minimum such as 500 paired runs for comparability with your Li–Zhang replication, but make the actual stopping criterion statistical: continue the high-priority scenario cells until the 95% confidence interval on the *paired difference* in your primary accuracy metric is narrower than a predeclared practically relevant tolerance.** Report both the estimate and interval. For skewed metrics such as peak error, track-loss rate or latency, use empirical quantiles/confidence intervals rather than only mean ± standard deviation.

**[INFERRED] Predeclare the hierarchy:** primary endpoint such as time-averaged position error or an operational custody metric; co-primary cost endpoint; secondary NEES, peak error, mode calibration, latency, and resilience metrics. This prevents choosing whichever metric happens to favor the learned policy after the run.

**What this means for your benchmark: keep 500 as a minimum/reproducibility anchor, but replace “500 point estimates” with paired common-seed comparisons, 95% intervals, and explicit NEES consistency bounds.**

### C2 ★ Baseline fairness

**Answer — `INFERRED` best practice is to publish both replicated-original and tuned baselines; `UNKNOWN` for a canonical tracking paper later formally invalidated solely because its IMM was under-tuned. Confidence: medium.**

**[CONSENSUS] IMM performance materially depends on the model bank and transition/process-noise assumptions; adaptive-transition and adaptive-turn-rate papers exist precisely because those choices affect performance.** Recent T-AES work estimates turn rate online, and classical adaptive-TPM work updates transition probabilities rather than treating them as universally fixed. citeturn15search1turn4search11

**[INFERRED] Use **two named classical baselines**.** Baseline A is the literature-replication configuration—the exact Li/Zhang-compatible configuration you have already verified. Baseline B is a tuned classical oracle-within-reason: tune transition probabilities, model-grid/process-noise parameters and LMS thresholds on the same training/validation scenario families available to ML, never on the sealed test set. Report the tuning domain and final parameters. citeturn1search4turn4search11

**[INFERRED] This gives the reviewer two valid comparisons:** “does ML beat the historically recognized baseline?” and the more important “does ML still beat a classical method after equal tuning effort?” If the learned policy beats only Baseline A, you have learned something useful about tuning but not demonstrated an intrinsically better selector.

**[UNKNOWN] I did not identify a well-documented maneuvering-target-tracking case in the primary literature where an ML-vs-IMM performance claim was later formally overturned because the authors had under-tuned IMM.** Do not manufacture such a cautionary citation. The generic failure mode is plausible; the requested clean historical example did not emerge from this search.

**What this means for your benchmark: publish both your replicated historical IMM/LMS and a validation-tuned classical baseline, with identical test seeds and computational accounting; do not rely on an “ML versus default IMM” result.**

### C3 Metrics

**Answer — `CONSENSUS` for GOSPA's role in multitarget evaluation and NEES for consistency; `INFERRED` for the proposed mode-explanation metrics. Confidence: high.**

**[CONSENSUS] GOSPA was introduced specifically to improve decomposition of multitarget error into localization error plus missed and false targets rather than inherit OSPA's less intuitive normalization/cardinality behavior.** The original 2017 FUSION paper makes that motivation explicit, and GOSPA-derived metrics continue to appear in current T-AES work. citeturn16search0turn15search0

**[INFERRED] For your principal **single-target, known-truth maneuver benchmark**, OSPA/GOSPA adds little unless track existence, false tracks or multitarget association are part of the experiment.** Use GOSPA in clutter scenarios where the tracker can instantiate false tracks or lose/reacquire the target; do not force it into a pure single-state-estimation experiment merely because it is modern. The original GOSPA motivation is explicitly multi-object cardinality/localization performance. citeturn16search0

**[CONSENSUS] RMSE and NEES are a sound pair because they answer different questions: accuracy and uncertainty credibility.** Current filtering papers routinely report both and evaluate NEES against statistical confidence regions. citeturn18search12turn18search5

**[INFERRED] I would expand the single-target scorecard to:** position/velocity RMSE and time-resolved error; 95th/99th-percentile and maximum transient error around maneuver onset; custody/track-loss and reacquisition time; ANEES/NEES violation rate; compute/FLOPs and wall latency; and your topic-level coverage/resilience measures. “Peak error” is useful operationally, but I did not find evidence that RMSE + NEES + peak error is a formally standardized trio.

**[UNKNOWN] I found no tracking-specific standard for scoring the *calibration* of IMM mode probabilities as explanations.** Li/Zhang-style mode-identification percentages tell whether the highest-probability model matches a labeled maneuver, but they do not tell whether a reported 0.8 probability is correct 80% of the time. citeturn1search4

**[INFERRED] If your simulator assigns an unambiguous latent mode label, score model probabilities with a proper probabilistic score—multiclass negative log likelihood is the simplest—and plot reliability/calibration curves in addition to top-mode accuracy.** Recent state-estimation work already argues for combining NEES with proper scoring rules such as NLL when assessing uncertainty credibility. For cases in which truth does *not* map uniquely onto one bank model, do not pretend there is a true mode; instead score whether the mixture predictive distribution is calibrated. citeturn18academia46

**What this means for your benchmark: use RMSE/transient error + NEES as core single-target metrics, GOSPA only when existence/false tracks matter, and add probability calibration—not merely “percent correct mode”—as the quantitative explainability metric.**

### C4 ★ Sim-to-real credibility at TRL 3

**Answer — `CONSENSUS` that ADS-B is already used as real-aircraft reference/ground truth in radar research; `INFERRED` that your proposed anchor is valuable but must be scoped correctly. Confidence: high.**

**[CONSENSUS] There is direct precedent for using ADS-B as a truth/reference source in sensing and tracking experiments.** A 2024 high-frequency-radar experiment uses civil-aircraft ADS-B position, speed, heading and identity as ground truth after temporal alignment; ONERA researchers have used OpenSky ADS-B as the ground-truth position/velocity metadata for measured radar signatures; and an IEEE conference study tests IMM-KF variants on real ADS-B aircraft measurements after synthetic maneuver experiments. citeturn20search0turn20search8turn20search12

**[CONSENSUS] ADS-B is not perfect independent metrology.** The OpenSky-derived LocaRDS dataset explicitly warns that aircraft-reported GNSS locations can have offsets/delay, provides quality indicators, and describes its verification process rather than claiming infallible truth. citeturn20search9

**[INFERRED] Your 26-million-row OpenSky corpus is therefore a strong TRL-3 *sanity anchor*, especially because it supplies real maneuver timing, traffic density and asynchronous identity-preserving tracks.** It is not evidence that aircraft dynamics resemble an HGV or that ADS-B errors resemble OPIR errors. Use it to ask narrower questions: does the selector behave pathologically on real kinematic time series? Are inferred mode probabilities stable/calibrated across ordinary turns? Does the architecture maintain custody through missing reports? Do synthetic aircraft-like trajectories generate comparable switching/error statistics?

**[INFERRED] A particularly clean experiment is to use ADS-B states as truth, place your *notional satellites* around them, synthetically generate LOS measurements with the exact same measurement code used in the HGV benchmark, and compare tracker behavior against synthetic aircraft trajectories matched in speed-normalized curvature and maneuver duration.** That anchors motion irregularity in real data while keeping the sensor model controlled.

**What this means for your benchmark: absolutely use the OpenSky corpus, but call it a kinematic/sim-to-real sanity anchor rather than HGV validation; filter on ADS-B quality and preserve a clear boundary between real motion and synthetic OPIR sensing.**

## Angles-only fusion architecture

### D1 ★ Converted measurement versus nonlinear filtering

**Answer — `CONSENSUS` that passive-LOS conversion can be biased/non-Gaussian and requires explicit debiasing/covariance treatment; `UNKNOWN` for a universal 5°/10°/20° cutoff; confidence: high.**

**[CONSENSUS] Lerro and Bar-Shalom established the general principle that nonlinear measurement-to-Cartesian conversion can introduce bias and inconsistent covariance, motivating debiased consistent converted measurements rather than naive conversion.** Their classic 1993 T-AES work concerns polar range/bearing conversion, so it should **not** by itself be cited as proof that two-LOS stereo triangulation is safe. citeturn2search0

**[SINGLE-PAPER] Much more directly relevant is Kowalski, Bar-Shalom, Willett and Fair's 2022 work on passive sensors.** They treat Cartesian conversion from multiple passive lines of sight using a closest-point-of-approach construction and explicitly address conversion bias/improper covariance caused by the nonlinear LOS geometry, including a second-order treatment. citeturn2search3

**[INFERRED] That literature does **not** justify “intersect two rays, attach a first-order covariance, feed the result to a linear IMM” at low convergence angle.** As your known \(1/\sin\alpha\) geometry becomes ill conditioned, the posterior along the weak range direction becomes elongated and increasingly non-Gaussian; a Gaussian pseudo-position can then carry more apparent information than the LOS actually contained. The 2022 passive-sensor conversion work is evidence that this nonlinear conversion error is significant enough to require special treatment. citeturn2search3

**[UNKNOWN] I found no primary source establishing a universal boundary at 5°, 10° or 20° below which converted measurements are mathematically forbidden.** The validity threshold depends on angular noise, range, baseline and the conversion method.

**[INFERRED] You can keep the verified *linear IMM motion bank* if you make the sensor front end responsible for this issue.** For each geometry bin, Monte Carlo the angular-noise distribution through the stereo conversion and test bias, covariance and NEES. Accept a Cartesian pseudo-measurement only where the converted Gaussian passes a predeclared consistency criterion. At poor geometry, either use a second-order/unbiased passive conversion or perform the measurement update on raw angles in a nonlinear mode-matched filter. citeturn2search3

**[INFERRED] This is stronger than choosing EKF versus UKF by taste: the conversion is admitted or rejected by an empirical consistency test.** Your already-verified linear IMM can remain the canonical dynamics implementation over the geometry where that front end is demonstrably consistent.

**What this means for your benchmark: keep the linear IMM only behind a geometry-tested, bias-aware LOS-to-Cartesian conversion; do not use naive triangulation at 5–20° and assume its error is Gaussian.**

### D2 ★ Single-sensor epochs

**Answer — `CONSENSUS` that bearings-only information can be processed directly and asynchronously rather than automatically discarded; confidence: high.**

**[SINGLE-PAPER] The 2007 FUSION asynchronous-bearings paper uses a **range-parameterized UKF** so multiple moving sensors can contribute bearings as they arrive, rather than waiting for synchronous pairs.** citeturn14search1

**[SINGLE-PAPER] Range-parameterized nonlinear filters have likewise been developed specifically for bearings-only tracking, preserving uncertainty over the poorly observed range dimension rather than forcing an immediate Cartesian point estimate.** citeturn2search7

**[CONSENSUS] More generally, multisensor tracking literature supports sequential/raw-measurement updates from heterogeneous sensors and asynchronous measurements.** A T-AES multisensor IMMPDA study feeds raw sensor measurements to a central estimator, while later T-AES work handles asynchronous measurements and bias jointly. citeturn15search11turn15search12

**[INFERRED] For an already-established track, **do not coast merely because stereo disappeared**.** Propagate normally and apply the single LOS as a weak nonlinear constraint; it contains cross-range information even though instantaneous range remains weakly observed. Coast only when the LOS is absent or deliberately gated out. This also prevents your “coverage” metric from collapsing stereo coverage and track custody into the same concept.

**[INFERRED] If preserving one common IMM implementation matters more than exact Bayesian elegance in Phase I, an acceptable architecture is dual-path: stereo epochs produce vetted Cartesian pseudo-measurements for the verified linear IMM; single-sensor epochs run a raw-bearing update or a range-parameterized side filter whose posterior is fused back conservatively.** Benchmark it against an all-raw-angle nonlinear implementation before choosing it as the production architecture.

**What this means for your benchmark: single-satellite visibility should be a bearings-only update case, not automatically a coast; include long intermittent-stereo stretches because they materially test covariance credibility and model selection.**

### D3 Cross-validation implementations

**Answer — `CONSENSUS` on Stone Soup's allowable license; `UNKNOWN` on a published angles-only result that can serve as a numerical verification vector analogous to your FilterPy IMM cross-check. Confidence: high.**

**[SINGLE-PAPER/SOFTWARE-DOCUMENTATION] One correction to the brief: the current upstream `dstl/Stone-Soup` repository reports an **MIT license**, not Apache-2.0.** MIT satisfies your commercial-license constraint, and the repository describes Stone Soup as a framework for development and testing of target-tracking algorithms. fileciteturn2file0L2-L10

**[UNKNOWN] I did not identify a peer-reviewed Stone Soup bearings-only example that publishes reference numerical state/covariance values suitable for a machine-precision validation in the way FilterPy supplied your IMM comparison.** Example code is still useful for an independent implementation check, but that is weaker than reproducing a paper's table.

**[INFERRED] Use Stone Soup as an **independent implementation oracle**, not as the truth definition: generate the same fixed bearing sequence, initial prior and sensor trajectories; compare raw-angle EKF/UKF state and innovation sequences; then separately validate stereo conversion against Kowalski et al.'s passive-LOS conversion formulation.** That creates two independent checks of different parts of the pipeline. citeturn2search3

**What this means for your benchmark: Stone Soup is currently license-compatible (MIT) and useful for cross-implementation testing, but I would not claim a published Stone-Soup bearings-only verification standard unless you reproduce a specific peer-reviewed case yourself.**

## Learned multiple-model prior art and novelty

### E1 ★ What already exists

**Answer — `CONSENSUS` that ML has already been inserted into several parts of the multiple-model pipeline; confidence: high. The prior-art landscape is materially closer to your contribution than a generic “KalmanNet exists” statement suggests.**

| Work | Label | What is learned | Classical structure/baseline | Reported result relevant here | Covariance consistency? |
|---|---|---|---|---|---|
| **Deep-Q-Network VSIMM, IFAC-PapersOnLine, 2025** | `SINGLE-PAPER` | Model-set-adaptation/model-selection policy in a **variable-structure IMM** | VSIMM | Offline DQN learning + online model-selection deployment; this is direct broad prior art against “learned model-set adaptation” | **Not established in the public abstract I located**. citeturn5search7 |
| **Adaptive CNN–LSTM TPM, IET Radar, Sonar & Navigation, 2026** | `SINGLE-PAPER` | Time-varying IMM transition-probability matrix using state estimates, observations and model probabilities | IMM-UKF | Reports roughly low-teens percentage position improvement and around twenty-percent velocity improvement in its scenarios | No NEES result found in the indexed primary page. citeturn4search0 |
| **LSTM–IMM, Aerospace, 2026** | `SINGLE-PAPER` | Time-varying transition matrix / mode recognition | IMM | Simulation reports improved tracking/mode identification in a missile-guidance context | No covariance-consistency result found. citeturn4search2 |
| **IMMNet, 2026** | `SINGLE-PAPER` | KalmanNet-like mode filters plus Transformer model classifier/probabilities | CV/CA/CT-style IMM bank | Retains explicit candidate motion models and model-probability output while replacing major analytic pieces with learned components | No NEES/covariance-consistency evidence located. citeturn6view2 |
| **DNC-IMM, 2026** | `SINGLE-PAPER` | Neural calibration of transition probabilities and measurement likelihoods | IMM | Final mode posterior remains an explicit output | No NEES result located. citeturn4academia42 |
| **Screened IMM-GRU, Sensors, 2026** | `SINGLE-PAPER` | GRU-based mode priors/classification plus screening logic | IMM | Preserves an IMM-like interpretable structure and uses variance/disagreement information | Not the same as reporting classical covariance consistency/NEES. citeturn7search13 |
| **KalmanNet, IEEE T-SP, 2022** | `SINGLE-PAPER` | Recurrent network learns the Kalman-gain mapping inside a model-based recursion | KF/EKF-family comparators | Important hybrid model/data-driven precedent, but **not an IMM model-set selector** | Original contribution is not a classical IMM covariance-consistency benchmark. citeturn7search0 |
| **RNN radar tracker, IEEE RadarConf, 2018** | `SINGLE-PAPER` | Recurrent state-tracking behavior | Conventional radar-tracking comparators | Shows the older end-to-end/data-driven maneuver-tracking branch | Not evidence of learned VSIMM selection. citeturn7search12 |
| **Adaptive TPM IMM, IEEE T-SMC Systems, 2019/2021** | `SINGLE-PAPER` | **Not ML**: Bayesian/algorithmic online TPM adaptation | IMM | Important fairness baseline showing that transition adaptation itself predates neural solutions | Classical covariance machinery retained. citeturn4search11 |

**[CONSENSUS] The field has therefore learned at least four distinct things: transition probabilities, mode priors/posteriors, filter correction/gain behavior, and now model-set selection itself.** That conclusion is supported independently by the DQN-VSIMM, CNN-LSTM-TPM, IMMNet and KalmanNet lines. citeturn5search7turn4search0turn6view2turn7search0

**[INFERRED] Your strongest distinction is *not* “we put ML into an IMM.”** It is closer to: *learn the computational model-set-selection decision while deliberately leaving each mode-matched classical filter, Bayesian mode likelihood/probability calculation, output mixture and covariance representation intact; evaluate the policy under equal-compute classical tuning, held-out maneuver generators and OPIR angles-only measurement failures.* That combination is much narrower and more defensible.

**What this means for your benchmark: benchmark against both classical VSIMM/LMS and at least one learned-TPM/mode-prior approach; the experiment must show that learning the active model set gives value beyond simply adapting transition probabilities.**

### E2 ★ Variable structure specifically

**Answer — `SINGLE-PAPER`: yes, learned VSIMM model-set adaptation already exists. Confidence: high because the paper's abstract states the overlap explicitly.**

**[SINGLE-PAPER] The critical prior art is “Variable Structure Interacting Multiple-Model Filtering Based on Deep Q-Network,” IFAC-PapersOnLine, 2025.** Its abstract explicitly identifies **model-set adaptation (MSA)** as a core VSIMM problem and proposes a DQN-based adaptive VSIMM in which the model-selection strategy is optimized offline through experience replay and deployed online. citeturn5search7

**[CONSENSUS] This sits on top of a pre-existing non-neural variable-structure literature in which the model set itself is adapted.** Recent intent-assisted VSIMM work uses directed-graph/model-set switching, while earlier BMA/EMA variable-structure approaches select or augment models algorithmically. The 2005 Li/Jilkov T-AES survey already treats variable-structure multiple-model estimation as a mature third-generation branch. citeturn5search0turn5search1turn15search5

**[INFERRED] Consequently, these novelty formulations are unsafe: “first learned VSIMM,” “first learned model-set adaptation,” or “first reinforcement-learning model selector for an IMM.”** The 2025 paper directly occupies those broad claims. citeturn5search7

**[UNKNOWN] From the public abstract available to me, I cannot establish whether that DQN work specifically learns an LMS adjacency graph, learns Li–Zhang activation/termination thresholds themselves, or merely learns the higher-level action “which models should be active next.”** That distinction requires full-paper claim-charting before you make a narrower novelty statement.

**[INFERRED] A more defensible provisional claim is:** *learned replacement for the LMS-style hand-designed selection heuristic in an otherwise classical, covariance-producing IMM, evaluated for asynchronous angles-only space sensing with explicit equal-cost comparison, out-of-generator generalization, explainable mode probabilities and covariance-consistency requirements.* Each qualifier matters; do not collapse it into “learned model-set adaptation.” citeturn5search7turn15search5

**What this means for your benchmark: treat the 2025 DQN-VSIMM paper as a mandatory baseline/prior-art citation and narrow your novelty to the exact retained-classical architecture, LMS-specific policy target, OPIR geometry, cost matching, generalisation protocol and confidence/explainability evaluation.**

### E3 Explainability-preserving learned trackers

**Answer — `SINGLE-PAPER` examples preserve mode probabilities; `UNKNOWN` for a learned-IMM paper that also satisfies a strong NEES-style covariance-consistency requirement. Confidence: medium-high.**

**[CONSENSUS] Learned hybrid IMM papers can preserve an interpretable discrete-mode output.** IMMNet retains a predefined motion-model bank and outputs model probabilities through a learned classifier; DNC-IMM calibrates transition/likelihood machinery while retaining the IMM posterior; the screened IMM-GRU likewise keeps the surrounding multiple-model structure rather than replacing the tracker with a black-box state regressor. citeturn6view2turn4academia42turn7search13

**[UNKNOWN] In the learned-IMM sources I located, I did not find the combination you specifically want: explicit mode-probability explanation **and** a reported NEES/ANEES or equivalent statistical test demonstrating that the state covariance remains consistent after learning.** “Prediction variance,” network disagreement or RMSE is not the same claim as normalized estimation error lying within its theoretical confidence region. citeturn7search13turn18search12

**[INFERRED] This is a meaningful differentiation opportunity.** Because your learned component chooses the active hypothesis set but does not replace the filter equations/covariance update, you can test whether learned selection preserves statistical credibility. The correct claim would be empirical—“ANEES remains within/near predeclared bounds under these conditions”—not structural—“classical covariance is automatically consistent because a Kalman filter remains inside.” Model-set misspecification can still make a classical covariance overconfident. citeturn18search12turn18academia46

**What this means for your benchmark: make NEES/ANEES a gating metric, not a decorative plot; a learned selector should not count as a win if lower RMSE is purchased with materially overconfident covariance.**

### E4 OPIR-specific ML tracking

**Answer — `UNKNOWN` for direct unclassified learned-OPIR tracking prior art after this sweep; `CONSENSUS` that public non-ML space-IR/HGV tracking simulations exist. Confidence: medium because conference indexing is incomplete.**

**[CONSENSUS] Public literature does contain space-based IR tracking scenarios relevant to your simulator.** The 2024 Aerospace Science and Technology HGV study explicitly uses three space-based infrared sensors and azimuth/elevation measurements; a 2023 multi-satellite space-IR paper studies velocity estimation of dim targets; and the 2017 ballistic-target PHD work uses a space-based IR focal-plane measurement model. citeturn23search6turn23search3turn23search0

**[UNKNOWN] I did not locate an unclassified AMOS/SPIE/AIAA/FUSION/IEEE primary paper in this sweep whose central contribution is a learned IMM/model-set tracking method for an operationally representative space-based missile-warning OPIR problem.** That is not proof of absence: AMOS/MSS and defense-conference coverage is less uniformly indexed than IEEE journals.

**[INFERRED] Phrase the proposal cautiously:** “We found substantial ML-augmented maneuvering-tracker prior art and public space-IR tracking studies, but did not identify a public work combining learned LMS/VSIMM-style model-set adaptation with the proposed asynchronous angles-only OPIR benchmark and covariance-consistency requirement.” That is supportable; “no one has applied AI to OPIR tracking” is not.

**What this means for your benchmark: position OPIR as the demanding application/test regime, not as the sole source of novelty, and keep a documented search log because the prior-art conclusion is necessarily an open-literature conclusion.**

## Real-data anchors and recommended benchmark freeze

### F1 Public angles-only data with truth

**Answer — `UNKNOWN` for a clean public multi-sensor bearings-only tracking dataset with independent high-accuracy truth matching your need; `SINGLE-PAPER` for partial anchors. Confidence: medium.**

**[SINGLE-PAPER] The Steward Observatory LEO Satellite Photometric Survey is genuinely useful public observational data: it includes photometric and **astrometric** measurements of Starlink and OneWeb satellites collected from 2020–2022.** However, its published inclusion criterion is measured position error below 0.5°, which is orders of magnitude too coarse to serve as a µrad-class numerical validation target for your tracker. citeturn22search6turn22search9

**[SINGLE-PAPER] Stanford's SAMUS work is highly relevant algorithmically—it performs autonomous spaceborne angles-only multitarget tracking and tests noise, eclipses and partially known maneuvers—but its reported evaluation is high-fidelity simulation, not the public real-observation-with-independent-truth dataset you asked for.** citeturn22academia30

**[CONSENSUS] High-quality orbit-reference data do exist publicly in adjacent measurement domains.** NASA's CDDIS distributes satellite-laser-ranging observations supporting very accurate orbit determination, and NASA/JPL distributes DORIS tracking data and precise orbit ephemeris products for missions such as SWOT. Those are valuable independent ephemeris sources, but SLR/DORIS measurements are not passive bearing streams. citeturn22search3turn22search7

**[UNKNOWN] I therefore did not find the “golden dataset”: timestamped bearings from two or more separated passive sensors, calibrated sensor poses, and independently accurate Cartesian truth, all public and easy to redistribute.**

**[INFERRED] The practical real-data anchor is a hybrid:** use public optical astrometry to exercise ingestion/calibration paths; use precise public ephemerides where available to establish reference states; and use your ADS-B corpus to provide rich real maneuver kinematics from which you generate synthetic satellite LOS. Do not claim the resulting measurement stream itself is real OPIR.

**What this means for your benchmark: proceed without waiting for a nonexistent-looking perfect angles-only dataset; use optical astrometry/precise-orbit data for sensor-path sanity checks and ADS-B-derived LOS as the stronger real-kinematics anchor.**

### F2 Public high-speed maneuvering trajectories

**Answer — `CONSENSUS` that NASA provides several public high-speed flight reconstructions suitable for non-weapon maneuver-statistics anchoring; confidence: high.**

**[SINGLE-PAPER] NASA's X-43A record is unusually useful.** The Mach-7 flight data include repeated pitch, yaw and roll doublets, frequency sweeps, and pull-up/push-over maneuvers over a wide Mach range, explicitly for extracting flight aerodynamics. NASA marks the record public/public-use-permitted. citeturn21search0turn21search6

**[SINGLE-PAPER] NASA also published the Mach-10 X-43A trajectory-reconstruction methodology, using inertial measurements plus redundant vehicle-state observations in an extended Kalman filter/smoother to obtain a best-estimated flight trajectory.** This is exactly the kind of independently reconstructed high-speed trajectory that can anchor maneuver bandwidth and smoothness without modeling a weapon. citeturn21search8

**[CONSENSUS] Space Shuttle Best Estimate Trajectory products offer an even longer atmospheric-entry record.** NASA documents STS-1 reconstruction from about 180 km to landing using onboard accelerometer/gyro and ground tracking, and later BET products contain reconstructed state histories; one STS-13 product explicitly documents a two-second-spaced trajectory/air-data listing. citeturn21search1turn21search7

**[SINGLE-PAPER] LOFTID supplies a much newer public re-entry example.** NASA's 2022 flight test was reconstructed after flight from available instrumentation despite loss of one IMU recorder stream, and the accepted Journal of Spacecraft and Rockets work reports the reconstructed flight performance. citeturn21search4turn21search9

**[INFERRED] These records should anchor **statistics**, not be used as surrogate HGV trajectories.** Useful non-weapon quantities include acceleration autocorrelation time, jerk distribution, turn/slew duration, spectral content and how smooth real controlled hypersonic motion is relative to instantaneous acceleration steps. X-43 is especially valuable because deliberate identification maneuvers are explicitly present. citeturn21search0turn21search15

**What this means for your benchmark: add X-43A and Shuttle/LOFTID reconstructed trajectories as non-weapon “reality checks” on maneuver smoothness and temporal spectra; they are public, technically documented, and much better leakage detectors than another synthetic seed.**

### The five changes I would make before freezing the benchmark

**[INFERRED] Priority one — change the novelty claim and add the 2025 DQN-VSIMM baseline.** The discovery that matters most for the proposal is that learned VSIMM model-set adaptation is already published. Your contribution must therefore be narrower: LMS-style selection inside an otherwise classical covariance-producing tracker, OPIR angles-only operation, equal-cost baseline fairness, generator-family generalisation, and quantitative explanation/confidence. citeturn5search7

**What this means for your benchmark: implement or faithfully approximate the DQN-VSIMM prior art as a comparator before claiming novelty.**

**[INFERRED] Priority two — freeze a multi-family truth generator and seal one family from ML development.** Keep Li–Zhang's deterministic cases as regression tests, but build the headline suite from at least stochastic correlated acceleration/Singer-like behavior, randomized-duration/semi-Markov maneuvers, physically generated HGV trajectories, and a smooth/real-trajectory family; hold one complete family out. citeturn13search0turn13search16turn19search3

**What this means for your benchmark: “unseen seed” is no longer sufficient evidence of generalisation; require “unseen generator.”**

**[INFERRED] Priority three — split sensor realism into a controlled core and a radiometric stress suite.** The core uses frozen \(\sigma_\theta\), constant \(P_D\), homogeneous Poisson clutter and controlled cadence. The stress suite ties background/range/transmission to SNR and \(P_D\), uses structured real-image-derived clutter, asynchronous timestamps, attitude bias and limb transitions. This lets you say exactly which performance gains survive realism without making unsupported claims about classified sensors. citeturn3search7turn8search8turn14search12

**What this means for your benchmark: never let one opaque “realistic sensor” configuration be the sole number to beat.**

**[INFERRED] Priority four — make covariance consistency and low-convergence geometry acceptance tests.** Bin performance by stereo convergence angle; validate the converted-measurement bias/covariance in each bin; fall back to raw-bearing/range-parameterized processing where conversion fails. Score ANEES with confidence bounds beside RMSE. citeturn2search3turn14search1turn18search12

**What this means for your benchmark: an ML accuracy win is invalid as a confidence-preserving win if its covariance becomes systematically overconfident or if it depends on an inconsistent stereo pseudo-measurement.**

**[INFERRED] Priority five — pre-register the comparison protocol and add real kinematic anchors.** Run classical and learned methods on identical seeds, report paired effect sizes and 95% intervals, publish both literature-replica and tuned classical baselines, and reserve the OpenSky plus X-43/Shuttle-derived tests until the design is frozen. ADS-B already has precedent as radar ground truth/reference data, while NASA's reconstructed high-speed flights give you a public check on the temporal character of real maneuvers. citeturn20search0turn20search8turn21search0turn21search8

**What this means for your benchmark: the frozen number to beat should be a vector—accuracy, consistency, computational cost, transient resilience and probability calibration with uncertainty—not one mean RMS error.**