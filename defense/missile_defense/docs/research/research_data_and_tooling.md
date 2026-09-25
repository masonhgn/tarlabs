# Open-Source Data & Tooling Guide: Multi-Orbit Missile-Warning Trade-Space Simulation (DAF26BX06-NV510)

## TL;DR
- **Yes, deep research pays off — but only in two narrow places.** You can build a *credible, realistic* multi-orbit missile-warning trade study almost entirely from public data today: real orbital elements for SBIRS/DSP (GEO) and the SDA Tranche 0 Tracking Layer + HBTSS (LEO) are publicly cataloged (NORAD IDs and live TLEs on n2yo/Space-Track/CelesTrak), and published boost-glide/ballistic equations of motion (Tracy & Wright; Fetter; Gronlund & Wright) give you validated threat trajectories with numeric parameters. The two data questions that actually move the trade study are (1) the **notional LEO Walker geometry** (planes/sats-per-plane/altitude/inclination) and (2) the **detection-threshold / IR-signature** assumption — both largely classified and to be *parameterized*, not hunted.
- **Get data now:** CelesTrak GP API (`gp.php?GROUP=...&FORMAT=...`, anonymous), Space-Track REST API (free registration, <30 req/min & <300 req/hr), GOES ABI L1b IR radiances (free on AWS S3), and the Berkeley/MIT HGV simulator + Science & Global Security papers (open PDFs). Software: Stone Soup (tracking/metrics), python-sgp4/Skyfield/`sgp4` Rust crate (propagation), Orekit/Basilisk (astrodynamics) — all permissively licensed except a few GPL traps.
- **Compliance:** A trade study built *entirely* from already-public data (published papers, public TLEs, unclassified fact sheets) sits in the ITAR "public domain" carve-out (22 CFR 120.34). The real risk is not the math — it's aggregating public data into a product a reviewer would treat as new controlled technical data, plus Space-Track's redistribution restriction. Keep raw Space-Track pulls and any customer-supplied threat parameters out of a public repo; publish only derived products and code that operates on published equations.

---

## Key Findings

1. **The public catalog is richer than most assume.** All four SpaceX "BB"/T0TR Tranche 0 Tracking Layer satellites are publicly cataloged **with live TLEs**: BB 1 (NORAD 56171, 2023-050K), BB 2 (56170, 2023-050J), BB 3 (57760, 2023-133D), BB 4 (57757, 2023-133B). The L3Harris "Raptor" T0TR sats and both MDA HBTSS prototypes (HBTSS-SV2 58955/2024-028A, HBTSS-SV1 58960/2024-028F) are also public. SBIRS GEO-1 through GEO-6 (37481, 39120, 41937, 43162, 48618, 53355) and DSP satellites (e.g., DSP-23 = NORAD 32287) are all cataloged. **None of these are withheld.**
2. **There is NO dedicated CelesTrak group for SDA/PWSA/Tranche/missile-warning.** The relevant generic group is `military` ("Miscellaneous Military"). You pull the specific sats by catalog number (`CATNR`) or international designator (`INTDES`).
3. **The threat models are fully public with usable numbers.** Tracy & Wright (S&GS 28, 2020) give the six coupled equations of motion for boost-glide over a spherical non-rotating Earth, integrated with 2nd-order Runge-Kutta, with a stated ballistic coefficient β = 13,000 kg/m². A free web-based HGV simulator exists at Berkeley (BRSL). Fetter's Ballistic Missile Primer and Gronlund & Wright give burnout velocities, apogees, and flight times.
4. **IR signature magnitudes are the genuine data gap.** Published rocket-plume IR intensities exist (hundreds of W/sr integrated in MWIR from CFD/bench studies), but real hardbody/threat signatures and sensor NEI are classified. This must be a parameterized detection threshold.
5. **The software stack is mature and mostly permissive** (MIT/Apache/ISC/BSD), with a few GPL items to route around for a company that wants to commercialize.

---

## Part 1 — Orbital / Constellation Data

### CelesTrak (celestrak.org) — anonymous, no login
The modern access path is the **GP API** (replacing legacy `.txt` files):
```
https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE[&FORMAT=VALUE]
```
`{QUERY}` is one of `CATNR` (catalog number, 1–9 digits), `INTDES` (international designator, yyyy-nnn), `GROUP`, `NAME`, or `SPECIAL`. `FORMAT` is `TLE`, `3LE`, `2LE`, `XML`, `KVN`, `JSON`, `JSON-PRETTY`, or `CSV`. Non-TLE formats deliver the **OMM (Orbit Mean-Elements Message)** per CCSDS 502.0-B-3.

**Examples you can run now:**
- SBIRS GEO-4: `https://celestrak.org/NORAD/elements/gp.php?CATNR=43162&FORMAT=json`
- All objects from the April 2023 Tranche 0 launch: `https://celestrak.org/NORAD/elements/gp.php?INTDES=2023-050&FORMAT=tle`
- Misc. military group: `https://celestrak.org/NORAD/elements/gp.php?GROUP=military&FORMAT=csv`
- Active GEO comms (context/co-location): `GROUP=geo`

