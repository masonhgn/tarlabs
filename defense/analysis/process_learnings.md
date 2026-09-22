# Process learnings — FY26 Release 5/6 cycle

Written 2026-09-20 after triaging Release 5 (87 Stage-0 survivors) and reconstructing Release 6. Ordered by how much each one would have changed the outcome.

## 1. Source topics from DSIP, never from sbir.gov exports
- The sbir.gov CSV (`topics_search_1789872938.csv`) contained **zero** Release 6 topics — sbir.gov had not indexed them 18 days after pre-release. We triaged 87 Release 5 topics closing in 3 days and missed 43 Release 6 topics with a month left.
- Fix in place: `build_release6_csv.py` parses the DSIP solicitation PDFs directly:
  `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation={DOD_SBIR_2026_P1_CBZ|DOD_SBIR_2026_P1_CBX|DOD_STTR_2026_P1_CTZ|DOD_STTR_2026_P1_CTX}&release=N&documentType=RELEASE_INSTRUCTIONS`
  (CBZ/CTZ = BAA topics, CBX/CTX = CSO topics). The preface doc gives dates; the instructions doc has full topic text.
- Next cycle: pull all four PDFs on pre-release day, not the sbir.gov search.

## 2. Read the calendar before triaging anything
- Each release has four dates: pre-release, open, Q&A close, close. Release 6: 09-02 / 09-23 / **10-07** / 10-21.
- Direct TPOC contact is allowed **only between pre-release and open** (3 weeks). After open, questions go through DSIP Q&A and are answered publicly to everyone. The private window is the most valuable thing in the cycle and we found it with three days left.
- Registration (SAM UEI, SBA registry) has to exist before open; it flags on every topic and was never resolved.

## 3. Stage 0's D2P2 rule was wrong in both directions
- The original rule killed any topic mentioning "Direct to Phase II". That falsely killed DPA26BZ06-DV026 (Influence Benchmarks — a top-3 fit) and two others that accept Phase I *and* D2P2.
- Loosening it to "mention ≠ kill" then falsely resurrected two D2P2-only topics whose Phase I paragraph uses different phrasing ("This solicitation is for a D2P2 award", "This DP2 SBIR seeks").
- Current rule (`stage0_screen.py`): STOP only on title prefix or explicit Phase-I-not-accepted phrasing; otherwise flag `T0.1 D2P2 also accepted`. The sbir.gov export strips the PHASE I: header, so the DSIP text (which has it) is more screenable.

## 4. The facility-clearance boilerplate is a Phase II gate, not a Phase I gate
- Nine Release 5 topics were killed PERMANENT on "must be able to acquire and maintain a secret level facility."
- [Q&A, DON26BZ05-NV077] NAVAIR TPOC: "A Secret-level Facility Clearance (FCL) is not required at Phase I award. Uncleared small businesses with a credible sponsorship path are viable offerors. FCL sponsorship and processing will be initiated during Phase I if required for Phase II transition."
- The clause still means Phase II needs a cleared facility and US-only ownership ("no foreign influence" stands). But the kill class should be CONTINGENT (business decision about pursuing FCL sponsorship), not PERMANENT. See addendum in `triage_results.md`.

## 5. Q&A is where the topic gets rewritten — read it before Stage 1, not after
- ARM26BX06-NV012: Q&A removed the apparent DAOSoft dependency and the government-data requirement ("offeror synthetic modeling is sufficient"). Without it the topic reads as wired.
- DAF26BX06-NV510: Q&A confirmed a simulation-only trade study is responsive — the topic text reads as if new fusion algorithms are required.
- DAF26BZ05-DV031 (F-16, killed): Q&A says the SPO owns airworthiness and government SIL/lab access exists, and asks for "artifact generation as part of an integration partnership" — the kill reasoning (no platform access) was overstated; still a poor fit, but for different reasons (integration-partner posture, not impossibility).
- Only 10 of 45 topics with published questions were expanded in the saved page; **all 12 Release 5 PURSUE topics** (≈200 questions) are unread. `parse_sitis_qa.py` handles the page; the panels just need expanding before save (or a browser-driven pull).

## 6. Stage 2 was never actually done
- Every LANDSCAPE line is `[INFERRED]`. The outline calls the SBIR.gov award search "the highest information-per-minute question." It costs minutes per topic and should be run only on the PURSUE list (now 7 + 18), not skipped.

## 7. Batch-mode economics held, but the wrong batch
- 87 → 18 PURSUE in one pass was efficient. The problem was upstream (item 1): effort went into a release we could not act on. Rule for next time: **calendar first, source second, triage third.**

## 8. Data-quality traps seen this cycle
- Truncated topic text at source (DPA26BZ05-DV021: `[Insert chart]`).
- PDF text splits topic numbers (`OSW26BZ06- NV024`) and repeats headers in topic indexes; the STTR CSO doc mislabels ARM26TX06-NV003's body as `BX`.
- NSF category rows and NIH/ARPA-H blurbs share the CSV with DoD topics and are not topics in the same sense.
- Saved SITIS HTML nests `div.row`, producing phantom empty Q/A pairs unless you anchor on the labeled column.

## Next-cycle checklist
1. Pre-release day: download the four DSIP PDFs → `build_release6_csv.py` (generalize the release number) → Stage 0.
2. Same day: Stage 1 on survivors; shortlist ≤5.
3. Days 1–20 (pre-release window): email TPOCs on the shortlist with the decisive-experiment question; run SBIR.gov award search on the shortlist.
4. Open day onward: watch DSIP Q&A for the shortlist; re-run `parse_sitis_qa.py` weekly.
5. Registration must already be done.
