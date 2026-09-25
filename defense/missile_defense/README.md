# missile_defense — DAF26BX06-NV510

SBIR Phase I effort against SpaceWERX topic **DAF26BX06-NV510**, *AI/ML for Next Generation
of Missile Detection, Warning, Tracking, and Reporting* (SSC Space Sensing Delta 84 / OPIR
Tap Lab).

**[`PLAN.md`](PLAN.md) is the ledger and the master document. Start there.**

## What we are building

An open, reproducible, deterministic simulation that screens the multi-orbit OPIR sensing
trade space — which constellation, revisit, detection-threshold and fusion-placement
parameters actually drive warn-to-decision time and track continuity against ballistic and
maneuvering threats — in order to identify, against a quantified classical baseline, where
AI/ML fusion has real leverage. The Phase I deliverables are a feasibility study, a USSF
CONOPS, and the trade-space engine itself.

The government confirmed in SITIS Q&A that this shape of effort — a feasibility study with
no new detection algorithm — is responsive to the topic.

## Layout

| Path | Contents |
|---|---|
| `PLAN.md` | the action-plan ledger |
| `mwsim/` | the simulation package |
| `scripts/` | entry points: fetch catalog, validate propagation, make figures |
| `data/raw/` | inputs as downloaded; never hand-edited |
| `data/processed/` | everything the scripts generate |
| `analysis/` | validation notes, compliance, engagement, assumptions register |
| `proposal/` | CONOPS, feasibility study, figures, cost, submission package |
| `docs/topic/` | the solicitation PDFs (official topic + internal triage brief) |
| `docs/research/` | background research: domain primer, data and tooling guide |
| `docs/extracted/` | grep-able text extracted from the PDFs |
| `tests/` | pytest, including the propagation validation gate (S-03) |

## Running

```sh
pip install -r requirements.txt
pytest                              # includes the S-03 propagation validation gate
python scripts/make_figures.py      # regenerates every proposal figure from seeds
```

## Data and compliance

Everything here is built from published, public-domain sources: CelesTrak / Space-Track
orbital elements, published equations of motion from the open literature, SDA and SSC fact
sheets, and NOAA GOES imagery. Bulk raw Space-Track pulls and any parameter calibrated to a
real system stay out of this repo. See `analysis/compliance/itar_posture.md`.