**Relevant GROUP names (verified current):** Special-Interest — `last-30-days`, `stations`, `visual`, `active`, `analyst`, `cosmos-2251-debris`, `iridium-33-debris`, `fengyun-1c-debris`. Comms — `geo`, `intelsat`, `ses`, `starlink`, `oneweb`, `kuiper`, `iridium-NEXT`. Navigation — `gnss`, `gps-ops`, `galileo`, `beidou`, `glo-ops`, `sbas`. Misc — `military`, `radar`, `cubesat`. There is **no** `sda`, `pwsa`, `tranche`, or `missile-warning` group. Use `CATNR`/`INTDES` for the specific missile-warning sats. CelesTrak also offers a "Search GP Groups by Catalog Number" tool (`celestrak.org/NORAD/elements/master-gp-index.php`) to find which groups any object belongs to.

**Supplemental (SupGP) data** — higher-accuracy operator ephemerides for some constellations:
```
https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?SOURCE=...&FORMAT=...
```
Sources include `Starlink-E`, `Iridium-E`, `ISS-E`, `CPF`. Not available for military sats.

**Catalog-number crunch (important for your build):** CelesTrak's front page warns 5-digit catalog numbers were exhausted around 2026-07-11 (object "Saramago" = 100000); new objects get 6-digit numbers (100000+) and **GP data will not be available in legacy TLE format** for them — only OMM (XML/KVN/JSON). Design your ingest around OMM/JSON, not fixed-width TLE parsing.

**Terms:** CelesTrak redistributes Space-Track data under USSPACECOM's blanket approval for "basic SSA data" (TLE/OMM, SATCAT, decay data) conditioned on appropriate citation.

### Space-Track.org — free registration required
REST API base pattern:
```
https://www.space-track.org/basicspacedata/query/class/gp/{PREDICATE}/{VALUE}/orderby/{...}/format/{tle|json|xml|csv|kvn}
```
Workflow: POST credentials to `/ajaxauth/login` to get a cookie, then GET query URLs. Useful queries:
- One object: `/class/gp/NORAD_CAT_ID/43162/format/json`
- By launch: `/class/gp/OBJECT_ID/~~2023-050/orderby/NORAD_CAT_ID%20asc/`
- Fresh full catalog: `/class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json`
- History for one object: `/class/gp_history/NORAD_CAT_ID/25544/orderby/epoch%20desc/limit/22/format/xml`

**Rate limits (verbatim from Space-Track API Use Guidelines):** "Limit API queries to less than 30 requests per 1 minute(s) and 300 requests per 1 hour(s)." The full catalog only updates a few times per day — cache locally and refresh every several hours.

**Terms / redistribution:** The User Agreement (10 USC 2274(c)(2)) says the user agrees **not to transfer any data or technical information received from this website, or analysis of that data, to any other entity without prior express approval.** BUT USSPACECOM has given **express blanket approval** for redistribution of "basic SSA data" — TLEs, OMMs, SATCAT, and decay/reentry data — conditioned on appropriate citation. Practical rule: you can freely use and cite TLE/OMM/SATCAT; do not mirror bulk raw pulls publicly; publish derived products.

### What is actually public for these constellations (verified)
| System | Object | NORAD ID | COSPAR | Notes |
|---|---|---|---|---|
| SDA T0 Tracking (SpaceX) | BB 1 / T0TR 1 | 56171 | 2023-050K | Public TLE, 81° incl, ~950–1000 km |
| | BB 2 / T0TR 2 | 56170 | 2023-050J | Public TLE |
| | BB 3 / T0TR 3 | 57760 | 2023-133D | Public TLE (n2yo COSPAR field inconsistent) |
| | BB 4 / T0TR 4 | 57757 | 2023-133B | Public TLE |
| SDA T0 Tracking (L3Harris) | Raptor 2 / T0TR 6 | 58959 | 2024-028E | Public TLE, ~40° incl |
| MDA HBTSS | HBTSS-SV2 | 58955 | 2024-028A | Public TLE |
| | HBTSS-SV1 | 58960 | 2024-028F | Public TLE |
| SBIRS GEO | GEO-1 (USA-230) | 37481 | 2011-019A | Public |
| | GEO-2 (USA-241) | 39120 | 2013-011A | Public |
| | GEO-3 (USA-273) | 41937 | 2017-004A | Public |
| | GEO-4 (USA-282) | 43162 | 2018-009A | Public |
| | GEO-5 (USA-315) | 48618 | 2021-042A | Public |
| | GEO-6 (USA-336) | 53355 | 2022-092A | Public; GEO-7/8 cancelled |
| DSP | DSP-23 (USA-197) | 32287 | 2007-054A | Public; final DSP |

The two MDA HBTSS prototypes launched **14 Feb 2024** from Cape Canaveral SFS on the USSF-124 mission — one built by L3Harris (a $121M MDA contract) and one by Northrop Grumman ($155M); MDA later confirmed (per SpaceNews, Apr 25, 2025) that the Northrop Grumman satellite failed to meet established requirements while the L3Harris satellite met its performance targets. All are publicly cataloged with TLEs regardless of operational status.

