"""
reporting_utils.py — Core utility functions for automated reporting and visualization.

Provides:
  - Master CSV loader and validator
  - High-resolution publication chart generators
  - Markdown table formatters
  - ReportLab PDF report generation engine
"""

import os
import sys
import yaml
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

# Load config
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "report_config.yaml")
with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
    REPORT_CONFIG = yaml.safe_load(f)

# Global aesthetic settings
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.autolayout": True,
})

MODEL_COLORS = {
    "autoencoder": "#1f77b4",
    "patchcore": "#2ca02c",
    "padim": "#ff7f0e",
    "dip_optimization": "#d62728",
    "hybrid_fusion": "#9467bd",
}


def load_master_df(csv_path: str = None) -> pd.DataFrame:
    """Load and sanitize master experimental study CSV."""
    if csv_path is None:
        csv_path = REPORT_CONFIG["paths"]["master_csv"]
    if not os.path.isabs(csv_path):
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        csv_path = os.path.join(proj_root, csv_path)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Master CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Standardize column types
    numeric_cols = [
        "image_auroc", "pixel_auroc", "average_precision",
        "precision", "recall", "f1_score",
        "training_time_s", "inference_time_s", "gpu_memory_mb", "model_size_mb",
        "training_samples", "test_samples"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean strings
    str_cols = ["experiment_id", "model", "category", "experiment_type", "status", "evidence_type"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def get_completed_experiments(df: pd.DataFrame) -> pd.DataFrame:
    """Filter for successfully completed experiment runs."""
    return df[df["status"].str.lower() == "completed"].copy()


def df_to_markdown_table(df: pd.DataFrame, float_format: str = "{:.4f}") -> str:
    """Convert a DataFrame to a clean GitHub Flavored Markdown table."""
    formatted_df = df.copy()
    for col in formatted_df.select_dtypes(include=[np.number]).columns:
        formatted_df[col] = formatted_df[col].apply(
            lambda x: "—" if pd.isna(x) else float_format.format(x) if isinstance(x, (float, np.floating)) else str(x)
        )
    try:
        return formatted_df.to_markdown(index=False)
    except Exception:
        # Fallback pure-python markdown table generator
        headers = list(formatted_df.columns)
        lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in formatted_df.iterrows():
            lines.append("| " + " | ".join(str(val) for val in row) + " |")
        return "\n".join(lines)


# ============================================================
# Numbered Canvas for PDF Reports
# ============================================================

class NumberedCanvas(canvas.Canvas):
    """Canvas that adds running headers and page numbers on all pages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setStrokeColor(colors.HexColor("#d0d7de"))
        self.setLineWidth(0.5)

        # Header (pages 2+)
        if self._pageNumber > 1:
            self.line(40, 11 * inch - 36, 8.5 * inch - 40, 11 * inch - 36)
            self.setFillColor(colors.HexColor("#57606a"))
            self.drawString(40, 11 * inch - 30, "Industrial Anomaly Detection — Experimental Research Report")
            self.drawRightString(8.5 * inch - 40, 11 * inch - 30, "Confidential Academic Document")

        # Footer (all pages)
        self.line(40, 36, 8.5 * inch - 40, 36)
        self.setFillColor(colors.HexColor("#57606a"))
        self.drawString(40, 24, "MVTec AD Benchmark | DIP, Deep Learning & Optimization Study")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 24, page_text)
        self.restoreState()


# ============================================================
# PDF Document Generator Helper
# ============================================================

class PDFReportGenerator:
    """Builds clean, academic multi-page PDF documents."""

    def __init__(self, filename: str, title: str, subtitle: str = ""):
        self.filename = filename
        self.title = title
        self.subtitle = subtitle
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=46,
            bottomMargin=46
        )
        self.story = []
        self._init_styles()

    def _init_styles(self):
        self.styles = getSampleStyleSheet()

        self.style_title = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f2b48"),
            spaceAfter=6,
        )
        self.style_subtitle = ParagraphStyle(
            "DocSubtitle",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#57606a"),
            spaceAfter=14,
        )
        self.style_h1 = ParagraphStyle(
            "Header1",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1b4965"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        )
        self.style_h2 = ParagraphStyle(
            "Header2",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#2b5c8f"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        )
        self.style_body = ParagraphStyle(
            "Body",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#24292f"),
            spaceAfter=6,
        )
        self.style_callout = ParagraphStyle(
            "Callout",
            parent=self.styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0969da"),
            spaceBefore=4,
            spaceAfter=6,
        )
        self.style_table_header = ParagraphStyle(
            "TableHeader",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=colors.white,
            alignment=1,
        )
        self.style_table_cell = ParagraphStyle(
            "TableCell",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#24292f"),
            alignment=1,
        )

    def add_title(self):
        self.story.append(Paragraph(self.title, self.style_title))
        if self.subtitle:
            self.story.append(Paragraph(self.subtitle, self.style_subtitle))
        self.story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1b4965"), spaceAfter=14))

    def add_heading(self, text: str, level: int = 1):
        style = self.style_h1 if level == 1 else self.style_h2
        self.story.append(Paragraph(text, style))

    def add_paragraph(self, text: str):
        self.story.append(Paragraph(text, self.style_body))

    def add_callout(self, text: str):
        box_data = [[Paragraph(f"<b>Key Takeaway:</b> {text}", self.style_callout)]]
        box_table = Table(box_data, colWidths=[532])
        box_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ddf4ff")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#54aeff")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        self.story.append(box_table)
        self.story.append(Spacer(1, 6))

    def add_table(self, df: pd.DataFrame, col_widths: list = None):
        """Render a styled PDF table from a pandas DataFrame."""
        if df.empty:
            self.add_paragraph("<i>No data available.</i>")
            return

        headers = [Paragraph(str(col), self.style_table_header) for col in df.columns]
        rows = []
        for _, r in df.iterrows():
            formatted_row = []
            for val in r:
                if pd.isna(val):
                    formatted_row.append(Paragraph("—", self.style_table_cell))
                elif isinstance(val, (float, np.floating)):
                    formatted_row.append(Paragraph(f"{val:.4f}", self.style_table_cell))
                else:
                    formatted_row.append(Paragraph(str(val), self.style_table_cell))
            rows.append(formatted_row)

        table_data = [headers] + rows
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b4965")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        self.story.append(t)
        self.story.append(Spacer(1, 10))

    def add_image(self, img_path: str, width: float = 500, height: float = 280):
        if os.path.exists(img_path):
            self.story.append(KeepTogether([
                Image(img_path, width=width, height=height),
                Spacer(1, 8)
            ]))
        else:
            logger.warning("Image path does not exist: %s", img_path)

    def add_page_break(self):
        self.story.append(PageBreak())

    def build(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.doc.build(self.story, canvasmaker=NumberedCanvas)
        logger.info("PDF generated successfully: %s", self.filename)
