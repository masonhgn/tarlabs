import csv
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
ANALYSIS = ROOT / "analysis"

HTML = RAW / "Topics and Topic Search (SITIS).html"
RESULTS = ANALYSIS / "triage_results.md"


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""


def parse_panels(soup):
    topics = []
    for panel in soup.select("mat-expansion-panel"):
        num_el = panel.select_one(".topic-number-status")
        num = re.search(r"[A-Z]{2,3}\d{2}[BT][XZ]\d{2}-[A-Z]{2}\d{3}", text(num_el))
        entry = {
            "topic_number": num.group(0) if num else text(num_el),
            "title": text(panel.select_one(".topic-title")),
            "component": text(panel.select_one(".topic-component")),
            "program": text(panel.select_one(".topic-program")),
            "release": text(panel.select_one(".topic-releaseNumber")),
            "baa": text(panel.select_one(".topic-baa")),
            "question_count": text(panel.select_one("em.questionCount")),
            "detail_text": text(panel.select_one(".topicDetailBox")),
            "qa": [],
        }
        body = panel.select_one(".mat-expansion-panel-body")
        if body is not None:
            pending_q = None
            for row in body.select("div.row"):
                # only rows whose own first column carries the Question:/Answer: label
                strong = row.select_one(":scope > .col-sm-1 > p > strong")
                if strong is None:
                    continue
                label = text(strong)
                val = row.select_one(":scope > .col-sm-11")
                if label.startswith("Question"):
                    pending_q = {"question": text(val), "answer": ""}
                    entry["qa"].append(pending_q)
                elif label.startswith("Answer") and pending_q is not None:
                    pending_q["answer"] = text(val)
                    pending_q = None
        topics.append(entry)
    return topics


def verdicts_from_results():
    out = {}
    try:
        md = open(RESULTS, encoding="utf-8").read()
    except FileNotFoundError:
        return out
    for block in md.split("```"):
        m = re.search(r"TOPIC:\s+(\S+)\s+—", block)
        v = re.search(r"VERDICT:\s+(\w+)", block)
        if m and v:
            out[m.group(1)] = v.group(1)
    return out


def main():
    soup = BeautifulSoup(open(HTML, encoding="utf-8", errors="ignore").read(), "lxml")
    topics = parse_panels(soup)
    verdicts = verdicts_from_results()
    for t in topics:
        t["triage_verdict"] = verdicts.get(t["topic_number"], "NOT IN SURVIVORS")

    with open(PROCESSED / "sitis_qa.json", "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)

    with open(PROCESSED / "sitis_qa.md", "w", encoding="utf-8") as f:
        f.write("# SITIS Q&A dump — pre-release questions and government answers\n\n")
        f.write(f"Source: `{HTML.name}` (saved 2026-09-20). {len(topics)} topic panels; "
                f"{sum(1 for t in topics if t['qa'])} with expanded Q&A; "
                f"{sum(len(t['qa']) for t in topics)} Q/A pairs.\n\n")
        f.write("| # | Topic | Rel | Verdict | Published Qs | Captured Q/A |\n|---|---|---|---|---|---|\n")
        for t in topics:
            f.write(f"| {t['topic_number']} | {t['title'][:70]} | {t['release']} | {t['triage_verdict']} | "
                    f"{t['question_count'] or '-'} | {len(t['qa'])} |\n")
        f.write("\n---\n\n")
        for t in topics:
            if not t["qa"]:
                continue
            f.write(f"## {t['topic_number']} — {t['title']}\n\n")
            f.write(f"**{t['component']} / {t['program']}** · triage verdict: **{t['triage_verdict']}**\n\n")
            for i, qa in enumerate(t["qa"], 1):
                f.write(f"**Q{i}.** {qa['question']}\n\n**A{i}.** {qa['answer']}\n\n")
            f.write("---\n\n")

    with open(PROCESSED / "sitis_qa.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topic_number", "title", "component", "program", "triage_verdict", "question", "answer"])
        for t in topics:
            for qa in t["qa"]:
                w.writerow([t["topic_number"], t["title"], t["component"], t["program"],
                            t["triage_verdict"], qa["question"], qa["answer"]])

    print(f"{len(topics)} panels, {sum(len(t['qa']) for t in topics)} Q/A pairs")
    print("Topics with Q&A, by verdict:")
    for t in topics:
        if t["qa"]:
            print(f"  {t['topic_number']:18} {t['triage_verdict']:18} {len(t['qa']):3} Q/A  {t['title'][:60]}")


if __name__ == "__main__":
    sys.exit(main())
