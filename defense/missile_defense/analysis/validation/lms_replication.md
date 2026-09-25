# S-08 — Replication of Li & Zhang (2000), Table IV

**Source.** X. R. Li and Y. M. Zhang, "Multiple-Model Estimation with Variable Structure
— Part V: Likely-Model Set Algorithm", *IEEE Transactions on Aerospace and Electronic
Systems* **36**(2), April 2000, pp. 448–466. Local copy:
`data/raw/literature/li_zhang_2000_lms.pdf` (scanned, no text layer).

**Code.** `mwsim/lz2000.py` (the benchmark, transcribed), `mwsim/lms.py` (LMS3 as
published), `scripts/replicate_lms.py` (the run), `tests/test_lz2000.py` and
`tests/test_lms.py` (57 tests). Numeric output: `analysis/validation/lms_table_iv.json`.

---

## Why this was done

The third rung of our classical baseline ladder (DEC-40) is variable-structure IMM, put
there on the strength of a sentence in the Li & Jilkov survey: where the Likely-Model Set
algorithm has been compared against fixed-structure IMM it *"substantially outperforms"*
it. We built a VS-IMM, measured no accuracy advantage, and recorded that as a failed
reproduction (DEC-41).

That record was not honest enough. We had invented the model bank, the scenario, the noise
levels and the adjacency graph, and then compared the result against a claim whose
experimental conditions we had never looked at. A comparison like that cannot confirm the
claim and cannot refute it. So the claim was traced to its primary source and the source's
own experiment was run.

## What the source actually reports

Table IV, p. 461. RMS position error in metres, over 500 Monte Carlo runs.

| case | IMM | LMS | LMS/IMM | LMS(λ) | LMS(λ)/IMM | LMS FLOP ratio |
|---|---|---|---|---|---|---|
| topology A, random | 39.56 | 40.10 | 1.014 | 37.83 | 0.956 | 0.384 |
| topology A, det. 1 | 37.15 | 37.58 | 1.012 | 35.85 | 0.965 | 0.358 |
| topology A, det. 2 | 41.52 | 42.43 | 1.022 | 37.86 | **0.912** | 0.382 |
| topology B, random | 36.93 | 36.94 | 1.000 | 35.79 | 0.969 | 0.651 |
| topology B, det. 1 | 35.28 | 35.30 | 1.001 | 35.29 | 1.000 | 0.596 |
| topology B, det. 2 | 36.47 | 36.73 | 1.007 | 36.28 | 0.995 | 0.556 |

**Plain LMS is worse than fixed-structure IMM on position accuracy in all six cases.** It
is never better, in either topology, in either deterministic scenario, or in the random
one. What it delivers is cost: 36–65% of the IMM's FLOPs.

The paper's own summary of its own table says this and nothing stronger:

> the LMS and MGS algorithms are much more cost-effective than the IMM estimator

Cost-effectiveness — not accuracy. The only accuracy improvement in Table IV belongs to
**LMS(λ)**, the variant carrying the forgetting factor of equations (18)–(20), and it is
3.5–8.8% on the sparse topology A and essentially nil on the dense topology B.

So there was never a "substantial" accuracy advantage for us to fail to reproduce. Our
earlier measurement — matched accuracy, far fewer filters — was the *correct* result, and
DEC-41 mis-described it as a shortfall. DEC-42 supersedes it.

## What was replicated

Everything in Section VI was transcribed: the thirteen nearly-constant-velocity models
with specified expected accelerations (eq. 28), both adjacency index matrices (eqs. 31–32),
both 13×13 transition probability matrices (eqs. 33–34), `Q¹ = (0.003)²I` and
`Qⁱ = (0.008)²I`, `R = 1250I`, thresholds `t₁ = 10⁻⁴` and `t₂ = 0.3`, the model-set floor
`K` = 5 and 9, the initial mode probabilities, the Table III deterministic scenarios, and
the semi-Markov random scenario of eqs. (29)–(30).

Because the source is a scan, transcription is the main risk. Two independent checks
guard it:

1. **Ω against Π.** The paper states the same graph twice in two unrelated notations —
   adjacency index matrices and transition probability matrices, typeset separately. A
   transition probability is non-zero exactly where a switch is legitimate. They agree
   cell for cell (`TestOmegaAgreesWithPi`).
2. **Graph against geometry.** Topology A's off-diagonal edges are all at Euclidean
   distance 20 m/s² in the acceleration grid; topology B's are at 20 and 20√2 — exactly
   "nearest neighbours" and "second nearest neighbours" as the text describes.

Two parameters the paper never states are inferred and flagged in `lz2000.INFERRED`: the
sampling period (taken as 1 s, from the integer time axis of Figs. 4–7) and the track
initialisation (two-point differencing). Neither can manufacture a difference between
estimators, because every estimator receives the identical initial condition; and
`test_estimation_error_is_invariant_to_where_the_target_starts` asserts that the unreported
initial state cannot affect any reported error.

## Result — 500 Monte Carlo runs

`python scripts/replicate_lms.py --runs 500`

| case | estimator | our RMSPE | paper | Δ | our /IMM | paper /IMM | filters/step |
|---|---|---|---|---|---|---|---|
| A, random | IMM | 34.03 | 39.56 | −14.0% | 1.0000 | 1.0000 | 13.00 |
| | LMS | 34.55 | 40.10 | −13.8% | 1.0151 | 1.0137 | 5.76 |
| | LMS(λ) | 34.05 | 37.83 | −10.0% | 1.0005 | 0.9563 | 5.77 |
| A, det. 1 | IMM | 37.72 | 37.15 | **+1.5%** | 1.0000 | 1.0000 | 13.00 |
| | LMS | 38.49 | 37.58 | +2.4% | 1.0203 | 1.0116 | 5.99 |
| | LMS(λ) | 37.86 | 35.85 | +5.6% | 1.0037 | 0.9650 | 6.00 |
| A, det. 2 | IMM | 42.10 | 41.52 | **+1.4%** | 1.0000 | 1.0000 | 13.00 |
| | LMS | 43.63 | 42.43 | +2.8% | 1.0363 | 1.0219 | 6.21 |
| | LMS(λ) | 41.77 | 37.86 | +10.3% | 0.9921 | 0.9118 | 6.25 |
| B, random | IMM | 32.30 | 36.93 | −12.5% | 1.0000 | 1.0000 | 13.00 |
| | LMS | 32.30 | 36.94 | −12.6% | 1.0002 | 1.0003 | 9.25 |
| | LMS(λ) | 32.16 | 35.79 | −10.1% | 0.9959 | 0.9691 | 9.26 |
| B, det. 1 | IMM | 35.77 | 35.28 | **+1.4%** | 1.0000 | 1.0000 | 13.00 |
| | LMS | 35.79 | 35.30 | +1.4% | 1.0005 | 1.0006 | 9.33 |
| | LMS(λ) | 35.82 | 35.29 | +1.5% | 1.0013 | 1.0003 | 9.34 |
| B, det. 2 | IMM | 36.90 | 36.47 | **+1.2%** | 1.0000 | 1.0000 | 13.00 |
| | LMS | 37.09 | 36.73 | +1.0% | 1.0053 | 1.0071 | 9.38 |
| | LMS(λ) | 37.01 | 36.28 | +2.0% | 1.0030 | 0.9948 | 9.39 |

### What reproduced

**The fixed-structure IMM, to 1.2–1.5%,** in all four deterministic cases. Thirteen
models, a 13×13 transition matrix, two process-noise levels, an inferred sampling period
and an unstated initialisation — and the answer lands within a percent and a half of the
published number four times out of four. A misread digit anywhere in that chain would not
produce this.

**The central finding.** Plain LMS is behind IMM in every case, in our run as in theirs,
and the per-case ratios track: 1.0002 against 1.0003 on topology B random, 1.0005 against
1.0006 on B/1, 1.0053 against 1.0071 on B/2. The dense topology matches almost exactly;
the sparse one we degrade somewhat more than they do.

