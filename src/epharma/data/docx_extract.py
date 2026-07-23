"""Extract tabular data from the bundled DOCX source file."""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

DEFAULT_TABLE_NAMES = [
    "patient_registration",
    "prescription_quality",
    "daily_sales",
    "doctor_performance",
    "inventory_status",
    "monthly_demand",
    "medicine_recommendations",
    "pharmacy_performance",
    "patient_risk",
    "api_predictions",
    "model_metrics",
    "api_status",
    "kpis",
]


def _cell_text(cell: ET.Element) -> str:
    paragraphs: list[str] = []
    for paragraph in cell.findall(".//w:p", WORD_NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NS))
        if text:
            paragraphs.append(text)
    return " ".join(paragraphs).strip()


def extract_tables(docx_path: str | Path) -> list[list[list[str]]]:
    """Return each DOCX table as rows of cell strings."""
    with zipfile.ZipFile(docx_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    tables: list[list[list[str]]] = []
    for table in root.findall(".//w:tbl", WORD_NS):
        rows: list[list[str]] = []
        for row in table.findall("./w:tr", WORD_NS):
            rows.append([_cell_text(cell) for cell in row.findall("./w:tc", WORD_NS)])
        tables.append(rows)
    return tables


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "table"


def _table_name(index: int, rows: list[list[str]]) -> str:
    if index < len(DEFAULT_TABLE_NAMES):
        return DEFAULT_TABLE_NAMES[index]
    header = "_".join(rows[0][:3]) if rows else f"table_{index + 1}"
    return _slug(header)


def write_tables(tables: list[list[list[str]]], output_dir: str | Path) -> list[Path]:
    """Write extracted tables as CSV files and return their paths."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for index, rows in enumerate(tables):
        path = target / f"{index + 1:02d}_{_table_name(index, rows)}.csv"
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract tables from a DOCX file to CSV.")
    parser.add_argument("--input", default="data.docx", help="Path to the DOCX file.")
    parser.add_argument("--output-dir", default="data/raw/docx", help="Directory for extracted CSVs.")
    args = parser.parse_args()

    tables = extract_tables(args.input)
    written = write_tables(tables, args.output_dir)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
