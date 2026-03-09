# file: langgraph_examples/example14_paper_report.py
"""
Paper Report PDF Generator
───────────────────────────
Reads paper_summaries.csv and papers.csv, merges them, and generates
a well-formatted PDF report. Each paper entry includes:
  - Paper name (title)
  - URL (file link)
  - LLM-generated summary
  - Original abstract
"""

from pathlib import Path

import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
SUMMARIES_CSV = OUTPUT_DIR / "paper_summaries.csv"
PAPERS_CSV = DATA_DIR / "papers.csv"
OUTPUT_PDF = OUTPUT_DIR / "paper_report.pdf"


# ─── Custom PDF class ────────────────────────────────────────────────────────

class PaperReportPDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "Systematic Review - Paper Summaries Report", align="C")
        self.ln(4)
        self.set_draw_color(70, 130, 180)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, number, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(25, 60, 120)
        self.multi_cell(0, 6, f"{number}. {title}")
        self.ln(1)

    def field_label(self, label):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, label)
        self.ln(4)

    def field_body(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 4.5, text)
        self.ln(2)

    def separator(self):
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(10, y, self.w - 10, y)
        self.ln(5)


# ─── Sanitize text for PDF ───────────────────────────────────────────────────

def sanitize(text: str) -> str:
    """Replace characters that fpdf can't render in latin-1."""
    if not isinstance(text, str):
        return ""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u2022": "-",    # bullet
        "\u00a0": " ",    # non-breaking space
        "\u2192": "->",   # right arrow
        "\u2190": "<-",   # left arrow
        "**": "",         # markdown bold
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


# ─── Build the PDF ───────────────────────────────────────────────────────────

def generate_report(summaries_csv: Path, papers_csv: Path,
                    output_pdf: Path):
    summaries_df = pd.read_csv(summaries_csv)
    papers_df = pd.read_csv(papers_csv)

    merged = summaries_df.merge(
        papers_df[["ID", "authors", "Abstract", "arxiv_id"]],
        on="ID",
        how="left",
    )

    print(f"Loaded {len(merged)} papers")
    print(f"Generating PDF report: {output_pdf.name}")

    pdf = PaperReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Title page info ───────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Total papers: {len(merged)}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    success = merged[~merged["Summary"].str.startswith("[", na=False)]
    pdf.cell(0, 6, f"Successfully summarized: {len(success)}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # ── Paper entries ─────────────────────────────────────────────────
    for idx, row in merged.iterrows():
        paper_id = row.get("ID", idx + 1)
        title = sanitize(str(row.get("Title", "Unknown")))
        url = str(row.get("URL", ""))
        summary = sanitize(str(row.get("Summary", "")))
        abstract = sanitize(str(row.get("Abstract", "")))
        arxiv_id = str(row.get("arxiv_id", ""))

        if pdf.get_y() > 240:
            pdf.add_page()

        pdf.section_title(paper_id, title)

        pdf.field_label("URL:")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(70, 130, 180)
        pdf.cell(0, 4, url, new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=url)
        pdf.ln(2)

        if arxiv_id and arxiv_id != "nan":
            pdf.field_label("File:")
            pdf.field_body(f"{arxiv_id}.pdf")

        pdf.field_label("Summary:")
        pdf.field_body(summary if summary and summary != "nan" else "N/A")

        pdf.field_label("Abstract:")
        pdf.field_body(abstract if abstract and abstract != "nan" else "N/A")

        pdf.separator()

    pdf.output(str(output_pdf))
    print(f"\nPDF report written to {output_pdf}")
    print(f"  File size: {output_pdf.stat().st_size / 1024:.1f} KB")


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Paper Report — PDF Generator")
    print("=" * 60)
    generate_report(SUMMARIES_CSV, PAPERS_CSV, OUTPUT_PDF)
