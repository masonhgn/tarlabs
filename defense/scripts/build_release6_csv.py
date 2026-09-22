import csv
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

BRANCH = {"ARM": "ARMY", "DAF": "USAF", "DON": "NAVY", "DPA": "DARPA", "OSW": "OSD",
          "SOC": "SOCOM", "DME": "DMEA", "DTR": "DTRA", "MDA": "MDA", "DHA": "DHA"}
CLOSE = "October 21, 2026"
HEAD_RE = re.compile(r"(?m)^\s*([A-Z]{2,3}26[BT][XZ]06-\s?[A-Z]{2}\d{3})\s+TITLE:\s*(.+?)\s*$")
# the STTR CSO document labels the ARM26TX06-NV003 body with an SBIR-style number
ALIAS = {"ARM26BX06-NV003": "ARM26TX06-NV003"}
# a topic body ends at its KEYWORDS paragraph; fall back to page footers / appendices / next header
END_PATTERNS = [
    re.compile(r"KEYWORDS:.*?(?:\n\s*\n|\n\s*[A-Z/]+ - \d+\s*\n)", re.S),
    re.compile(r"\n\s*Appendix [A-Z]\b"),
    re.compile(r"\n\s*\d\.\d+\s+[A-Z][A-Za-z ]{4,}\n"),
]


def blocks(txt):
    heads = list(HEAD_RE.finditer(txt))
    for i, h in enumerate(heads):
        hard_end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
        body = txt[h.end():hard_end]
        if "OBJECTIVE:" not in body[:1500]:
            continue  # Topic Index stub, not the real block
        end = len(body)
        m = END_PATTERNS[0].search(body)
        if m:
            end = m.end()
        else:
            for pat in END_PATTERNS[1:]:
                m = pat.search(body)
                if m:
                    end = min(end, m.start())
        num = h.group(1).replace(" ", "")
        title = re.sub(r"\s+", " ", h.group(2))
        # titles wrap onto the next line in the PDF text
        nxt = body.lstrip("\n").split("\n", 1)[0].strip()
        if nxt and not re.match(r"^(OUSW|COMPONENT|PROJECTED|OBJECTIVE|TECHNOLOGY|MODERNIZATION)", nxt):
            title = f"{title} {nxt}"
        yield ALIAS.get(num, num), title, body[:end]


def main():
    rows = {}
    for f in sorted(glob.glob(str(RAW / "release6_*.txt"))):
        txt = open(f, encoding="utf-8").read()
        for num, title, body in blocks(txt):
            desc = re.sub(r"[ \t]+", " ", body)
            desc = re.sub(r"\n{2,}", "\n", desc).strip()
            rows[num] = {
                "Topic Title": title.strip(),
                "Topic Description": desc,
                "Topic Number": num,
                "Phase": "BOTH",
                "Program": "STTR" if num[5] == "T" else "SBIR",
                "Agency": "DOD",
                "Branch": BRANCH.get(num[:3], num[:3]),
                "Close Date": CLOSE,
                "Release Date": "September 2, 2026",
                "Open Date": "September 23, 2026",
                "Solicitation Agency URL": "https://www.dodsbirsttr.mil/topics-app/",
                "Solicitation Status": "Open",
                "Solicitation Year": "2026",
                "SBIRTopicLink": "",
                "_source": Path(f).name,
            }
    cols = ["Topic Title", "Topic Description", "Topic Number", "Phase", "Program", "Agency", "Branch",
            "Close Date", "Release Date", "Open Date", "Solicitation Agency URL", "Solicitation Status",
            "Solicitation Year", "SBIRTopicLink"]
    with open(PROCESSED / "release6_raw.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for num in sorted(rows):
            w.writerow(rows[num])
    print(f"{len(rows)} topics written to release6_raw.csv")
    for num in sorted(rows):
        r = rows[num]
        print(f"  {num:18} {r['Program']:4} {r['Branch']:6} {len(r['Topic Description']):6} chars  {r['Topic Title'][:60]}")


if __name__ == "__main__":
    main()
