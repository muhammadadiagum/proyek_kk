"""Ekspor rekaman mentah JSONL ke CSV/XLSX untuk paket submit.

Menyalin isi 03_experiments/raw/*.jsonl ke 06_package/raw_results/ dalam bentuk
tabel (satu baris per run) supaya pemeriksa dapat membuka hasil tanpa Python.
Kolom `cfg` dan `trace` dipertahankan sebagai JSON string.

Pemakaian: python export_raw.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "03_experiments/raw"
OUT = ROOT / "06_package/raw_results"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {}
    for suite in ("pilot", "main", "ablation"):
        path = RAW / f"{suite}.jsonl"
        if not path.exists():
            print(f"lewati {suite}: tidak ada")
            continue
        rows = [json.loads(l) for l in path.open()]
        df = pd.DataFrame(rows)
        for col in ("cfg", "trace"):
            if col in df.columns:
                df[col] = df[col].map(lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v)
        df = df.drop(columns=[c for c in ("pid",) if c in df.columns])
        out = OUT / f"{suite}_runs.csv"
        df.to_csv(out, index=False)
        frames[suite] = df
        print(f"{out.relative_to(ROOT)}: {len(df)} run, {len(df.columns)} kolom")

    if frames:
        xlsx = OUT / "all_runs.xlsx"
        with pd.ExcelWriter(xlsx, engine="openpyxl") as xw:
            for name, df in frames.items():
                df.to_excel(xw, sheet_name=name[:31], index=False)
        print(f"{xlsx.relative_to(ROOT)}: {len(frames)} sheet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
