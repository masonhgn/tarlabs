# defense

SBIR/STTR topic research — screening DoD solicitation releases down to the handful of
topics worth writing a proposal for, and turning those into briefs.

## Layout

```
scripts/          the pipeline
data/raw/         inputs, as downloaded from dodsbirsttr.mil (never edited by hand)
data/processed/   everything the scripts generate
analysis/         written triage, verdicts and notes
briefs/           the per-topic PDF briefs
```

## Pipeline

| Step | Script | In | Out |
|---|---|---|---|
| 1 | `build_release6_csv.py` | `data/raw/release6_*.txt` | `data/processed/release6_raw.csv` |
| 2 | `stage0_screen.py` | a topics CSV | `data/processed/stage0_survivors.csv` |
| 3 | `parse_sitis_qa.py` | the saved SITIS page + `analysis/triage_results.md` | `data/processed/sitis_qa.{json,md,csv}` |
| 4 | `make_briefs.py` | briefs written inline in the script | `briefs/*.pdf` |

Step 2 screens topics for Direct-to-Phase-II status and other disqualifiers. It defaults to
`data/raw/topics_search_1789872938.csv`; `data/processed/release6_stage0.csv` is the same
screen run over the Release 6 CSV from step 1.

Scripts resolve their own paths, so they run from any working directory:

```sh
pip install -r requirements.txt
python3 scripts/build_release6_csv.py
```

## Analysis

- `analysis/release6_topics.md` — the Release 6 topic list.
- `analysis/release6_triage.md`, `analysis/triage_results.md` — per-topic verdicts.
- `analysis/sbir-topic-triage.md` — the triage criteria.
- `analysis/process_learnings.md` — what worked and what to do differently next release.
