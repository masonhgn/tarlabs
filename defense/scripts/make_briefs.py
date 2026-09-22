import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "briefs")
os.makedirs(OUT, exist_ok=True)

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=17, leading=21, alignment=TA_LEFT, spaceAfter=4)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9.5, leading=12, textColor=colors.HexColor("#444444"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, leading=15, spaceBefore=10, spaceAfter=4,
                    textColor=colors.HexColor("#1f3a5f"))
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontSize=9.8, leading=13, spaceAfter=4)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2)
QUOTE = ParagraphStyle("QUOTE", parent=BODY, leftIndent=14, rightIndent=10, textColor=colors.HexColor("#333333"),
                       backColor=colors.HexColor("#f3f6fa"), borderPadding=(4, 4, 4, 4), spaceAfter=6)
VERDICT = ParagraphStyle("VERDICT", parent=BODY, fontSize=10.5, leading=14, backColor=colors.HexColor("#eef7ee"),
                         borderPadding=(5, 5, 5, 5), spaceAfter=8)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8.5, leading=11, textColor=colors.HexColor("#555555"))


def facts_table(rows):
    t = Table([[Paragraph(f"<b>{k}</b>", BODY), Paragraph(v, BODY)] for k, v in rows],
              colWidths=[1.55 * inch, 5.2 * inch])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def bullets(items):
    return [Paragraph(x, BUL, bulletText="•") for x in items]


def build(filename, title, subtitle, verdict, facts, sections):
    doc = SimpleDocTemplate(os.path.join(OUT, filename), pagesize=letter, leftMargin=0.8 * inch,
                            rightMargin=0.8 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                            title=title, author="defense_research triage")
    story = [Paragraph(title, H1), Paragraph(subtitle, SUB), Spacer(1, 8), Paragraph(verdict, VERDICT),
             facts_table(facts), Spacer(1, 6)]
    for heading, content in sections:
        block = [Paragraph(heading, H2)]
        for item in content:
            if isinstance(item, tuple) and item[0] == "quote":
                block.append(Paragraph(item[1], QUOTE))
            elif isinstance(item, list):
                block.extend(bullets(item))
            else:
                block.append(Paragraph(item, BODY))
        story.append(KeepTogether(block[:2]))
        story.extend(block[2:])
    story.append(Spacer(1, 10))
    story.append(Paragraph("Tags: [TOPIC TEXT] = quoted from the solicitation; [Q&amp;A] = government answer on DSIP; "
                           "[INFERRED] = our judgment, not verified by search. Generated 2026-09-20 from "
                           "release6_triage.md / triage_results.md / sitis_qa.md.", SMALL))
    doc.build(story)
    print("wrote", filename)


COMMON_DATES = "Opens Sep 23, 2026 (TPOC direct contact ends) | DSIP Q&amp;A closes Oct 7, 12:00 ET | Proposals due Oct 21, 12:00 ET"

