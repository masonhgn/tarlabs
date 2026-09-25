"""Render a progress brief from its HTML source to PDF.

    python progress_briefs/build_brief.py brief_01_2026-09-24

Uses PyMuPDF's Story layout engine (already a project dependency), so no new packages.
"""

from __future__ import annotations

import sys
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
PAGE = fitz.paper_rect("letter")
MARGIN = 54  # 0.75 in


def build(stem: str) -> Path:
    html = (HERE / f"{stem}.html").read_text(encoding="utf-8")
    out = HERE / f"{stem}.pdf"
    story = fitz.Story(html=html)
    writer = fitz.DocumentWriter(str(out))
    frame = PAGE + (MARGIN, MARGIN, -MARGIN, -MARGIN)
    more = True
    while more:
        device = writer.begin_page(PAGE)
        more, _ = story.place(frame)
        story.draw(device)
        writer.end_page()
    writer.close()

    # Page numbers, added after layout so they never disturb it.
    doc = fitz.open(out)
    for i, page in enumerate(doc):
        page.insert_text(
            (PAGE.width / 2 - 20, PAGE.height - 28),
            f"{i + 1} / {len(doc)}",
            fontsize=8,
            color=(0.45, 0.45, 0.45),
        )
    doc.saveIncr()
    doc.close()
    return out


if __name__ == "__main__":
    stem = sys.argv[1] if len(sys.argv) > 1 else "brief_01_2026-09-24"
    print(build(stem))