**Withheld-object / analyst-object policy:** The most sensitive US payloads (chiefly NRO optical reconnaissance) are catalogued but have **no published orbital elements** — CelesTrak carries these as "analyst objects" (`GROUP=analyst`), and amateur observers (the SeeSat-L community) are the source of what is known. **Crucially for you: the missile-warning constellations are NOT in this withheld set.** SBIRS, DSP, SDA Tracking Layer, and HBTSS all have public elements, so your GEO and LEO missile-warning layers can be seeded with *real* elements.

### Alternatives and supplements
- **n2yo.com** — per-object pages with live AFSPC-sourced TLEs; good for spot-checking a NORAD ID (e.g., `n2yo.com/satellite/?s=56171`).
- **Heavens-Above** (heavens-above.com) — pass predictions, human-readable.
- **Jonathan McDowell's space report** (planet4589.org/space/) — authoritative launch logs; his TLE page excludes US-gov-restricted redistribution.
- **Gunter's Space Page** (space.skyrocket.de) — best free source for constellation-by-constellation object lists, COSPAR IDs, buses; the T0TR page gives Tranche 0 orbit as 950 km × 950 km, 80–89.5°.
- **SDA "On-Orbit" fact sheets** (sda.mil/on-orbit/, sda.mil/wp-content/uploads/.../Tracking-Layer-Fact-Sheet...) — **the authoritative published Walker parameters.**

**Published Walker parameters for the Tracking Layer (use these directly):**
- **Tranche 0 Tracking:** 8 WFOV SVs; per the SDA "ON ORBIT" page, "The majority of the space vehicles are distributed in two orbital planes; Inclination: 80°; Altitude: 1000km."
- **Tranche 1 Tracking:** 28 SVs. Per SDA's July 18, 2022 award announcement, L3Harris and Northrop Grumman each build "a space segment consisting of two planes with seven space vehicles per plane — 14 satellites from each performer for a total of 28 satellites in **four planes**" at **~1000 km, ~81° inclination.** (Note: the widely cited "10 launches / 10 planes" figure refers to the **Transport** Layer, not Tracking.)
- **Tranche 1 overall:** 154 operational SVs = 126 Transport + 28 Tracking, plus four missile-defense demo SVs (per Space Systems Command via National Defense Magazine, Sep 15, 2026; ~63 on-orbit as of July 2026). Later epochs add **MEO planes** for low-latitude coverage and stereo custody (published intent, not yet on-orbit).

### Practical verdict (Part 1)
Seed the **GEO layer with real SBIRS/DSP elements** and the **LEO layer with real Tranche 0 elements**, then **synthesize the operational LEO layer as a notional Walker constellation** from the SDA-published counts (28 Tracking SVs, 4 planes, 1000 km, 81°). MEO missile-warning is **not yet meaningfully on-orbit or cataloged**, so MEO must be fully notional from published intent. Honest, defensible split: **~30% real elements** (enough to validate propagation and geometry) and **~70% synthesized Walker** for the operational architecture.

---

## Part 2 — Threat Trajectory Data and Models

