"""Render the saved written answers to a readable, linked PDF using reportlab."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Flowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor("#142A43")
GOLD = colors.HexColor("#9A742D")
MUTED = colors.HexColor("#526173")
PALE = colors.HexColor("#F1F4F7")
WIDTH = A4[0] - 92


def markup(text: str) -> str:
    text = text.replace("–", "-").replace("—", "-").replace("’", "'")
    text = escape(text)
    text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#235A8A">\1</link>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    return text


class ProcessFigure(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = WIDTH, 306

    def draw(self):
        canvas = self.canv
        box_w, box_h, gap = (WIDTH - 36) / 3, 49, 18
        labels = [
            ("01  Applicant", "Identity, consent, period"),
            ("02  Upload", "Invoice Excel + bank PDFs"),
            ("03  Parse + validate", "Retain source lineage"),
            ("04  Normalize + match", "Check coverage and receipts"),
            ("05  Human review", "Resolve uncertain evidence"),
            ("06  Metrics + AI flags", "Separate facts from suggestions"),
            ("07  Freeze package", "Versioned source references"),
            ("08  Reviewer approval", "Approve exact package hash"),
            ("09  Bank submission", "Durable intent; stable reference"),
            ("10  Observe + reconcile", "Unknown outcome: hold, verify"),
            ("11  Human escalation", "Resolve conflicting bank states"),
            ("12  Confirmed decision", "Bank retains underwriting"),
        ]
        positions = []
        # Serpentine: each row continues into the next without crossing lines.
        for index in range(12):
            row, col = divmod(index, 3)
            if row % 2:
                col = 2 - col
            x, y = col * (box_w + gap), self.height - 28 - (row + 1) * box_h - row * 19
            positions.append((x, y))
        for index, ((title, subtitle), (x, y)) in enumerate(zip(labels, positions)):
            canvas.setFillColor(PALE if index not in (4, 7, 10) else colors.HexColor("#F7F0E3"))
            canvas.setStrokeColor(colors.HexColor("#CED6DF"))
            canvas.roundRect(x, y, box_w, box_h, 5, fill=1, stroke=1)
            canvas.setFillColor(NAVY)
            canvas.setFont("Helvetica-Bold", 8.7)
            canvas.drawString(x + 8, y + 30, title)
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 7.1)
            canvas.drawString(x + 8, y + 13, subtitle)
        canvas.setStrokeColor(GOLD)
        canvas.setFillColor(GOLD)
        for i in range(11):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            if y1 == y2:
                right = x2 > x1
                start = x1 + box_w if right else x1
                end = x2 if right else x2 + box_w
                y = y1 + box_h / 2
                canvas.line(start, y, end, y)
                step = -4 if right else 4
                canvas.line(end, y, end + step, y + 3)
                canvas.line(end, y, end + step, y - 3)
            else:
                x = x1 + box_w / 2
                canvas.line(x, y1, x, y2 + box_h)
                canvas.line(x, y2 + box_h, x - 3, y2 + box_h + 4)
                canvas.line(x, y2 + box_h, x + 3, y2 + box_h + 4)


def build() -> Path:
    target = ROOT / "output/pdf/qawafel-assessment.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BodyTextCustom", fontName="Helvetica", fontSize=9.2, leading=13.5, spaceAfter=6, textColor=NAVY, allowWidows=0, allowOrphans=0))
    styles.add(ParagraphStyle("TitleCustom", fontName="Helvetica-Bold", fontSize=24, leading=28, spaceAfter=12, textColor=NAVY))
    styles.add(ParagraphStyle("TaskHeading", fontName="Helvetica-Bold", fontSize=17, leading=21, spaceBefore=12, spaceAfter=10, textColor=NAVY, keepWithNext=True))
    styles.add(ParagraphStyle("SectionCustom", fontName="Helvetica-Bold", fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=7, textColor=GOLD, keepWithNext=True))
    styles.add(ParagraphStyle("CellCustom", fontName="Helvetica", fontSize=7.8, leading=11, textColor=NAVY))
    styles.add(ParagraphStyle("CodeCustom", fontName="Courier", fontSize=7.3, leading=10, leftIndent=8, rightIndent=8, spaceAfter=8, backColor=PALE))
    styles.add(ParagraphStyle("CaptionCustom", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED, spaceAfter=10))
    body = styles["BodyTextCustom"]
    story = []
    lines = (ROOT / "docs/assessment_answers.md").read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            story.extend([
                Paragraph("TECHNICAL ASSESSMENT / 24 OCTOBER 2026", styles["CaptionCustom"]),
                Paragraph(markup(line[2:]), styles["TitleCustom"]),
                Paragraph("Wholesaler Financing Insights<br/>Written requirements, technical design, and integration judgment", body),
                Spacer(1, 8),
            ])
        elif line.startswith("## "):
            title = line[3:]
            if title.startswith(("Task 2", "Task 4")):
                story.append(PageBreak())
            story.append(Paragraph(markup(title), styles["TaskHeading"]))
        elif line.startswith("### "):
            if line == "### End-to-end process":
                story.append(KeepTogether([
                    Paragraph(markup(line[4:]), styles["SectionCustom"]),
                    ProcessFigure(),
                    Paragraph("Figure 1. Proposed production flow. Validation failures return for correction. Unknown or contradictory bank outcomes remain on hold for verification; they never trigger an automatic resend. Gold-tinted steps require human judgment.", styles["CaptionCustom"]),
                ]))
            else:
                story.append(Paragraph(markup(line[4:]), styles["SectionCustom"]))
        elif line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.extend(textwrap.wrap(lines[i], width=94, break_long_words=True, break_on_hyphens=False) or [""])
                i += 1
            story.append(Paragraph("<br/>".join(escape(item) for item in code), styles["CodeCustom"]))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+", cell) for cell in cells):
                    rows.append([Paragraph(markup(cell), styles["CellCustom"]) for cell in cells])
                i += 1
            i -= 1
            cols = len(rows[0])
            widths = [WIDTH * .22, WIDTH * .45, WIDTH * .33] if cols == 3 else [WIDTH * .34, WIDTH * .66]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), .7, colors.HexColor("#BCCAD7")),
            ]))
            story.extend([table, Spacer(1, 9)])
        elif line.startswith("- "):
            story.append(Paragraph(markup(line[2:]), ParagraphStyle("ListItemCustom", parent=body, leftIndent=10, firstLineIndent=0, spaceAfter=5), bulletText="-"))
        elif re.match(r"^\d+\. ", line):
            number, text = line.split(". ", 1)
            story.append(Paragraph(markup(text), ParagraphStyle("NumberedItemCustom", parent=body, leftIndent=15, spaceAfter=5), bulletText=number + "."))
        else:
            paragraph = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].lstrip().startswith(("#", "|", "```", "- ")) and not re.match(r"^\d+\. ", lines[i + 1].strip()):
                i += 1
                paragraph.append(lines[i].strip())
            story.append(Paragraph(markup(" ".join(paragraph)), body))
        i += 1

    def page_frame(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(.8)
        canvas.line(46, A4[1] - 34, A4[0] - 46, A4[1] - 34)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(46, 25, "Mishal Saad | Qawafel graduate assessment | Synthetic data only")
        canvas.drawRightString(A4[0] - 46, 25, f"{doc.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=46, leftMargin=46, topMargin=48, bottomMargin=43,
                                 title="Qawafel Graduate Software Engineer Assessment", author="Mishal Saad")
    document.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    print(target)
    return target


if __name__ == "__main__":
    build()
