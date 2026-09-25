# S-03 — Propagation validation report

Generated 2026-09-23T02:16:24+00:00 by
`scripts/validate_propagation.py`. Do not edit by hand; regenerate it.

## Check 1 — agreement with Vallado's published SGP4 verification vectors

The reference data (`SGP4-VER.TLE`, `tcppver.out`) ships inside the `sgp4` package
and is the standard verification set for the algorithm.

- State vectors compared: **533**
- Worst position disagreement: **1.165e-07 km** (0.12 mm)
- Worst velocity disagreement: **4.997e-10 km/s**

Agreement at this level means we are running the standard algorithm, not an
approximation of it. Any remaining error against reality is physical -- the
limitation of mean elements -- not an implementation defect.

## Check 2 and 3 — real catalogued elements land in the expected regimes

Measured over 12 h at 2 min
steps from 2026-09-23T02:16:24+00:00. Altitude is WGS-84 geodetic.

| NORAD | Object | Layer | Epoch age | rev/day | Incl (deg) | Alt min | Alt mean | Alt max |
|---|---|---|---|---|---|---|---|---|
| 25544 | ISS (ZARYA) | reference | 0.8 d | 15.4922 | 51.63 | 415.7 | 425.2 | 437.4 |
| 37481 | SBIRS GEO-1 (USA-230) | geo | 0.7 d | 1.0027 | 4.75 | 35777.7 | 35780.7 | 35786.9 |
| 39120 | SBIRS GEO-2 (USA-241) | geo | 0.5 d | 1.0027 | 4.70 | 35783.1 | 35792.4 | 35796.6 |
| 41937 | SBIRS GEO-3 (USA-273) | geo | 0.6 d | 1.0027 | 2.43 | 35776.9 | 35782.9 | 35793.4 |
| 43162 | SBIRS GEO-4 (USA-282) | geo | 1.5 d | 1.0027 | 2.26 | 35781.8 | 35790.3 | 35793.9 |
| 48618 | SBIRS GEO-5 (USA-315) | geo | 0.5 d | 1.0027 | 4.99 | 35777.9 | 35782.3 | 35791.6 |
| 53355 | SBIRS GEO-6 (USA-336) | geo | 0.5 d | 1.0027 | 3.10 | 35778.0 | 35786.2 | 35794.2 |
| 56162 | CHECKMATE 8 | leo | 0.6 d | 13.8497 | 81.01 | 944.9 | 958.1 | 979.3 |
| 56163 | CHECKMATE 5 | leo | 0.5 d | 13.8500 | 81.00 | 944.6 | 958.2 | 979.2 |
| 56164 | CHECKMATE 4 | leo | 0.6 d | 13.8482 | 81.00 | 946.6 | 958.7 | 979.7 |
| 56165 | CHECKMATE 6 | leo | 0.5 d | 13.8875 | 81.01 | 922.3 | 944.9 | 971.7 |
| 56166 | CHECKMATE 7 | leo | 0.5 d | 13.8945 | 81.00 | 918.4 | 942.3 | 970.9 |
| 56167 | CHECKMATE 2 | leo | 1.0 d | 13.8517 | 81.01 | 943.4 | 957.5 | 978.7 |
| 56168 | CHECKMATE 1 | leo | 1.0 d | 13.8496 | 81.01 | 944.7 | 958.3 | 983.4 |
| 56169 | CHECKMATE 3 | leo | 0.6 d | 13.8515 | 81.01 | 943.6 | 957.4 | 978.6 |
| 56170 | BB 2 | leo | 0.8 d | 14.4654 | 81.00 | 733.4 | 748.8 | 766.7 |
| 56171 | BB 1 | leo | 0.9 d | 14.3428 | 81.01 | 768.7 | 789.2 | 813.4 |
| 57756 | WILDFIRE 4 | leo | 0.6 d | 13.8637 | 81.00 | 940.8 | 953.3 | 977.6 |
| 57757 | BB 4 | leo | 5.0 d | 14.8373 | 81.00 | 612.8 | 629.5 | 650.5 |
| 57758 | WILDFIRE 3 | leo | 0.6 d | 13.8629 | 80.99 | 941.5 | 953.3 | 977.0 |
| 57760 | BB 3 | leo | 1.0 d | 14.8655 | 80.99 | 604.9 | 621.2 | 639.7 |
| 57761 | WILDFIRE 7 | leo | 0.6 d | 13.8511 | 81.00 | 944.5 | 957.7 | 977.9 |
| 57762 | CHECKMATE 10 | leo | 0.6 d | 13.8548 | 81.00 | 943.9 | 956.4 | 978.1 |
| 57763 | WILDFIRE 6 | leo | 1.4 d | 13.8577 | 80.99 | 942.2 | 955.3 | 976.8 |
| 57764 | WILDFIRE 1 | leo | 0.7 d | 13.8575 | 81.00 | 943.5 | 955.5 | 977.3 |
| 57765 | WILDFIRE 9 | leo | 0.6 d | 13.8544 | 81.00 | 943.9 | 956.6 | 977.9 |
| 57766 | WILDFIRE 10 | leo | 0.6 d | 13.8565 | 81.00 | 943.6 | 955.6 | 977.7 |
| 57767 | WILDFIRE 2 | leo | 0.6 d | 13.8550 | 80.99 | 943.8 | 956.3 | 977.0 |
| 57768 | WILDFIRE 8 | leo | 0.6 d | 13.8546 | 80.99 | 944.0 | 956.3 | 977.8 |
| 57769 | WILDFIRE 5 | leo | 1.1 d | 13.8581 | 81.00 | 942.9 | 955.3 | 976.7 |
| 58955 | HBTSS-SV2 | leo | 0.9 d | 13.7049 | 39.99 | 986.5 | 1000.8 | 1022.8 |
| 58956 | RAPTOR 4 | leo | 0.6 d | 13.7440 | 39.99 | 976.0 | 987.3 | 1005.7 |
| 58957 | RAPTOR 1 | leo | 0.9 d | 13.7425 | 39.99 | 977.5 | 987.6 | 1004.0 |
| 58958 | RAPTOR 3 | leo | 1.0 d | 13.7049 | 39.99 | 991.4 | 1001.2 | 1017.0 |
| 58959 | RAPTOR 2 | leo | 1.0 d | 13.7056 | 39.99 | 990.8 | 1000.9 | 1016.9 |
| 58960 | HBTSS-SV1 | leo | 0.8 d | 15.0378 | 39.99 | 547.3 | 558.3 | 568.3 |