### Tracy & Wright (S&GS 28, 2020), "Modeling the Performance of Hypersonic Boost-Glide Missiles"
Open PDF: `https://scienceandglobalsecurity.org/archive/sgs28tracy.pdf`. Contents you can lift directly:
- **Six coupled equations of motion** over a spherical, non-rotating Earth in a 3-D coordinate system (velocity v, flight-path angle γ, heading, plus position), forces = gravity, lift, drag, apparent centrifugal.
- **Integration:** 2nd-order Runge-Kutta (midpoint).
- **Equilibrium-glide condition** (their Eq. 7) setting initial altitude where weight = lift + centrifugal.
- **Ballistic coefficient β = 13,000 kg/m²** (confirmed in Candler's response paper).
- Maneuvering via bank/roll-angle variation; terminal inverted dive at roll = 180°.
- Boost and ballistic phases use standard ballistic EoM (Appendix); pull-up handled analytically per Acton.
- **No official code is published with the paper**, BUT the team released a **free web-based Hypersonic Glide Vehicle Simulator** (Tracy, Wright, Ly, Ding): `https://brsl.berkeley.edu/?p=2100`, with a detailed user manual ("Quantification of Hypersonic Missile Capabilities using the Hypersonic Glide Vehicle Simulator"). This is your reference oracle for validating your own HGV integrator.

Companion papers (open PDFs at scienceandglobalsecurity.org/archive/): Acton `sgs23acton.pdf` (boost-glide fundamentals, EoM derivation), Wright `sgs23wright.pdf` (HTV-2 boost analysis, Δv = 2V sin(θ/2) dogleg math), Candler `sgs30candler.pdf` (CFD IR emission — uses β = 13,000 kg/m²).

### Cameron Tracy / Berkeley BRSL
The BRSL HGV Simulator (above) is the public open resource. There is **no official BRSL GitHub repo** of the solver itself; the web app + manual are the public artifacts.

### Public GitHub implementations (usable, caveat licensing)
- `jlev/ballistic-missile-range` — ICBM boost + ballistic flight from launch parameters; documents variables (V, T, m, ρ, A, h, g, ψ range angle, γ, η thrust-axis angle) and minimum-energy-trajectory γ_burnout formula. Good scaffold.
- `Rishit-katiyar/hypersonic-visualization`, `lwcook/hypersonic-simulation` (Cambridge) — HGV trajectory/aero visualization.
- `nasa/simupy-flight` — NASA 6-DOF flight-vehicle toolkit, validated against NESC reference cases; authoritative for validation.
- `RocketPy-Team/RocketPy` — 6-DOF launch-vehicle trajectory (MIT license); relevant for boost-phase modeling with real atmospheric data.

### Ballistic missile parameters (public numeric values)
- **Steve Fetter, "A Ballistic Missile Primer"** (`armscontrol.ru/course/articles/primer.pdf`): rocket equation, staging mass ratios, burnout-velocity formula v_bo as function of range/altitude/angle; minimum-energy trajectory at θ = (φ+π)/4.
- **Gronlund & Wright, "Depressed Trajectory SLBMs" (S&GS 3, 1992)** (`sgs03gronlund.pdf`): Table 1 gives, verbatim, for a **7,400 km MET: burnout velocity 6.3 km/s, apogee 1,340 km, flight time 29.2 min** (134 R / 86 CR dispersion). Two-dimensional EoM in Appendix B (point-mass, zero-lift).
- **Wilkening (S&GS 12, 2004)** (`sgs12wilkening.pdf`): boost-phase detection/tracking timelines and sensor-architecture treatment; useful for latency modeling.
- NRC "Making Sense of Ballistic Missile Defense" (2012): ICBM boost ≈ 250 s (liquid), burnout velocity 6.5–7.4 km/s, total flight ~40 min.

### IR signature magnitudes — be explicit about what is/isn't public
**Genuinely public** (rocket-plume radiant intensity, from CFD + bench studies):
- ONERA soot-plume study: integrated **MWIR ≈ 491–593 W/sr, SWIR ≈ 987–1518 W/sr, LWIR ≈ 96–103 W/sr** for a bench-scale plume.
- DLR "Infrared measurements of launch vehicle exhaust plumes": plume ≈ 1500 K; measured irradiances at km ranges in SWIR/MWIR.
- Chinese solid-motor plume studies: peak radiance at CO₂ (4.3 µm) and CO (4.7 µm) bands; recommend **2.7 µm and 4.3 µm bands** for space-based warning — matching real SBIRS SWIR/MWIR band choices.

**NOT public (must parameterize):** real threat hardbody IR signatures, actual SBIRS/OPIR sensor NEI/NEΔT, real plume signatures of specific adversary missiles, and space-based detection SNR budgets. Model detection as a **parameterized threshold** (radiant intensity vs. range vs. band vs. background) with a swept SNR, not a hard-coded number.

---

## Part 3 — Detection / Sensor Modeling Inputs

### IR background & imagery (pull a sample today, free)
- **GOES-R ABI Level-1b Radiances (ABI-L1b-Rad)** — 16 bands incl. MWIR/LWIR (Ch. 7 = 3.9 µm; Ch. 11–16 = 8.5–13.3 µm). Free on **AWS S3** (`s3://noaa-goes16/ABI-L1b-RadF/...`), Google Cloud, and Azure via NOAA Open Data Dissemination (NODD). Filename schema: `OR_ABI-L1b-RadF-M6C07_G16_sYYYYJJJHHMMSSs_e..._c....nc` (F=full disk, C=CONUS, M=mesoscale). Pull with `goes2go` (Python) or `aws s3 cp`. Registry: `registry.opendata.aws/noaa-goes/`.
- **VIIRS / MODIS** — active-fire and IR products via NASA LAADS DAAC / FIRMS; useful as hot-target and background proxies.

### Published GOES launch-detection work (SDA TAP Lab "Project Apollo")
The SDA/SSC TAP Lab ran "Project Apollo" (space-launch custody). Documented in the AMOS 2024 paper (Allen et al., `amostech.com/TechnicalPapers/2024/Poster/Allen.pdf`): in an integrated test, **CU Boulder detected the launch event using GOES-16 infrared imagery**; GTC Analytics used seismic data; Intrack generated a launch nominal; Leidos cued a South American telescope. Problem statements (Catalyst Campus; ssc.spaceforce.mil "TAP Lab Project Apollo.pdf") confirm: "Using commercial or public imagery, detect the start of a space launch cycle automatically." **The GOES data is public; the specific Project Apollo detection code is not released**, but the approach (GOES ABI IR delta-detection) is reproducible from the public data.

### Public detection datasets and proxies
- **There is no public dataset of space-based IR launch detections.** Assume none exists; do not promise one.
- **Best multi-target tracking proxy: OpenSky Network ADS-B** (`opensky-network.org`) — real multi-target trajectories for benchmarking your tracker/fusion pipeline. Live REST API is free (OAuth, daily credits); **historical Trino/SQL access is free only to university-affiliated researchers, governmental orgs, and aviation authorities** — a company must request a license. Python: `pyopensky`, `traffic`. Use ADS-B to validate IMM/JPDA multi-target logic against real, messy tracks.
- Curated OpenSky scientific datasets (weekly state-vector snapshots) are downloadable without the Trino license.

---

## Part 4 — Software Stack

| Tool | Repo / URL | License | Lang | Good for | First thing to run |
|---|---|---|---|---|---|
| **Stone Soup** | github.com/dstl/Stone-Soup | MIT | Python | Multi-target tracking, fusion, metrics | Tutorial 08 (JPDA) |
| **python-sgp4** | pypi.org/project/sgp4 | MIT | Python/C++ | TLE/OMM propagation | `twoline2rv` + `sgp4` |
| **Skyfield** | rhodesmill.org/skyfield | MIT | Python | Propagation + geometry, time systems | `EarthSatellite.at()` |
| **sgp4 (Rust)** | crates.io/crates/sgp4 | MIT | Rust | Fast batch propagation | `sgp4::propagate` |
| **satkit** | github.com/ssmichael1/satkit | MIT/Apache | Rust+Py | RK9(8) numerical prop, SGP4, frames | `sk.utils.update_datafiles()` |
| **Orekit** | orekit.org | Apache-2.0 | Java (+`orekit-python`) | High-fidelity astrodynamics, NRLMSISE-00 | `TLEPropagator` |
| **Basilisk** | avslab.github.io/basilisk | ISC | C/C++ + Py | Spacecraft mission sim, Monte-Carlo | `scenarioBasicOrbit` |
| **NASA GMAT** | SourceForge/NASA | Apache-2.0 | C++/Java | Mission analysis, coverage | Tutorial mission |
| **hapsira** (poliastro successor) | github.com/pleiszenburg/hapsira | MIT | Python | Two-body/astrodynamics quick calcs | Quickstart |
| **Astropy** | astropy.org | BSD-3 | Python | Coordinates/time/units backbone | `SkyCoord`, `Time` |
| **CesiumJS** | cesium.com/cesiumjs | Apache-2.0 | JS | 3-D globe visualization | Sandcastle demo |
| **matplotlib/plotly** | — | PSF/BSD, MIT | Python | Proposal charts (Pareto, coverage) | — |

### Stone Soup tutorial → method mapping
- **JPDA:** `docs/tutorials/08_JPDATutorial.py` (multi-target data association).
- **IMM:** Stone Soup IMM predictor/updater tutorials (maneuvering-target model switching — essential for boost→midcourse→glide phase changes).
- **MHT / GNN:** data-association tutorials + "Comparing EHM with probability associators" example.
- **Multi-sensor / sensor management:** `auto_tutorials/sensormanagement/` (single & multi-sensor).
- **Angles-only / bearings-only:** the bearing-only tracking example (PR #823) — directly relevant to passive IR/OPIR.
- **Metrics:** `OSPAMetric` (`stonesoup.metricgenerator.ospametric`, params c=40, p=1), **GOSPA** (same module), **SIAP** (`siapmetrics`), plus an uncertainty metric. Instantiate via `MultiManager`.

### SGP4/TLE accuracy caveats (state these in the proposal)
TLE+SGP4 carries **~1 km error at epoch, growing ~1–3 km/day**. TLEs use *mean*, not osculating, elements; conversion to osculating without error is impossible, so use only a simplified-perturbations propagator with TLE input. `python-sgp4` and `sgp4_pure_python` agree to within 0.1 mm of the reference C++ (numerical fidelity), so any residual error is physical, not implementation. A 1-second time error ≈ 7 km position error in LEO — handle time systems carefully (TLE epochs are UT1-based; Skyfield converts automatically via IERS). For GEO/deep-space sats, SDP4 applies (error ~10 km at epoch).

### Coverage / revisit analysis (open source)
No single dominant OSS "coverage tool" exists; **NASA GMAT** has built-in coverage/contact analysis, and **Orekit** provides `ElevationDetector`/`FootprintOverlapDetector` and event detection for building coverage/revisit yourself. For a Go/Rust-first team, computing access geometry directly (LOS + horizon mask + FOV cone) from propagated ephemerides is the pragmatic route — a few hundred lines, not a library dependency.

### Go/Rust-first guidance + licensing flags
- **Rust:** `sgp4` crate and `satkit` (both MIT/Apache) cover propagation natively — do the heavy propagation/coverage loops in Rust.
- **Python glue:** Stone Soup (tracking/metrics) and Skyfield (validation) are Python-only; wrap them as a thin analysis/validation layer, not the compute core.
- **GPL traps to avoid for a company that may commercialize:** `pynrlmsise00` is **GPLv2**; `hypervehicle` is **GPLv3**; the CelesTrak `fundamentals-of-astrodynamics` repo is now **AGPL-3.0** (though the underlying SGP4 code carries a CelesTrak FAQ statement of "no license... use for any purpose, personal or commercial"). Prefer **MIT/Apache** equivalents: use `pymsis` (NRLMSISE-00, NASA SWx-TREC) or Orekit's Java NRLMSISE00 instead of the GPL Python wrapper; `pyatmos` (MIT) for COESA76/NRLMSISE-00/JB2008. Orekit (Apache-2.0), Basilisk (ISC), Stone Soup (MIT), sgp4/Skyfield (MIT) are all commercialization-safe.

---

## Part 5 — Legal / Compliance Guardrails

### ITAR / EAR public-domain carve-out
- **22 CFR 120.34** defines "public domain," verbatim: "information which is published and which is generally accessible or available to the public: (1) Through sales at newsstands and bookstores; (2) Through subscriptions which are available without restriction... (8) Through fundamental research in science and engineering at accredited institutions of higher learning in the U.S. where the resulting information is ordinarily published and shared broadly in the scientific community." Public-domain information is excluded from the ITAR "technical data" definition (120.33), which also excludes general scientific/mathematical/engineering principles taught in schools.
- **Key nuance for a company (not a university):** the *fundamental research* prong (120.34(a)(8)) is a university carve-out and does **not** automatically cover a for-profit SBIR performer. But the other prongs do: information **already published** (the S&GS papers, public TLEs, SDA fact sheets, GOES data) is public-domain regardless of who uses it. Your simulation of *published* boost-glide equations using *published* parameters and *public* orbital elements is operating on public-domain inputs.
- **The real risk is aggregation and output.** ITAR controls "technical data" that provides information for the design/development/production of defense articles. A trade study that (a) uses only published inputs and (b) does not reveal non-public performance of a specific US defense article is defensible as public-domain-derived. But if your *outputs* start to look like design data for the actual SDA architecture (e.g., you back out real sensor NEI or real constellation geometry), a MITRE/Aerospace reviewer could treat that aggregate as new controlled technical data. **Intent to publish is not sufficient** under ITAR — data must actually be published through an approved channel before the exclusion attaches.
- **Practical rule of thumb for a small company:** (1) build from published sources and cite them; (2) parameterize anything classified rather than sourcing real values; (3) if the SBIR contract imposes access/dissemination controls (likely for Phase II), those override the public-domain assumption for contract deliverables — get an export-control determination before publishing; (4) keep a US-persons-only posture for anything touching real threat/sensor parameters.

### Space-Track redistribution
User Agreement (10 USC 2274(c)(2)): do not transfer received data or its analysis to third parties without approval — **except** USSPACECOM's express blanket approval for "basic SSA data" (TLE, OMM, SATCAT, decay data) with citation. So: cite Space-Track; publish derived products; don't mirror bulk raw catalog pulls in a public repo.

### Publishing HGV performance models
The Tracy & Wright papers and the Berkeley HGV simulator are already public and unclassified (peer-reviewed, hosted openly). That establishes that **generic boost-glide performance modeling from first principles is publishable.** Re-implementing those published equations and citing them is squarely public-domain. The line you don't cross: incorporating any non-public parameters for a *specific* real weapon system.

### What can safely go in a public GitHub repo vs. stay internal
- **Public-safe:** code implementing published EoM (Tracy/Wright/Fetter), notional Walker-constellation generators, coverage/geometry math, Stone Soup tracking pipelines, synthetic-data generators, visualization, and results using *notional* parameters. License it MIT/Apache.
- **Internal only:** any real Space-Track bulk pulls; any parameter set that came from the customer, a classified source, or reverse-engineering a real system's performance; the specific calibrated detection thresholds if tuned to represent a real sensor; and all Phase II contract deliverables subject to dissemination controls.

---

## Part 6 — Concrete Build Sequence

Each step: inputs → transformation → output artifact → Phase II metric supported (Accuracy / Latency / Resilience / Coverage). "Parameterize" = expose as config, because the real value is classified.

**Step 1 — Ingest & propagate public elements; validate.**
Inputs: CelesTrak/Space-Track OMM/JSON for SBIRS (37481, 39120, 41937, 43162, 48618, 53355), DSP (32287), Tranche 0 (56170/56171/57757/57760), HBTSS (58955/58960). Transform: parse OMM → SGP4/SDP4 propagate (python-sgp4 or Rust `sgp4`). Output: ephemeris tables + ground tracks. **Metric: Accuracy (foundation).** *Validation that survives Aerospace/MITRE scrutiny:* reproduce a known reference — propagate ISS (25544) and compare to Vallado's SGP4 test vectors (agreement to <1 mm numerically); confirm GEO sats hold ~35,786 km, ~1.0 rev/day; confirm Tranche 0 sits at ~1000 km, ~81°. State the ~1–3 km/day TLE degradation explicitly. *Parameterize:* propagation step size, epoch window.

**Step 2 — Synthesize notional Walker constellations.**
Inputs: SDA published parameters — T1 Tracking = 28 SVs, LEO 1000 km, ~81°, **4 planes**; GEO from SBIRS reality; MEO fully notional (published intent only). Transform: Walker-delta generator (i:T/P/F) producing TLE/OMM-equivalent state sets. Output: notional multi-orbit constellation (GEO + MEO + LEO). **Metric: Coverage + Resilience.** *Validation:* seed with the 4 real Tranche 0 elements and show the synthesized plane reproduces their altitude/inclination/RAAN spread; sanity-check against SDA's stated "near-global stereo" claim for T1+. *Parameterize:* planes, sats/plane, phasing F, altitude, inclination, MEO plane count.

**Step 3 — Coverage & revisit over a chosen launch region.**
Inputs: constellation ephemerides + a defined (notional) threat launch box. Transform: LOS + horizon-mask + FOV-cone access computation; compute single-look, multi-look, and **stereo** (≥2 simultaneous LOS with adequate convergence angle) availability. Output: coverage/revisit statistics, stereo-availability time series and maps. **Metric: Coverage.** *Validation:* independently recompute a subset of accesses in GMAT or via closed-form horizon geometry; verify percentage coverage is monotonic in constellation size. *Parameterize:* sensor FOV, minimum elevation/grazing angle, stereo convergence-angle threshold.

**Step 4 — Generate synthetic ballistic & HGV trajectories.**
Inputs: Fetter/Gronlund ballistic EoM + parameters (burnout 6.3–7.4 km/s; apogee ~1,340 km, flight time 29.2 min for the 7,400 km MET); Tracy & Wright HGV EoM (β = 13,000 kg/m², L/D swept, RK2/RK4 integration). Transform: integrate trajectories for a threat menu (SRBM/MRBM/ICBM/HGV). Output: truth trajectory library (time, position, velocity, phase labels). **Metric: Accuracy + Latency.** *Validation:* reproduce the Berkeley HGV simulator's published range/time-of-flight for matched inputs; reproduce Gronlund's 7,400 km MET table (6.3 km/s, 29.2 min); energy-conservation check in ballistic coast. *Parameterize:* L/D, β, boost profile, burn time, launch/aim points.

**Step 5 — Sensor / detection model.**
Inputs: truth trajectories + constellation ephemerides + plume/hardbody IR intensity (parameterized from public plume numbers, e.g. hundreds of W/sr MWIR). Transform: LOS geometry, Earth occultation, Sun/terminator/solar-exclusion constraints, atmospheric transmission (parameterized), a **parameterized detection threshold** (radiant intensity vs range vs band vs background), plus a false-alarm generator (parameterized clutter/FAR). Output: time-tagged detections (with misses and false alarms) per sensor. **Metric: Accuracy + Coverage.** *Validation:* show detection onset coincides with boost-phase plume (highest signal), and that occultation/terminator logic zeroes detections when geometry forbids; band choice consistent with 2.7/4.3 µm public guidance. *Parameterize:* NEI/SNR threshold, band, FAR, background radiance, transmission.

**Step 6 — Tracking baseline in Stone Soup.**
Inputs: detections from Step 5. Transform: **IMM** (boost/midcourse/glide models) + **JPDA** multi-target; angles-only/stereo fusion of ≥2 sensors. Output: tracks + covariances. **Metric: Accuracy.** Measure with **OSPA/GOSPA** (c=40, p=1) and **SIAP**. *Validation:* first validate the pipeline on **OpenSky ADS-B** real multi-target data (does IMM/JPDA hold tracks through maneuvers?), then apply to synthetic threats; report OSPA vs. number of sensors and vs. detection threshold. *Parameterize:* process-noise per model, IMM transition matrix, gate size.

**Step 7 — Fusion-placement comparison + Pareto chart.**
Inputs: tracks + a latency model (sensor→fusion→decision) for three architectures: ground-based fusion, on-orbit (edge) fusion, hybrid. Transform: compute warn-to-decision latency and track accuracy for each; add crosslink/downlink hops (parameterized delays). Output: **warn-to-decision-time vs. track-accuracy Pareto chart.** **Metric: Latency + Accuracy (the core trade).** *Validation:* latency budget must sum transparently (propagation + processing + comms hops); cross-check against Wilkening's boost-phase timelines and the TAP Lab "seconds-to-minutes" cueing goal. *Parameterize:* per-hop latency, crosslink availability, processing time.

**Step 8 — Resilience sweeps.**
Inputs: constellation + fusion graph. Transform: Monte-Carlo node loss (kill N sats) and link loss (sever crosslinks); recompute coverage, stereo availability, track continuity, latency. Output: degradation curves vs. % nodes/links lost. **Metric: Resilience.** *Validation:* show graceful degradation for the proliferated LEO layer vs. brittle failure for the sparse GEO layer — the expected qualitative result reviewers look for. *Parameterize:* failure count/pattern, correlated vs. random loss.

**Step 9 — ML component + classical baseline.**
Inputs: synthetic + ADS-B tracks/detections. Transform: an ML classifier/discriminator (e.g., threat-type ID from track features, or detection/clutter discrimination) **always reported against a classical baseline** (IMM likelihood, threshold detector). Output: ROC/confusion vs. baseline; ablation. **Metric: Accuracy (+ Latency if inference is on-orbit).** *Validation:* strict train/test split, no leakage across trajectories; show ML only where it beats the classical baseline — reviewers distrust ML that isn't baselined. *Parameterize:* feature set, model size (for on-orbit SWaP), inference latency.

---

## Part 7 — Is Deep Research on the Data Worth It?

**Direct answer: Do focused research, not a data expedition.** The public data is good enough to make the trade study *credible*, and the outcome is dominated by parameters you cannot get publicly anyway. Spend research effort on exactly three things; parameterize everything else.

**The two–three data questions that actually change the trade result:**
1. **Notional LEO Walker geometry (planes / sats-per-plane / altitude / inclination).** This drives coverage, stereo availability, latency (crosslink hops), and resilience simultaneously — it moves *all four* Phase II metrics. Worth the effort to nail the *published* SDA numbers precisely (28 Tracking SVs, 4 planes, 1000 km, 81°, plus MEO intent) and sweep around them. **High payoff.**
2. **The detection-threshold / IR-signature assumption.** Whether a boost plume or a cold gliding hardbody is detectable at a given range/band sets when custody begins and therefore latency and track accuracy. The real numbers are classified, so the payoff is in *bounding* it well from public plume radiometry and running it as a sweep — not in finding the "true" value. **High payoff as a parameter sweep; zero payoff as a hunt for the real number.**
3. **Fusion-placement latency budget.** The ground-vs-orbit-vs-hybrid latency deltas decide the headline Pareto chart. Component latencies are partly public (comms physics, TAP Lab "seconds-to-minutes" goal) and partly assumption. Worth building carefully. **Medium-high payoff.**

**Nice-to-have (do NOT sink time here):**
- Chasing withheld/analyst-object elements for real sensors — they're withheld for the sensitive NRO payloads; the missile-warning sats you need are already public.
- Precise real IR signatures of specific threats — classified; parameterize.
- High-fidelity atmosphere beyond NRLMSISE-00/COESA76 — negligible effect on a trade study.
- Sub-km propagation accuracy — irrelevant given the trade study operates on notional geometry; SGP4's 1–3 km/day is fine.
- A "perfect" HGV solver — the Berkeley simulator + published EoM already give validated behavior.

**Bottom line:** The data hunt pays off in *parameterizing the right knobs and validating against public references*, not in acquiring secret truth. Build the pipeline (Steps 1–9), seed it with real public elements where they exist, synthesize the rest from published SDA/threat parameters, and make every classified quantity a swept parameter with a defensible public-data-derived range.

---

## Recommendations (staged)

**Stage 0 — Today (before writing more of the proposal):**
- Pull real elements now: CelesTrak `gp.php?INTDES=2023-050&FORMAT=json` (Tranche 0), `CATNR=43162` (SBIRS GEO-4), and register for Space-Track. Pull one GOES-16 ABI L1b scene from AWS with `goes2go`. Clone Stone Soup and run Tutorial 08. Read `sgs28tracy.pdf` and open the Berkeley HGV simulator.
- **Signal that would change the plan:** if you cannot reproduce SGP4 test vectors or the Gronlund MET table, fix your propagator/integrator before anything else.

**Stage 1 — Feasibility spine:** Steps 1–4 (ingest/validate → synthesize Walker → coverage → synthetic threats). Deliver a coverage/stereo map and a truth-trajectory library. **Threshold to proceed:** propagation validated to <1 km at epoch vs. reference, and coverage numbers monotonic in constellation size.

**Stage 2 — The trade itself:** Steps 5–7. Deliver the warn-to-decision-vs-accuracy Pareto across ground/orbit/hybrid fusion. **This is the CONOPS centerpiece.** Threshold: latency budget must be transparent and cross-checked against Wilkening timelines.

**Stage 3 — Robustness & differentiation:** Steps 8–9. Resilience curves + one baselined ML component. **Threshold to include ML in the proposal:** it must beat the classical baseline on a clean train/test split; if not, present the classical result and cite ML as Phase II work.

**Compliance gate (before any public release):** confirm all inputs are published/public-domain, cite Space-Track, keep raw bulk pulls and any customer/classified parameters internal, and get an export-control determination if the SBIR imposes dissemination controls.

---

## Caveats
- **Forward-looking/soft claims flagged:** SDA MEO missile-warning is largely *planned/notional* — treat MEO as synthesized-from-intent, not on-orbit reality. SDA fact-sheet coverage claims ("near-global stereo," "global track custody") are program goals, not measured performance. One of the two HBTSS prototypes (Northrop Grumman) reportedly failed to meet requirements — do not model HBTSS as fully validated operational capability.
- **Data conflicts noted:** Gunter's Space Page gives Tranche 0 orbit as 950 km × 950 km, 80–89.5°; SDA's own "ON ORBIT" page says 1000 km, 80°. The "10 planes / 10 launches" figure applies to the **Transport** Layer; the **Tracking** Layer is **28 SVs in 4 planes** (2 planes × 7 SVs × 2 performers) per SDA's July 2022 award announcement. n2yo shows a COSPAR-field inconsistency for BB 3 (57760: header "2023-133E" vs. TLE "23133D"); the NORAD ID 57760 is firm. Older Space-Track wrappers cite "<20/min"; use the current official "<30/min and <300/hr."
- **What is genuinely NOT public:** real threat IR signatures, real sensor NEI/SNR, real (vs. published-notional) constellation geometry, and any withheld NRO-class elements. None of these block the trade study if parameterized.
- **Licensing:** verify each dependency's license at integration time; the GPL/AGPL items (`pynrlmsise00`, `hypervehicle`, CelesTrak `fundamentals-of-astrodynamics`) should be swapped for MIT/Apache equivalents if commercialization is intended.
- **TLE/SGP4 accuracy:** ~1 km at epoch, +1–3 km/day; adequate for a trade study but not operational fire control — state this limitation explicitly.