# Accountability checklist — standing version

Answered at the end of **every** progress brief, in full, by the agent and then reviewed by
Mason. The point is not to feel good; it is to find the places we fooled ourselves before a
reviewer does. A "no" or "don't know" is a useful answer. An unexamined "yes" is not.

Each answer gets a status: **OK**, **WATCH** (known weakness, contained) or **ACT** (needs a
task row in PLAN.md before the next brief).

## A. Evidence — do we know what we think we know?

1. Is every load-bearing claim traced to a **primary source we have actually read** — not a
   survey, not an abstract, not a research-assistant summary?
2. Which claims rest on **deep-research output we have not independently verified**? How
   many of its citations did we check?
3. Have we concluded "nobody has done X" or "X doesn't exist" **without searching**?

## B. Verification — is the code right?

4. For every module we rely on, **what independent reference is it checked against**? List
   any module with none.
5. Is there any replication with an **unexplained residual difference**? Did we investigate
   it, or explain it away?
6. Did we **change a method after seeing its results**? If so, was the change justified by
   the source *before* we saw the number?

## C. Assumptions — how much of each number is ours?

7. For each headline number, what fraction is assumption? Is **every** one in
   `analysis/assumptions_register.md`?
8. Which conclusions **flip** if a notional parameter moves across its declared range?

## D. Shortcuts and depth

9. What is marked **DONE whose artifact is thinner than its name** suggests?
10. What data did we acquire and **never use**? Why?
11. What did we **skip or postpone because it was hard or blocked**, and is that written down?

## E. Contribution and honesty

12. What is our claimed contribution **today**, and what is the **closest prior art**, read
    in full?
13. What result would **falsify** our main claim? Have we run that test?

## F. Process and reproducibility

14. Is all work **committed to version control**? Can a stranger regenerate every number
    from one command?
15. Are PLAN.md, CLAUDE.md and the decisions log **current**? Any drift?
16. Were gate reviews **real reviews by Mason**, or agent summaries accepted?

## G. Outside world

17. Status of every **externally clocked** item (registrations, TPOC contact, Q&A, template)?
18. Is the work still aimed at the topic's **four metrics plus explainability and
    confidence** — or drifting toward what is interesting?

## H. Where to dig

19. If you had to point at one or more parts of the process and say *"let's check whether we
    really did this correctly and well"*, what are they — and what **targeted research
    prompt** would settle each one?
