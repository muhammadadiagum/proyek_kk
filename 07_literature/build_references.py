"""Bangkitkan daftar referensi (Markdown + BibTeX) dari metadata terverifikasi.

Sumber angka dan metadata: 07_literature/refs_verified.json, yang diisi dari
Crossref (judul, penulis, tahun, venue, volume, halaman, DOI) dan OpenAlex
(abstrak, jumlah sitasi). Tidak ada entri yang ditulis manual di sini.

Pemakaian: python build_references.py
Keluaran: 07_literature/references.md, 07_literature/references.bib
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def clean(text: str) -> str:
    text = text.replace("&amp;", "&").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def apa(rec: dict) -> str:
    authors = rec.get("authors") or []
    if not authors:
        a = "Anon."
    elif len(authors) == 1:
        a = authors[0]
    elif len(authors) <= 5:
        a = ", ".join(authors[:-1]) + " & " + authors[-1]
    else:
        a = authors[0] + " et al."
    year = rec.get("year") or "n.d."
    title = clean(rec.get("title", "")).rstrip(".")
    venue = clean(rec.get("venue", ""))
    bits = [f"{a} ({year}). {title}."]
    if venue:
        loc = venue
        if rec.get("volume"):
            loc += f", {rec['volume']}"
            if rec.get("issue"):
                loc += f"({rec['issue']})"
        if rec.get("page") and rec["page"] not in ("None", "-"):
            loc += f", {rec['page']}"
        bits.append(loc + ".")
    bits.append(f"https://doi.org/{rec['doi']}")
    return " ".join(bits)


def bibkey(rec: dict) -> str:
    first = (rec.get("authors") or ["anon"])[0].split(",")[0]
    first = re.sub(r"[^A-Za-z]", "", first).lower()
    year = rec.get("year") or "nd"
    word = re.sub(r"[^A-Za-z]", "", clean(rec.get("title", "x")).split(" ")[1] if len(clean(rec.get("title", "x")).split(" ")) > 1 else "x").lower()
    return f"{first}{year}{word}"


def bibentry(rec: dict) -> str:
    kind = "article" if rec.get("type") == "journal-article" else "inproceedings"
    fields = {
        "title": clean(rec.get("title", "")),
        "author": " and ".join(rec.get("authors") or []),
        "year": rec.get("year"),
        "journal" if kind == "article" else "booktitle": clean(rec.get("venue", "")),
        "volume": rec.get("volume"),
        "number": rec.get("issue"),
        "pages": rec.get("page"),
        "doi": rec.get("doi"),
    }
    body = ",\n  ".join(f"{k} = {{{v}}}" for k, v in fields.items() if v and str(v) != "None")
    return f"@{kind}{{{bibkey(rec)},\n  {body}\n}}\n"


def main() -> int:
    recs = json.loads((ROOT / "refs_verified.json").read_text())
    recs.sort(key=lambda r: (r.get("year") or 9999, (r.get("authors") or ["zz"])[0]))
    lines = ["# References", "",
             f"Jumlah entri: **{len(recs)}** "
             f"(2022–2026: **{sum(1 for r in recs if (r.get('year') or 0) >= 2022)}**). "
             "Metadata diverifikasi via Crossref; abstrak via OpenAlex/Semantic Scholar.", ""]
    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {apa(rec)}")
    (ROOT / "references.md").write_text("\n".join(lines) + "\n")
    (ROOT / "references.bib").write_text("\n".join(bibentry(r) for r in recs))
    print(f"references.md: {len(recs)} entri; references.bib ditulis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
