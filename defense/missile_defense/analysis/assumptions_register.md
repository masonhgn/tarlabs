# Assumptions & sources register  (task A-08)

Every quantitative value that reaches the proposal gets a row here. No naked numbers.

**Classification column:**
- `PUBLIC-CITED` — taken from a published, citable source. Cite it in the proposal.
- `NOTIONAL-SWEPT` — the real value is classified or unknown; we parameterize and sweep it.
  The proposal must say so explicitly and report *relative* results.
- `DERIVED` — computed by us from other rows. Show the derivation.

The proposal's credibility rests on this table being complete and honest. Evaluators are
MITRE and Aerospace Corporation; candor about the unclassified/classified boundary is
rewarded, and an invented absolute number is the fastest way to lose.

| Symbol | Value | Classification | Source | Sweep range | Used in |
|---|---|---|---|---|---|
| — | SDA Tranche 0 Tracking: 8 SVs, 2 planes, 1000 km, 80° | PUBLIC-CITED | SDA "On Orbit" page | — | S-04 |
| — | SDA Tranche 1 Tracking: 28 SVs, 4 planes, ~1000 km, ~81° | PUBLIC-CITED | SDA award announcement, 2022-07-18 | plane count ±, alt ± | S-04 |
| — | SDA MEO missile warning geometry | NOTIONAL-SWEPT | published *intent* only; not on orbit | plane count, altitude | S-04 |
| FOR | Tranche 0 requirement: fixed sensor, objective FOV **~110°**, pixel footprint **<1.5 km** | PUBLIC-CITED | CSIS *Getting on Track* p.32, citing SDA T0 technical requirements | sweep 90–120° | S-05, S-07 |
| FOR | 120° is near the physical limit at 1,000 km — Earth curvature caps line-of-sight gain beyond it | PUBLIC-CITED | CSIS *Getting on Track* p.28 | — | S-05 |
| — | Notional LEO architectures: **91** sats @1000 km/120° FOR (global stereo; **fails** at 110°/100°); **135** @1000 km/120°; **312** @110° | PUBLIC-CITED | CSIS *Getting on Track*, Figs 16/17/27/28 | architecture sweep | S-04, S-05 |
| — | Notional multi-orbit: 15 MEO @10,000 km; 135 LEO + 8 MEO; 36 LEO + 8 MEO; 4 HEO + 8 MEO; 4 HEO + 15 MEO + 70 LEO; **30 MEO + 135 LEO = 165** | PUBLIC-CITED | CSIS *Getting on Track*, Figs 35/43/44/45/46/47 | architecture sweep | S-04, S-05 |
| — | SSC testbed GEO WFOV satellite uses a **4K-format** FPA; industry moving to 6K/8K | PUBLIC-CITED | CSIS *Getting on Track* p.32 | pixel count swept | S-07 |
| β | 13,000 kg/m² (HGV ballistic coefficient) | PUBLIC-CITED | Tracy & Wright, S&GS 28 (2020) | ± for sensitivity | S-06 |
| — | 7,400 km MET: burnout 6.3 km/s, apogee 1,340 km, ToF 29.2 min | PUBLIC-CITED | Gronlund & Wright, S&GS 3 (1992), Table 1 | — | S-06 validation |
| — | ICBM boost ≈ 180 s (solid) / ≈ 250 s (liquid) | PUBLIC-CITED | Wilkening S&GS 12 (2004); NRC (2012) | — | W-02, A-04 |
| — | Legacy detect-to-alert ≈ 30 s | PUBLIC-CITED | INSS, March 2025 — *illustrative, not a requirement* | — | A-04 framing |
| — | "~1 min to detect and characterize a threatening launch" | PUBLIC-CITED | National Academies boost-phase report | — | A-04 framing |
| NEI | sensor detection threshold, **DSP-class: 20 kW/sr** in 2.69–2.95 µm | PUBLIC-CITED | Garwin & Postol, inferred from Gulf War Scud detections; via Tracy & Wright 2020 p.17 | sweep 2–50 kW/sr | S-07 |
| NEI | sensor detection threshold, **SBIRS-like: 6 kW/sr** in 1.4–3.0 µm | PUBLIC-CITED | American Physical Society 2004 boost-phase study; via Tracy & Wright 2020 p.18 | sweep 2–50 kW/sr | S-07 |
| — | APS notional detector: step-stare, 1 km² pixel, 33 ms collection, 1 s revisit, 3-D geolocation <300 m | PUBLIC-CITED | APS 2004 — **Tier B proxy, not an agency spec** | pixel/revisit swept | S-07 |
| I_HGV | HGV glide hardbody radiant intensity, 2.69–2.95 µm: **2.95 – 43 kW/sr** | PUBLIC-CITED **(disputed)** | Tracy & Wright 2020 (43) vs Candler & Leyva 2022 (4.90 / 2.95). Both endpoints cited; do not adjudicate — DEC-15 | full range swept | S-07 |
| I_HGV | HGV glide hardbody radiant intensity, 1.4–3.0 µm: **22.1 – 370 kW/sr** | PUBLIC-CITED **(disputed)** | same dispute | full range swept | S-07 |
| — | Tracy & Wright cross-check: 113 vs Niu et al. 105 kW/sr (3–5 µm) at 5.4 km/s, 60 km | PUBLIC-CITED | Tracy & Wright 2020 p.16 — ~8% agreement | — | validation |
| h_glide | HGV equilibrium glide altitude **38–57 km** | NOTIONAL-SWEPT | Published values disagree: BRSL 38.15, T&W ~49, ours 48.9–49.5, Candler 49.7 and 57.1. Range is insensitive to altitude so nobody reconciled it — DEC-17 | full range swept | S-06, S-07 |
| — | bands 2.69–2.95 µm chosen because the atmosphere blocks most surface IR there, suppressing background | PUBLIC-CITED | Tracy & Wright 2020 p.17 | — | S-07 |
| — | *(quarantined)* ONERA/DLR plume radiometry (MWIR 491–593 W/sr etc.) | **UNVERIFIED — DO NOT USE** | never traced to a primary source; see D-04-a | — | none |
| — | per-hop fusion latency (crosslink / downlink / processing) | NOTIONAL-SWEPT | partly comms physics, partly assumption | full sweep | S-09 |
| — | fire-control-quality track accuracy threshold | NOTIONAL-SWEPT | **classified** — qualitative public description only | — | W-02 |
| — | TLE/SGP4 error ≈ 1 km at epoch, +1–3 km/day | PUBLIC-CITED | standard SGP4 literature | — | S-03, stated as a limitation |

*(Extend as the simulation produces values. Zero unfilled rows before W-04 starts.)*