**The compute saving.** LMS runs 5.8–6.3 of 13 filters on topology A and 9.3–9.4 on
topology B. The paper's FLOP ratios for LMS (0.358–0.384 and 0.556–0.651) sit below our filter
fractions, as they should — FLOPs also capture the quadratic mixing arithmetic, where a
5-model set saves far more than 5/13. Same ordering, same magnitude, measured differently.

### What did not reproduce, stated plainly

**The random scenario comes out ~13% easier than theirs.** All three estimators shift
together by the same amount, so the relative comparison is unaffected and the LMS/IMM
ratios still match the published ones closely — but the absolute level does not replicate.
The likely cause is our reading of eqs. (29)–(30): the sojourn-time and magnitude
distributions are fully specified but the process is described in prose, and small
differences in how segments are drawn change the manoeuvre density. Deterministic
scenarios, which leave nothing to interpretation, replicate to 1.2–1.5%.

**LMS(λ)'s accuracy advantage reproduces in direction only.** The paper gets 3.5–8.8% on
topology A; we get roughly 1%, and only in one case does our LMS(λ) beat IMM at all
(A/det. 2, by 0.8%). Equations (18)–(20) leave genuine ambiguity: whether λ resets on each
manoeuvre detection or decays once, whether the inflation applies at activation only or
persists, and what counts as "newly activated" across a step where the set both grows and
shrinks. We chose one reading, documented it in `LMSFilter._advance_forgetting`, and are
not going to search the others until the number improves — that would be fitting to a
published answer rather than replicating a method.

This matters for how the result may be used. **We can say, on our own evidence, that plain
LMS buys compute and not accuracy.** We cannot say how much accuracy the forgetting factor
is worth; we can only report that the source claims 3.5–8.8% on a sparse topology and that
we see the same sign at a smaller size.

## Algorithm details that turned out to matter

Implementing LMS3 from Table I rather than from the survey's prose changed the answer
twice (DEC-43):

- **One-step-back activation.** *"A good and systematic technique is to go back several
  steps in time to initialize the newly activated models and their filters… One-step back
  is recommended and was used in our examples"* (pp. 454–455). A model activated
  mid-manoeuvre is otherwise born from a stale prediction and must compete on the very
  measurement that triggered it. Adding this cut our topology-A gap from +5.9% to +3.6%
  and peak error from 84 m to 74 m.
- **AND-logic deletion.** LMS3 discards a model only if it is unlikely **and** not
  adjacent from a principal model. A model the target is about to switch into is protected
  while its probability is still negligible.

A third suggestion in the paper — repeatedly applying the adaptation rules within one time
step, offered as a cure for LMS3's *"weakness in handling jumps between two widely
separated modes that are connected only through several intermediate modes"* — was
implemented and measured at **no effect at all**, to four decimal places. A newly activated
model is essentially never principal in the step it appears, so the loop exits immediately.
It is left in place, off by default, and recorded here rather than quietly dropped.

## Correctness of our implementation

With a fully connected adjacency graph, no model is ever discardable and expansion never
finds anything new, so LMS3 must degenerate into an ordinary fixed-structure IMM. It
agrees with `mwsim/imm.py` to **6e-11** on states of order 10⁵ m — relative machine
precision. Since `mwsim/imm.py` already agrees with FilterPy's `IMMEstimator` to 8.5e-14
(DEC-39), this chains the variable-structure implementation back to a third-party
reference.

## Consequences for the study

1. **The baseline ladder survives, with its third rung re-labelled.** Variable structure
   belongs in the comparison, but as a *cost* reduction at matched accuracy, not an
   accuracy improvement. Any later ML claim must beat fixed-structure IMM on accuracy and
   LMS on cost — which is a harder and more honest bar than beating one filter.
2. **The compute result feeds DEC-29 directly.** Edge fusion cannot win by shortening the
   signal path, so the on-orbit question reduces to a compute breakeven. A filter bank
   that runs 45% of its models at unchanged accuracy moves that breakeven, and now does so
   on replicated rather than self-generated evidence.
3. **A citation discipline.** The survey sentence was accurate about the literature it
   summarised and misleading about this paper. Any remaining load-bearing claim taken from
   a survey should be traced to primary source before it is built on.