# ---------------------------------------------------------------------------------------------
build(
    "01_DPA26BZ06-DV026_Influence_Benchmarks.pdf",
    "DPA26BZ06-DV026 - Influence Benchmarks for AI Systems",
    "DARPA | SBIR | Release 6 | " + COMMON_DATES,
    "<b>Recommendation: PURSUE - top candidate.</b> Pure software, an open-source starting point named in the topic, "
    "month-by-month milestones already written for you, CMMC Level 1, no ITAR, and a commercial buyer the sponsor "
    "itself describes. Confidence HIGH.",
    [
        ("Phase I award", "$300,000, 12 months, fixed payable milestones at months 2/6/9/12"),
        ("Proposal format", "DARPA: 10-page white paper + 5-slide deck (not the standard 20-page technical volume)"),
        ("Compliance", "CMMC Level 1. No ITAR clause. D2P2 also accepted but Phase I is open."),
        ("Phase II", "24 months; software + data delivered to DARPA at month 21 for government testing"),
        ("TABA", "DARPA: up to $6,500 Phase I technical assistance on top of the cap"),
    ],
    [
        ("What they want", [
            "A simulated marketplace (auctions/markets with a live 'news feed') where many AI agents trade, so an AI system's "
            "latent preferences - bias, deception, collusion, over-compliance - can be measured purely from its bids, without "
            "access to model weights.",
            ("quote", "[TOPIC TEXT] \"Such a testbed shall rely only on queries and outputs of the subject AI system, rather than "
                      "direct access to the model itself... economic frameworks do not rely on a priori definitions of 'harmful' "
                      "or 'helpful' traits, and these testbeds allow for diverse social strategies such as deception and collaboration.\""),
            "Phase I milestones are explicit:",
            ["Month 2: architecture report - market structures, payout schemes, efficiency and consumer-utility measures, "
             "the dynamic 'news feed', and classifiers for agent behavior.",
             "Month 6: scaling strategy and the agent decision space (bids = time, asset, quantity, price).",
             "Month 9: a suite of 'stock' agents drawn from at least 10 different LLMs, running in the sandbox only.",
             "Month 12: proof-of-concept environment that replicates real bidding patterns with allocative efficiency > 90%, "
             "with data sufficient to compare agents against models of human auction behavior."],
            "Phase II adds 'human' reference agents, an error function vs. expected human results, and quantitative metrics on "
            "how deception/collaboration change market outcomes.",
        ]),
        ("How we would build it", [
            "Core is a discrete-event market simulator plus an agent harness plus an analytics layer - all backend/ML work.",
            ["<b>Market engine:</b> pluggable mechanisms (English/Dutch/sealed-bid auctions, continuous double auction) with a "
             "clearing house, order book, payout rules and logged state. Deterministic seeds so runs are reproducible.",
             "<b>Information layer:</b> a scripted and generative 'news feed' with controllable truth/noise so we can test how "
             "agents update beliefs and whether they exploit or spread misinformation.",
             "<b>Agent harness:</b> a common interface for LLM agents (API and open-weight), scripted rational/zero-intelligence "
             "bidders (the classic Gode-Sunder baseline), and later 'human' agents fit to published auction-experiment data.",
             "<b>Classifiers/metrics:</b> allocative efficiency, price convergence, bid-shading, winner's-curse behavior, "
             "collusion signatures (tacit price coordination), deception (stated vs. revealed valuation), herding on the feed.",
             "<b>Experiment runner:</b> batch execution across model x market x feed conditions, with cost tracking per LLM call."],
            "Start from Magentic Marketplace (open source, cited in the topic) to avoid rebuilding the agent-market plumbing; "
            "extend it toward auctions, efficiency accounting and the classifiers, which it does not focus on.",
        ]),
        ("Resources we would use", [
            ["Magentic Marketplace (Microsoft, arXiv 2510.25779) - the named open-source environment.",
             "OpenAgentSafety (arXiv 2507.06134) and the NVIDIA agent-evaluation guidance the topic cites - for framing and vocabulary.",
             "Experimental-economics literature on auction behavior (Hausch 1986; Martinez-Saito 2019) to define 'human-like' baselines.",
             "LLM access: a mix of API models and open-weight models (to reach the 10-LLM requirement cheaply).",
             "Standard Python simulation stack; nothing exotic. No hardware."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>API cost:</b> 10+ LLMs x many market rounds x repeated seeds can get expensive; budget for it explicitly and lean on "
             "open-weight models for volume runs.",
             "<b>Human baseline validity:</b> the >90% allocative-efficiency target is easy for scripted bidders but the comparison "
             "to human behavior needs defensible calibration - an experimental-economics advisor (a few hours/month) would help.",
             "<b>Classifier definition:</b> 'bias' in a market is not self-evident; the Month-2 report has to commit to measurable "
             "constructs (bid-shading, misinformation uptake, collusion index) before agents exist.",
             "<b>Crowded adjacent space:</b> AI-safety evals are busy; the differentiator is the economic-mechanism framing, so the "
             "proposal must not read like a generic LLM benchmark.",
             "<b>Format:</b> 10 pages + 5 slides means the white paper must be tight; milestones map one-to-one to the topic's."],
        ]),
        ("Decision factors", [
            ["Fit to team: highest of any topic in either release - simulation, agents, classifiers, backend.",
             "Dual use: [TOPIC TEXT] \"AI firms have strong market demand for the capability to benchmark the influence of their "
             "systems\" (liability exposure) - a real commercial product line, not a detour.",
             "No clearance, no ITAR, CMMC 1 - lowest compliance friction available.",
             "Decisive pre-proposal experiment: run Magentic Marketplace (or a minimal double auction) with 3-4 LLMs plus a "
             "scripted bidder, inject a news shock, and check whether efficiency lands near 90% and a simple classifier separates "
             "agent types from bid streams. Doing this before Oct 21 would give the white paper real data."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask whether API-hosted proprietary LLMs count toward the 10, and whether agents may be "
            "fine-tuned or must be used as-is (affects budget and the 'sandbox only' clause).",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "02_ARM26BX06-NV012_Agentic_Decision_Management.pdf",
    "ARM26BX06-NV012 / ARM26TX06-NV003 - Agentic-AI, Schema-Driven Decision Management",
    "Army (DEVCOM GVSC) | SBIR (NV012) and STTR twin (NV003) | Release 6 CSO | " + COMMON_DATES,
    "<b>Recommendation: PURSUE (submit to one twin, not both).</b> The Q&amp;A removed the two things that made the topic look "
    "wired - the DAOSoft dependency and the need for Army data. Phase I is 'proof by demonstration', synthetic data is "
    "explicitly acceptable, CMMC Level 1, no ITAR. Confidence HIGH on fit.",
    [
        ("Phase I award", "Up to $300,000, 1-6 months (Army CSO, 'Phase I (Feasibility)')"),
        ("Proposal format", "Army CSO technical volume: 7 pages for Phase I (verify against Section 3 of the Army instructions)"),
        ("Compliance", "CMMC Level 1. No ITAR clause. Army CSO (Commercial Solutions Opening) evaluation, not classic BAA."),
        ("Phase II", "Two cases from PAE Maneuver Ground and PAE Fires; COTS-style product the Army and industry would both use"),
        ("STTR twin", "NV003: identical text; needs a research institution at >= 30% of the work"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] \"Prove a decision-as-a-program capability that turns complex engineering/acquisition questions "
                      "into structured, auditable Decision Packages - faster, with higher confidence.\""),
            "Phase I desired outcomes:",
            ["A decision schema in which objectives, options, constraints, assumptions, risks and bias checks are first-class objects.",
             "An agentic layer that performs structured elicitation into that schema, generates a decision workflow plan, and runs "
             "reproducible evaluations with explicit \"what flips the decision\" logic.",
             "Two end-to-end demonstrations: one point-in-time trade study, one long-horizon decision program with refresh cycles."],
            "Context engineering for the ground-vehicle domain (knowledge graphs / semantic layers), interoperability with "
            "digital-engineering artifacts (SysML 2.0, UML), and human control per human-AI interaction guidance are all named.",
        ]),
        ("What the Q&amp;A changed", [
            ["[Q&amp;A] \"DAOSoft is not a requirement!\" - offerors may use their own platform, integrate with DAOSoft, or replace it.",
             "[Q&amp;A] \"For Phase I, offeror generic documents are sufficient\" and \"offeror synthetic modeling is sufficient if PAE "
             "or PM data is not forthcoming\" - no government data wall.",
             "[Q&amp;A] Either demonstration structure is acceptable; \"the government supports a fresh innovative approach.\"",
             "[Q&amp;A] On 'open-source' in Phase II: \"COTS is better... Offerors will own their own code, and the government places "
             "no restrictions on an offeror chosen distribution model.\" The intent is avoiding government-maintained code.",
             "[Q&amp;A] The effort is framed as \"100% new effort\" toward agentic AI for rapid product decisions."],
        ]),
        ("How we would build it", [
            ["<b>Schema:</b> a typed decision model (JSON Schema / Pydantic) - Decision, Option, Criterion, Constraint, Assumption "
             "(with evidence and confidence), Risk, BiasCheck, RefreshTrigger - versioned so a decision program is a sequence of "
             "schema instances over time.",
             "<b>Elicitation agent:</b> LLM agent that interviews a user and ingests documents (requirements, spec sheets, cost tables) "
             "into the schema with citations; every field carries provenance.",
             "<b>Evaluation engine:</b> deterministic scoring (weighted criteria, constraint satisfaction, Monte Carlo on uncertain "
             "assumptions) producing the ranked options and a sensitivity table: which assumption or weight flips the top choice.",
             "<b>Refresh loop:</b> when an assumption's evidence changes, re-run and produce a delta report - this is the 'long-horizon "
             "decision program' demonstration.",
             "<b>Audit/trust layer:</b> bias checks as executable tests (anchoring on incumbent option, missing alternatives, "
             "unstated assumptions), full run logs, signer-ready package export (PDF/SysML-compatible artifact).",
             "<b>Demonstrations:</b> (1) a vehicle-subsystem trade study built from public sources (e.g., powertrain or armor "
             "options with published cost/weight data); (2) a multi-year 'program' where new evidence arrives each cycle."],
        ]),
        ("Resources we would use", [
            ["Public ground-vehicle trade-study material (SAE papers, GAO/CRS reports on Army vehicle programs) for synthetic cases.",
             "SysML v2 open tooling (pilot implementation / API) to show interoperability with digital-engineering artifacts.",
             "The topic's own reference: SAE 2025-01-0455 (agentic decision-intelligence framework) - align vocabulary with the author.",
             "DAOSoft public site (daosoft.ai) to understand the incumbent's structured-decision UX without depending on it.",
             "LLM agent framework of choice; graph store for the semantic layer if needed. No hardware."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>Incumbent adjacency:</b> DAOSoft is on GVSC's network and the topic author knows it; a proposal must show clear "
             "advance beyond 'structured trade study + LLM', i.e., reproducibility, sensitivity and refresh logic.",
             "<b>Acquisition-domain credibility:</b> Army acquisition decision programs have their own vocabulary (AoA, KPPs, "
             "milestone decisions). A short engagement with a former acquisition professional would de-risk the demos.",
             "<b>Determinism vs. LLMs:</b> reviewers will ask how an LLM-driven pipeline is 'reproducible'; the architecture must "
             "confine the LLM to elicitation/authoring and keep evaluation deterministic.",
             "<b>Page limit:</b> 7 pages is very short for a two-demo plan; the schema and the sensitivity logic must be shown "
             "compactly (one figure each).",
             "<b>SBIR vs STTR choice:</b> the STTR twin requires an RI partner; only worth it if a university decision-science or "
             "MBSE group adds credibility we cannot show ourselves."],
        ]),
        ("Decision factors", [
            ["Fit to team: schema + workflow + evaluation harness + LLM orchestration - direct.",
             "Dual use: [TOPIC TEXT] \"the vehicle design process for the automotive industry\"; more broadly any product-development "
             "trade-study workflow (a generic 'decision package' tool).",
             "Phase III framing is ERP-style deployment per customer - a services-heavy model; decide whether that is a business "
             "you want.",
             "Decisive pre-proposal experiment: encode one public trade-off in the schema, run the deterministic evaluator, then "
             "perturb one assumption and confirm the 'what flips the decision' output is correct and traceable."],
            "<b>Before Oct 7 (Q&amp;A):</b> the PAE data answers are still 'pending' - ask whether any unclassified PAE Maneuver Ground "
            "case will be released in Phase I, and whether a SysML v2 export is expected or merely desirable.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "03_DAF26BX06-NV510_AI_ML_Missile_Warning.pdf",
    "DAF26BX06-NV510 - AI/ML for Next Generation of Missile Detection, Warning, Tracking, and Reporting",
    "USAF / SpaceWERX with SSC Space Sensing Delta 84 and the OPIR Tap Lab | SBIR | Release 6 CSO | " + COMMON_DATES,
    "<b>Recommendation: PURSUE (feasibility-study track).</b> The TPOC confirmed in Q&amp;A that a simulation-driven trade study "
    "with no new detection algorithm is responsive. Small award, short period, ITAR staffing constraint. Confidence MEDIUM-HIGH.",
    [
        ("Phase I award", "$150,000, 3 months (SpaceWERX CSO)"),
        ("Proposal format", "Technical volume limit 30 pages (per the DAF CSO index table)"),
        ("Compliance", "ITAR/EAR clause: foreign nationals must be disclosed and may be restricted. CMMC Level 2 (Self)."),
        ("Phase II", "Development and testing inside the OPIR Tap Lab or similar testbed; transition path is SSC's Space Modernization Initiative"),
        ("Deliverable", "Feasibility study + CONOPS + analytical findings; algorithm prototypes or simulation results 'as applicable'"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] \"Proposals should emphasize technical feasibility and clearly outline a Phase I research plan that "
                      "can include modeling, simulation, literature review, or trade studies... Phase I deliverables are expected to "
                      "focus on a feasibility study detailing USSF CONOPS and technical viability, as well as analytical findings.\""),
            "Four focus areas, any part of which is acceptable: edge fusion and autonomy (on-orbit track fusion, constellation "
            "tasking); multi-source integration (OPIR + EO + radar + SIGINT + commercial); OODA-loop collapse and mission assurance "
            "(orchestration, edge computing, 'AI trade-space exploration', explainability); and new sources/methods outside current TTPs.",
            "The feasibility study must identify benefits over existing solutions, risks with mitigations, critical technology "
            "elements, and evidence for each CTE (literature, trade studies, analysis, heritage).",
        ]),
        ("What the Q&amp;A changed", [
            ["[Q&amp;A] A \"deterministic simulation that screens the multi-orbit OPIR sensing trade space... to find where AI/ML fusion "
             "would have real leverage before Phase II\" - \"Yes, a feasibility study would be appropriate for this topic.\"",
             "[Q&amp;A] An in-space edge-compute architecture effort (hosting, not inventing, the algorithms) is responsive; document it "
             "with DoDAF 2.0-style architecture products.",
             "[Q&amp;A] \"Mission-aware orchestration and AI-assisted trade-space decision management\" is \"an appropriate submission\" "
             "for the OODA focus area.",
             "[Q&amp;A] Future use of the Phase I product (offline tool vs. Tap Lab plug-in) is decided at the end of Phase I."],
        ]),
        ("How we would build it", [
            ["<b>Constellation and sensing simulator:</b> propagate synthetic GEO/MEO/LEO constellations (public two-line-element "
             "style orbits), model sensor fields of view, revisit and data cadence, and link latency.",
             "<b>Threat set:</b> synthetic boost/glide trajectories for ballistic and maneuvering profiles from open-literature "
             "kinematics - no real threat data.",
             "<b>Fusion placement experiments:</b> compare ground-centralized vs. on-orbit/edge fusion for warn-to-decision latency, "
             "track continuity through handovers, and robustness to dropped links; identify where AI/ML data association adds "
             "value versus classical filters.",
             "<b>Explainability/confidence:</b> propagate confidence through the pipeline so the CONOPS can state what an operator "
             "sees and when automation hands off.",
             "<b>Deliverables:</b> the feasibility study (benefits, risks, CTEs with evidence), a system-level CONOPS, and the "
             "simulation as a reusable analysis tool with a stated path into the OPIR Tap Lab."],
        ]),
        ("Resources we would use", [
            ["Public orbit propagation tooling (SGP4-class libraries, open astrodynamics packages) and public catalog data for "
             "constellation geometry.",
             "Open literature on OPIR missile-warning architectures (Next-Gen OPIR, HBTSS-class concepts as publicly described) and "
             "multi-sensor tracking (JPDA/MHT, learned data association).",
             "OPIR Tap Lab public material (boulderlab.org) for integration expectations.",
             "GAO TRL guide (cited in the topic) for the maturity language reviewers expect.",
             "No hardware. Compute is modest."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>ITAR staffing:</b> any non-US-person contributor must be disclosed and may be excluded from technical data.",
             "<b>Three months, $150k:</b> scope must be a crisp trade study, not a platform; over-promising algorithms is the "
             "classic failure here.",
             "<b>Domain vocabulary:</b> missile-warning CONOPS reviewers expect fluency (revisit, dwell, handover, typing). A "
             "space-sensing advisor would materially improve the CONOPS section.",
             "<b>Incumbency:</b> established OPIR ground-processing primes are around this program; the Tap Lab exists precisely to "
             "onboard non-traditionals, which helps, but Phase II integration will require working inside their environment.",
             "<b>Transition dependence:</b> value realization depends on being invited into the Tap Lab; Phase I is a foot in the door."],
        ]),
        ("Decision factors", [
            ["Fit to team: simulation + data pipelines + ML - direct; astrodynamics is learnable at the fidelity a trade study needs.",
             "Dual use: [INFERRED] multi-orbit sensor tasking and fusion resemble commercial EO-constellation scheduling and space "
             "traffic management; the topic itself names none.",
             "Strategic value: opens the SpaceWERX/SSC relationship at low cost; the 3-month award is small but fast.",
             "Decisive pre-proposal experiment: build a two-constellation revisit/latency simulator against a synthetic launch and "
             "show one chart where fusion placement changes warn-to-decision time - that chart belongs in the proposal."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask whether unclassified OPIR-like sample data or Tap Lab sandbox access is available in "
            "Phase I, and what architecture artifacts the Tap Lab expects at handoff.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "04_DAF26TZ06-NV007_Combat_Assessment_at_the_Edge.pdf",
    "DAF26TZ06-NV007 - Automated Combat Assessment at the Edge",
    "USAF (AFRL) | STTR | Release 6 | " + COMMON_DATES,
    "<b>Recommendation: PURSUE with a remote-sensing research partner.</b> An edge-ML damage-classification problem with a "
    "public benchmark dataset that maps almost exactly onto the ask. STTR requires a research institution; ITAR applies. "
    "Confidence MEDIUM-HIGH.",
    [
        ("Phase I award", "$300,000, 6 months"),
        ("Proposal format", "Technical volume 20 pages"),
        ("Compliance", "ITAR/EAR clause (foreign nationals restricted). CMMC Level 2 (Self). STTR: RI >= 30%, small business >= 40%."),
        ("Phase I deliverable", "Analysis and design of the system with preliminary laboratory model testing; feasibility findings and a Phase II plan"),
        ("Phase II", "Functional prototype software + model weights on representative edge hardware, ICDs, demo in a simulated or operationally relevant environment"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] \"Awardees must demonstrate an innovative approach to physical and functional combat assessment, "
                      "and novel or under-utilized data modalities.\""),
            "Three components: edge-processing software that runs on sensors/UAVs under low SWaP and contested comms; AI/ML "
            "damage classification (physical and functional) aligned to CJCSI 3162.02 with confidence intervals per ICD 203; "
            "and phased test and evaluation from lab to simulated to field.",
            "The sponsor names the data problem itself: \"the lack of real time pre- and post-event satellite imagery for model "
            "training.\" A proposal that solves the training-data problem credibly has an edge.",
            "Phase III named uses: urban surveillance, disaster and humanitarian response.",
        ]),
        ("How we would build it", [
            ["<b>Model:</b> lightweight change-detection/segmentation network on pre/post image pairs (building- and vehicle-level "
             "damage classes), distilled and quantized for Jetson/Coral-class boards.",
             "<b>Functional damage layer:</b> rule/graph reasoning on top of physical damage (e.g., a radar site is 'functionally "
             "destroyed' if antenna and power are hit) - this is the under-served half of the ask.",
             "<b>Novel modalities:</b> add SAR change detection (day/night, cloud) and thermal signatures; fuse with EO. Public SAR "
             "and thermal datasets exist to show feasibility.",
             "<b>Confidence reporting:</b> calibrated probabilities mapped to ICD 203 language (e.g., 'likely', 'highly likely'), "
             "with an evidence chain per assessment.",
             "<b>Edge/comms:</b> compact assessment messages, on-device queueing for intermittent links, and a bandwidth budget.",
             "<b>Phase I lab test:</b> accuracy/latency/power on the edge board against a held-out damage benchmark."],
        ]),
        ("Resources we would use", [
            ["xBD / xView2 building-damage dataset (pre/post disaster imagery with damage grades) - the standard public benchmark.",
             "Public SAR archives (Sentinel-1, Capella open data) for change-detection experiments; FLIR-class public thermal sets.",
             "CJCSI 3162.02A (combat assessment methodology) and ICD 203 (analytic standards) - both public, both cited in the topic.",
             "COTS edge boards: NVIDIA Jetson Orin Nano, Coral Edge TPU, Hailo-8L.",
             "RI partner: a university remote-sensing / computer-vision lab (needed for STTR and for the 'novel modalities' credibility).",
             "AFRL BAA FA8750-25-S-7002 'Targeting Operations and Analytics Development' (cited) - read for the sponsor's framing."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>Domain gap:</b> disaster damage is not combat damage; military target types and functional-kill logic need SME "
             "input, and real military pre/post imagery is unavailable in Phase I.",
             "<b>STTR partner timing:</b> an RI agreement must be in place by Oct 21; start the conversation immediately.",
             "<b>ITAR:</b> staffing restriction on foreign nationals.",
             "<b>Edge constraints:</b> the topic wants low SWaP under contested comms - the model must actually run on the board, "
             "not just in the cloud; demonstrate this in Phase I.",
             "<b>Competition:</b> AFRL Rome's targeting/analytics ecosystem has incumbents; the differentiator must be the "
             "functional-assessment reasoning and the modality fusion, not a generic detector."],
        ]),
        ("Decision factors", [
            ["Fit to team: edge ML pipelines - strong (same skill set as the Release 5 semantic-ISR topic).",
             "Dual use: disaster/humanitarian damage mapping is an existing commercial and NGO market.",
             "Decisive pre-proposal experiment: fine-tune a small segmentation model on xBD, quantize for a Jetson, and report "
             "accuracy, latency and watts - three numbers that would anchor the technical volume."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask whether representative pre/post military-target imagery will be furnished in Phase II, "
            "which sensor modalities the sponsor considers 'under-utilized', and the target edge hardware class.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "05_DAF26TX06-NV514_Space_Domain_Assessment.pdf",
    "DAF26TX06-NV514 - Space Domain Operational Environment Assessment (Technical Area 2)",
    "USAF / USSF | STTR | Release 6 CSO | " + COMMON_DATES,
    "<b>Recommendation: PURSUE TA2 only, with an astrodynamics research partner.</b> TA2 is a data-fusion / analytics / "
    "decision-support software design problem; TA1 (new sensing phenomenologies) is out of reach. Small award, 10-page "
    "limit, ITAR. Confidence MEDIUM.",
    [
        ("Phase I award", "$175,000, 6 months"),
        ("Proposal format", "Technical volume 10 pages (DAF STTR CSO index table)"),
        ("Compliance", "ITAR/EAR clause. CMMC Level 2 (Self). STTR: RI >= 30%. 'GFE will not be provided.'"),
        ("Phase I (TA2)", "Design a workable, scalable prototype concept; identify data sources; define metrics and Phase II success criteria"),
        ("Phase II (TA2)", "Prototype software assessing space operations from multi-INT data, shown with modeling, simulation and real-world data"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] TA2: \"Design a concept for a workable and scalable prototype to address the basic capabilities and "
                      "technical feasibility of the stated objective as well as data and information sources and the timeliness of "
                      "their solution. Identify non-traditional phenomenology and data sources. Define a set of metrics and success "
                      "criteria for a Phase 2 prototype.\""),
            "The problem is operations assessment: compare forecasted outcomes to actual events to judge whether a space task "
            "achieved its effect, in a domain where operators cannot directly observe effects or adversary reaction.",
            "Phase II success criteria: a demonstrated software prototype measured against metrics and a CONOPS use case; outputs "
            "that integrate into operational workflows with minimal user burden; a Phase III path with customers and funding.",
            "Phase III explicitly includes maturing the software into \"a commercial product for commercial SDA\" and providing "
            "\"health and operational status of commercial satellites and their services in relation to adversaries' actions.\"",
        ]),
        ("How we would build it", [
            ["<b>Data layer:</b> ingest public catalogs (element sets, conjunction messages), space-weather feeds, launch notices, "
             "and open-source reporting as a proxy for multi-INT; normalize to an event/object graph with provenance.",
             "<b>Pattern-of-life models:</b> per-object maneuver and RF/optical behavior baselines; anomaly detection for "
             "unexpected maneuvers, station-keeping breaks, proximity operations.",
             "<b>Assessment engine:</b> represent a planned task with measures of performance/effectiveness, forecast expected "
             "observables, then score observed vs. forecast - the 'did it work?' logic the topic is really asking for.",
             "<b>Timeliness metrics:</b> detection lead time, time-to-assessment, false-alarm rate - defined in Phase I, measured in Phase II.",
             "<b>Operator view:</b> a lightweight assessment dashboard that fits into existing workflows (the same pattern as the "
             "Release 5 NAVWAR APNT topic)."],
        ]),
        ("Resources we would use", [
            ["Public catalog data (space-track.org, Celestrak), conjunction data messages, space-weather services.",
             "Open astrodynamics libraries for propagation and maneuver detection; the AMOS conference papers cited in the topic "
             "(multi-phenomenology characterization with RL; passive-RF cislunar tracking) for the state of the art.",
             "Joint Publications 3-14, 5-0, 3-60 and the Space Capstone Publication (cited) for assessment doctrine and vocabulary.",
             "RI partner: a university astrodynamics / space-situational-awareness group (covers orbital mechanics credibility).",
             "No hardware; no GFE will be provided, so the data plan must be entirely public/commercial."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>Data realism:</b> real multi-INT is classified; the proposal must argue convincingly that public/commercial data "
             "suffices to prove the assessment logic, and that classified feeds slot in later.",
             "<b>Commercial incumbents:</b> commercial SDA analytics firms already sell catalog/conjunction products; our lane must "
             "be assessment and adversary-intent reasoning, not another catalog.",
             "<b>10-page limit and STTR partner:</b> both constrain how much can be shown; a strong figure of the assessment loop "
             "is essential.",
             "<b>ITAR staffing.</b>",
             "<b>Scope creep into TA1:</b> stay out of new-sensor territory; reviewers will score TA2 on the analytics design."],
        ]),
        ("Decision factors", [
            ["Fit to team: data integration, anomaly detection, dashboards - strong; astrodynamics via the RI.",
             "Dual use: explicitly stated by the sponsor (commercial SDA product, commercial satellite health vs. adversary action).",
             "Decisive pre-proposal experiment: from public element-set histories, detect a set of known, publicly reported "
             "maneuvers and report lead time and false alarms - a concrete TA2 metric to put in the proposal."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask whether TA2-only proposals are welcome, what 'non-traditional data sources' the sponsor "
            "has in mind for TA2, and whether any unclassified operational assessment examples can be shared.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "06_OSW26BZ06-NV028_5G_Signature_Deception.pdf",
    "OSW26BZ06-NV028 - 5G Signature Tracking Mitigation via Cyber Deception",
    "OSD FutureG | SBIR | Release 6 | " + COMMON_DATES,
    "<b>Recommendation: PURSUE if a cellular-protocol partner is available.</b> Phase I is a concept design, feasibility "
    "study and design document; the hard problem (AI personas that defeat ML pattern-of-life tracking) is an ML problem. "
    "Phase II needs small decoy devices. ITAR. Confidence MEDIUM.",
    [
        ("Phase I award", "Up to $323,090, 6 months (OSW FutureG cost volume rule)"),
        ("Proposal format", "Technical volume 20 pages"),
        ("Compliance", "ITAR/EAR clause. CMMC Level 2 (Self)."),
        ("Phase I deliverables", "Kickoff/TIM slides, monthly status reports, Preliminary Design Document (AI-persona generation and ID-swapping mechanics), Phase II plan, final report"),
        ("Phase II", "Prototype to TRL 7: mission-management software plus hardened decoy boxes (router-sized team device, puck-sized personal device); field demo on a 5G test network"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] \"an advanced digital signature management and deception system that obfuscates cellular metadata "
                      "('digital exhaust') to protect personnel, small units, and critical facilities from adversarial surveillance, "
                      "tracking, and pattern-of-life analysis on 3rd-party commercial networks.\""),
            "Suggested key performance metrics: 2 (threshold) to 4+ (objective) AI personas broadcast per decoy device; 12 to "
            "24-36 hours battery; under 2 lb (~1 lb objective); obfuscation realism that defeats basic heuristics (threshold) "
            "up to advanced ML-based behavioral tracking (objective). Proposers must define their own quantifiable KPMs.",
            "Phase I is six months of concept, algorithms and a software-architecture design document, plus a PDR.",
        ]),
        ("How we would build it", [
            ["<b>Persona generator:</b> a generative sequence model of mobility and device-usage patterns (location trace, call/data "
             "cadence, app-traffic mix, dwell times) conditioned on a mission plan, producing several concurrent believable personas.",
             "<b>Adversary model:</b> our own pattern-of-life tracker (the kind an adversary would run on CDR/location metadata) used "
             "as the discriminator - realism is measured as the tracker's failure to separate real from decoy or to find the unit.",
             "<b>Mission planner:</b> AI-enabled planning of when/where personas appear and how identities rotate so deviations "
             "that signal 'VIP visit' or 'mission prep' are masked.",
             "<b>Device architecture (design only in Phase I):</b> COTS cellular modems / SDR modules on an SBC with SIM/eSIM identity "
             "management; ID-swapping mechanics documented with the legal/operational envelope.",
             "<b>Evaluation harness:</b> synthetic and public mobility datasets; metrics per KPM."],
        ]),
        ("Resources we would use", [
            ["Public mobility/trajectory datasets (GeoLife, taxi/GPS traces, open CDR-style research datasets) to train and test "
             "persona realism.",
             "Open-source cellular stacks (srsRAN, OpenAirInterface) and a lab 5G core for Phase II test-network work.",
             "DoDI 8520.02 (cited) for identity/credential handling constraints.",
             "Cellular-protocol partner or consultant for identity, SIM and network-attach behavior.",
             "COTS modems, eSIM management, small SBCs - benchtop-sourceable."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>Protocol and legal depth:</b> generating decoy identities on third-party networks touches SIM provisioning, IMSI/IMEI "
             "behavior and carrier terms; the design document must be credible on this without in-house telecom experience.",
             "<b>Realism bar is high:</b> defeating ML-based behavioral tracking is an adversarial-ML arms race; the honest framing is "
             "measurable degradation of tracker performance, not invisibility.",
             "<b>Phase II hardware:</b> hardened 1-lb devices with 24-36 h battery is a product-engineering job; plan a hardware sub.",
             "<b>ITAR staffing.</b>",
             "<b>Operational validation:</b> field demo on a 5G test network requires range access the government does not promise."],
        ]),
        ("Decision factors", [
            ["Fit to team: the realism/generation/evaluation core is ML and backend - strong; radios are not.",
             "Dual use: [TOPIC TEXT] protecting corporate executives, personnel and IP from commercial espionage and tracking - "
             "a plausible executive-protection / travel-security product.",
             "Decisive pre-proposal experiment: train a persona generator on a public trajectory dataset and show a standard "
             "pattern-of-life classifier cannot separate synthetic from real traces above chance - directly evidences the "
             "'obfuscation realism' KPM."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask whether Phase I may remain software/design-only, whether a test 5G network will be "
            "available in Phase II, and how the sponsor expects identity swapping to be lawful on third-party networks.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "07_OSW26BZ06-DV025_Compact_Passive_Radar.pdf",
    "OSW26BZ06-DV025 - Compact Passive Radar",
    "OSD Reliance 21 | SBIR | Release 6 | " + COMMON_DATES,
    "<b>Recommendation: PURSUE only with an RF partner; otherwise HOLD.</b> Phase I wants a simulation plus a basic lab "
    "prototype, which is feasible on COTS software-defined radios, but the X-band SAR/GMTI requirement and the Phase II "
    "miniaturized hardware are well beyond a software team alone. Confidence LOW-MEDIUM.",
    [
        ("Phase I award", "$314,363, 12 months"),
        ("Proposal format", "Technical volume 20 pages"),
        ("Compliance", "ITAR/EAR clause. CMMC Level 2 (Self)."),
        ("Phase I deliverable", "System architecture, low-cost receiver components, antenna configurations, edge-processing hardware selection; proof-of-concept algorithms; 'a robust simulation and a basic laboratory prototype'"),
        ("Phase II", "Miniaturized hardware prototype on a small UAS or ground node; outdoor passive detection, tracking and imaging; unit-cost and SWaP validation"),
    ],
    [
        ("What they want", [
            ("quote", "[TOPIC TEXT] \"a Small Form Factor (SFF) passive X-Band radar featuring both Synthetic Aperture Radar (SAR) imaging "
                      "and Ground Moving Target Indicator (GMTI) capabilities... light enough for integration onto Group 1 or 2 UAS, "
                      "loitering munitions, or unattended ground sensors.\" 100% receive-only; \"the sensor shall not transmit any RF energy.\""),
            "Phase I algorithms named: reference-signal isolation, clutter cancellation, target detection/tracking under constrained "
            "compute. The end product is a simulation and a benchtop prototype validating detection from signals of opportunity "
            "within SWaP-C limits.",
            "Phase III commercial uses named: low-cost air-traffic monitoring, counter-UAS for critical infrastructure, airspace "
            "monitoring where adding active RF is undesirable.",
        ]),
        ("How we would build it", [
            ["<b>Simulation:</b> bistatic geometry, illuminator waveform models, clutter and direct-path interference; cross-ambiguity "
             "processing and CFAR detection; SAR/GMTI feasibility analysis for candidate X-band illuminators.",
             "<b>Lab prototype:</b> a coherent multi-channel COTS SDR (4-5 channel), reference and surveillance antennas, and our "
             "processing chain running on a Jetson-class edge board; detect a cooperative moving target using a local broadcast "
             "illuminator to prove the chain, then analyze the X-band case.",
             "<b>Edge compute budgeting:</b> profile the pipeline to size the attritable processor.",
             "<b>Architecture study:</b> component costs, antenna form factors for Group 1/2 UAS, and a path to a custom multi-channel "
             "X-band receiver in Phase II."],
        ]),
        ("Resources we would use", [
            ["Multi-channel coherent SDRs (KrakenSDR-class, USRP) with public passive-radar toolchains and tutorials.",
             "Principles of Modern Radar Vol. 3 and Adaptive Radar Resource Management (both cited) - the sponsor's reference frame.",
             "Academic passive bistatic radar literature (FM/DVB-T/cellular illuminators; X-band passive SAR studies).",
             "RF/antenna partner for the X-band front end and Phase II miniaturization."],
        ]),
        ("Bottlenecks and risks", [
            ["<b>X-band illuminators of opportunity are scarce:</b> most public passive-radar work uses FM/TV/cellular; X-band "
             "requires cooperative or specific illuminators (satellite/marine radars). This could invalidate the SAR/GMTI ask for "
             "our approach - check the literature before committing.",
             "<b>Hardware in Phase II:</b> a miniaturized, tightly synchronized multi-channel X-band receiver is real RF engineering.",
             "<b>Domain expertise:</b> bistatic SAR and clutter cancellation are specialist areas.",
             "<b>ITAR staffing.</b>",
             "<b>Incumbents:</b> ESM/SIGINT houses the topic criticizes still have the receivers; our cost angle is the wedge."],
        ]),
        ("Decision factors", [
            ["Fit to team: signal-processing software and edge compute - partial; RF hardware - none.",
             "Dual use: explicitly stated and credible (counter-UAS, airspace monitoring).",
             "Decisive pre-proposal experiment: with a COTS multi-channel SDR and a public toolchain, detect a moving target off a "
             "local broadcast illuminator and measure processing load - proves the software chain, then decide on the X-band question."],
            "<b>Before Oct 7 (Q&amp;A):</b> ask which X-band illuminators of opportunity the sponsor envisions, whether cooperative "
            "illumination is acceptable in Phase I/II demos, and whether a lower band is acceptable for the Phase I lab prototype.",
        ]),
    ],
)

# ---------------------------------------------------------------------------------------------
build(
    "08_Release5_closing_Sep23_top3.pdf",
    "Release 5 - three strongest fits (all close Sep 23, 2026, 12:00 ET)",
    "DON26BX05-NP004 | OSW26BZ05-DV018 | DON26BZ05-NV071 | SBIR | Release 5 | Q&amp;A closed; direct TPOC contact closed",
    "<b>Only actionable if SAM.gov UEI and SBA registrations already exist.</b> These three were the highest-confidence "
    "Release 5 fits. Each has published DSIP questions we have not read (24, 21 and 7 respectively). If registration is "
    "not live, treat them as the pattern of topic to watch for next cycle.",
    [
        ("Awards (typical)", "Navy Phase I ~$140k-$240k / 6 months (base + option, per Navy instructions); OSW ~$250k-$323k / 6-12 months - verify in the Release 5 instructions"),
        ("Compliance", "No clearance clauses on these three; NP004 and NV071 have no ITAR clause; DV018 none in text"),
        ("Deadline", "September 23, 2026, 12:00 ET - three days from this brief"),
    ],
    [
        ("DON26BX05-NP004 - NAVWAR Open Topic: Unified APNT Operational Awareness and Decision Support", [
            ("quote", "[TOPIC TEXT] \"This topic does not seek development of new PNT... hardware systems. Instead, the Department seeks "
                      "expertise in software architecture, data integration, information management, user experience (UX), "
                      "human-machine interface (HMI) design, analytics, visualization, and decision-support technologies.\""),
            ["<b>What they want:</b> a single operational picture of GPS/alternate-PNT system health, confidence, threats, degradations "
             "and recommended courses of action, ingesting through GPNTS; containerized, on-prem.",
             "<b>Build:</b> data-integration layer over the open-source ASPN / pntOS data types named in the topic, a confidence/degradation "
             "model, and a decision-support dashboard; prototype on synthetic multi-source PNT status streams.",
             "<b>Resources:</b> ASPN and pntOS (open source, named in the topic); commercial ops-center dashboard patterns the sponsor "
             "explicitly invites (telecom NOC, logistics, industrial monitoring).",
             "<b>Bottlenecks:</b> real GPNTS schemas and feeds arrive after award; APNT vocabulary; 24 unread Q&amp;A entries likely "
             "address data availability - read them before writing anything.",
             "<b>Why it fits:</b> the sponsor wrote a software/UX topic and said commercial analogues are welcome. Confidence HIGH."],
        ]),
        ("OSW26BZ05-DV018 - AI/ML-Based Radar Data Compression", [
            ("quote", "[TOPIC TEXT] \"Phase I is to explore autoencoder architectures for radar data... Phase I will benchmark compression "
                      "ratios vs. classical methods.\" Dual use: \"any high-rate sensor (remote lidar, sensor webs)... UAS radar streams "
                      "or... weather radar data.\""),
            ["<b>Build:</b> complex-valued autoencoders on raw pulses / range-Doppler maps; benchmark ratio vs. fidelity vs. downstream "
             "detection; quantization-aware training for the Phase II embedded target.",
             "<b>Resources:</b> public SAR data (MSTAR, Sentinel-1 SLC, Capella open data); the sponsor notes recent literature on "
             "neural compression in the complex SAR domain.",
             "<b>Bottlenecks:</b> true raw-pulse data may not be public (processed imagery likely suffices for the Phase I benchmark); "
             "21 unread Q&amp;A entries.",
             "<b>Why it fits:</b> an ML research-and-benchmark task with public data and a stated dual-use market. Confidence HIGH."],
        ]),
        ("DON26BZ05-NV071 - Dynamically Generated, Articulated 3-D Training Content", [
            ("quote", "[TOPIC TEXT] \"a low-code/no-code software platform for the automated generation of AR/MR training content that "
                      "requires minimal source media (e.g., smartphone photos, video, Computer-aided design model, or schematics)\""),
            ["<b>Build:</b> photos/CAD to Gaussian-splat or NeRF reconstruction, automated part segmentation to infer articulation, "
             "procedural-logic authoring without code, export to Unity/Unreal and Navy HMDs.",
             "<b>Resources:</b> open-source 3D Gaussian Splatting / NeRF pipelines, part-segmentation models, Unity/Unreal exporters.",
             "<b>Bottlenecks:</b> reliable automatic articulation from static reconstructions is the unsolved piece; Navy LVC export "
             "standards; 7 unread Q&amp;A entries.",
             "<b>Why it fits:</b> largest civilian market of any topic reviewed (industrial training, e-commerce, VR). Confidence MEDIUM-HIGH."],
        ]),
        ("Decision", [
            "If registrations exist and one proposal is feasible in three days, NP004 is the one: pure software, open-source starting "
            "point, sponsor-stated commercial analogues, no compliance clauses. Otherwise, let Release 5 go and put the effort into "
            "the Release 6 briefs (01-07), which have a month and an open Q&amp;A window.",
        ]),
    ],
)
