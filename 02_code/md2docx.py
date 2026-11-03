"""Konversi naskah Markdown (subset) ke DOCX, lalu ekspor PDF via Word.

Pemakaian:
    python md2docx.py 05_manuscript/manuscript.md 05_manuscript/manuscript.docx
    python md2docx.py ... --pdf        # ekspor PDF memakai Word di host Windows

Subset Markdown yang didukung: heading (#..####), paragraf, daftar berbutir
("- "), daftar bernomor ("1. "), tabel pipa, gambar ("![alt](path)"), tebal
("**"), miring ("*"), kode inline ("`"), dan penanda halaman
("<!-- pagebreak -->"). Cukup untuk naskah artikel dan tidak memerlukan
pustaka konversi eksternal.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]


def add_runs(par, text: str) -> None:
    """Tangani **tebal**, *miring*, `kode` di dalam satu paragraf."""
    tokens = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            run = par.add_run(tok[2:-2]); run.bold = True
        elif tok.startswith("`") and tok.endswith("`"):
            run = par.add_run(tok[1:-1]); run.font.name = "Consolas"; run.font.size = Pt(9)
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            run = par.add_run(tok[1:-1]); run.italic = True
        else:
            par.add_run(tok)


def style_document(doc: Document) -> None:
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(2.2)
    sec.left_margin = sec.right_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    for lvl, size in ((1, 15), (2, 12.5), (3, 11)):
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.font.bold = True
        st.paragraph_format.space_before = Pt(10 if lvl == 1 else 8)
        st.paragraph_format.space_after = Pt(4)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, cell in enumerate(header):
        par = table.rows[0].cells[i].paragraphs[0]
        run = par.add_run(cell.strip())
        run.bold = True
        run.font.size = Pt(8.5)
    for row in body:
        cells = table.add_row().cells
        for i, cell in enumerate(row[: len(header)]):
            par = cells[i].paragraphs[0]
            run = par.add_run(cell.strip())
            run.font.size = Pt(8.5)
    doc.add_paragraph()


def render(md: str, out: Path, base: Path) -> Document:
    doc = Document()
    style_document(doc)
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.strip() == "<!-- pagebreak -->":
            doc.add_page_break(); i += 1; continue
        if not line.strip():
            i += 1; continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            if level == 1:
                par = doc.add_paragraph()
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = par.add_run(text)
                run.bold = True
                run.font.size = Pt(16)
                run.font.name = "Times New Roman"
            else:
                doc.add_heading(text, level=min(level, 3))
            i += 1; continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = [c for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[\s:\-|]+", lines[i]):
                    rows.append(raw)
                i += 1
            if rows:
                add_table(doc, rows)
            continue
        if line.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", line)
            if m:
                alt, rel = m.group(1), m.group(2)
                path = (base / rel).resolve()
                if path.exists():
                    doc.add_picture(str(path), width=Cm(15.5))
                    cap = doc.add_paragraph()
                    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = cap.add_run(alt)
                    run.italic = True
                    run.font.size = Pt(8.5)
            i += 1; continue
        if line.startswith("- "):
            par = doc.add_paragraph(style="List Bullet")
            add_runs(par, line[2:])
            i += 1; continue
        if re.match(r"^\d+\.\s", line):
            par = doc.add_paragraph(style="List Number")
            add_runs(par, re.sub(r"^\d+\.\s", "", line))
            i += 1; continue
        par = doc.add_paragraph()
        # teks utama rata kiri-kanan; satu paragraf = satu blok di Markdown
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_runs(par, line)
        i += 1
    doc.save(out)
    return doc


def to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Ekspor PDF memakai Microsoft Word di host Windows (WSL)."""
    win_docx = subprocess.run(["wslpath", "-w", str(docx_path)], capture_output=True,
                              text=True).stdout.strip()
    win_pdf = subprocess.run(["wslpath", "-w", str(pdf_path)], capture_output=True,
                             text=True).stdout.strip()
    ps = (
        "$ErrorActionPreference='Stop';"
        "$w=New-Object -ComObject Word.Application; $w.Visible=$false;"
        f"$d=$w.Documents.Open('{win_docx}');"
        f"$d.SaveAs([ref]'{win_pdf}',[ref]17); $d.Close(); $w.Quit()"
    )
    res = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True)
    if res.returncode != 0:
        print("PDF export gagal:", res.stderr[:400])
        return False
    return pdf_path.exists()


def main() -> int:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    render(src.read_text(), out, src.parent)
    print(f"DOCX: {out} ({out.stat().st_size} bytes)")
    if "--pdf" in sys.argv:
        pdf = out.with_suffix(".pdf")
        if to_pdf(out.resolve(), pdf.resolve()):
            print(f"PDF : {pdf} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