**Not retrievable from the CelesTrak GP set:** DSP-23 (USA-197) (32287).

### Check 2 — SBIRS GEO

Mean altitude spans **35781-35792 km** against the nominal 35,786 km, and
mean motion spans **1.0027-1.0027 rev/day** against the
nominal 1.0027. The regime is confirmed. Inclinations of 2-5 deg are expected:
ageing GEO satellites are commonly allowed to drift in inclination to save the
fuel that north-south stationkeeping would cost.

### Check 3 — the Tranche 0 Tracking Layer spans two distinct geometries

The eight Tracking satellites are not one homogeneous shell:

*SpaceX-built, near-polar:*

- BB 2: **749 km**, 81.00 deg
- BB 1: **789 km**, 81.01 deg
- BB 4: **629 km**, 81.00 deg
- BB 3: **621 km**, 80.99 deg

*L3Harris-built, mid-inclination:*

- RAPTOR 4: **987 km**, 39.99 deg
- RAPTOR 1: **988 km**, 39.99 deg
- RAPTOR 3: **1001 km**, 39.99 deg
- RAPTOR 2: **1001 km**, 39.99 deg

**This is not a contradiction of SDA's published figures.** SDA's wording is that
the *majority of Tranche 0 space vehicles* occupy two planes near 1000 km and 80
deg -- a hedged statement about the tranche as a whole, not a specification for
every Tracking satellite. An earlier version of this report framed it as a
discrepancy; that framing was wrong and is retracted (decision DEC-08 -> D-10).
The public record does not explain the mid-inclination geometry of the L3Harris
group, and we do not invent a rationale for it.

The MDA HBTSS prototypes split similarly -- SV2 near 1000 km, SV1 near 560 km.
**Altitude is not evidence of payload performance** and is never used as a proxy
for it here. L3Harris publicly reports a successful demonstration of its own
prototype; no government comparative test record was located, so no claim is made
about the other.

What this means for the study, per decision DEC-11: architecture documents and
catalogue geometry answer different questions. Propagate the real objects for
current-epoch coverage; use agency-stated design parameters for future-architecture
trades; never substitute one for the other.

**Provenance note.** The object-to-layer assignment above is a *manifest-count
inference*, not a published agency lookup -- no SDA/SSC/MDA source joins NORAD
numbers to contractor and layer. The inference is strong because the counts match
one-to-one across all three launches (19 Transport, 8 Tracking, 2 HBTSS), and the
19-rather-than-20 Transport count independently corroborates SDA's statement that
one vehicle was retained on the ground as a testbed.

## Stated limitations

- TLE/OMM mean elements propagated with SGP4 carry roughly **1 km** of position
  error at epoch, growing **1-3 km/day**. The oldest element set used here is
  **5.0 days** old.
- Mean elements cannot be converted to osculating elements without error, so they
  must be propagated with a simplified-perturbations model and nothing else.
- `teme_to_ecef` neglects polar motion and the TEME-to-PEF equation-of-equinoxes
  term (tens of metres), and approximates UT1 by UTC (up to ~0.4 km of Earth
  rotation at the equator). All are inside the SGP4 error budget above.
- This fidelity is adequate for a trade study over notional geometry and
  **inadequate for fire control**. The proposal says so in those words.

