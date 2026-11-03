"""Pemilihan konfigurasi dari hasil pilot, mengikuti aturan yang sudah dikunci
di 00_config/design_lock.md bagian 9:

    pilih kombinasi dengan (i) proporsi run feasible tertinggi,
    (ii) median best_H terendah, (iii) median best_P terendah,
    (iv) porsi anggaran repair terendah (bila masih seri).

Sweep pm untuk GA standar dipilih terpisah dengan aturan yang sama (tanpa
kriteria iv), agar baseline memperoleh penyetelan yang adil.

Keluaran: 00_config/config_final.json + tabel ringkas
04_results/tables/pilot_selection.csv

Pemakaian: python pilot_select.py [03_experiments/raw/pilot.jsonl]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> pd.DataFrame:
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df = df[df["status"] == "ok"]
    return df


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("tag").apply(
        lambda g: pd.Series({
            "runs": len(g),
            "feasible_frac": float((g["best_H"] == 0).mean()),
            "median_H": float(g["best_H"].median()),
            "mean_H": round(float(g["best_H"].mean()), 3),
            "median_P": float(g["best_P"].median()),
            "median_runtime_s": round(float(g["runtime_s"].median()), 2),
            "median_repair_share": None if g["repair_share"].isna().all()
            else round(float(g["repair_share"].dropna().median()), 4),
            "median_generations": None if g["generations"].isna().all()
            else int(g["generations"].dropna().median()),
        }), include_groups=False)
    return agg.reset_index().sort_values(
        ["feasible_frac", "median_H", "median_P"], ascending=[False, True, True])


def parse_tag(tag: str) -> dict:
    """tag ga_repair: pm{pm}_k{k}_a{att}_s{sw}"""
    out = {}
    for part in tag.split("_"):
        if part.startswith("pm"):
            v = part[2:].replace("p", ".")
            out["pm"] = "1/n" if v == "1/n" else float(v)
        elif part.startswith("k"):
            out["repair_max_sessions"] = int(part[1:])
        elif part.startswith("a"):
            out["repair_attempts"] = int(part[1:])
        elif part.startswith("s"):
            out["swap_attempts"] = int(part[1:])
    return out


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "03_experiments/raw/pilot.jsonl"
    df = load(path)
    summary = summarise(df)
    tables = ROOT / "04_results/tables"
    tables.mkdir(parents=True, exist_ok=True)
    summary.to_csv(tables / "pilot_selection.csv", index=False)

    rep = summary[summary["tag"].str.startswith("pm")]
    std = summary[summary["tag"].str.startswith("std_")]
    best_rep = rep.iloc[0]
    best_std = std.iloc[0]
    cfg = parse_tag(best_rep["tag"])
    # pm untuk GA standar: nilai pm dari tag std_pm<x>
    pm_tag = best_std["tag"].replace("std_pm", "").replace("p", ".")
    cfg["pm_std"] = "1/n" if pm_tag == "1/n" else float(pm_tag)
    cfg.setdefault("pm", "1/n")
    cfg.update({"budget": 10000, "pop_size": 50, "pc": 0.8, "elitism": 2,
                "seed_mode": "greedy", "selected_from": str(path.relative_to(ROOT)),
                "rule": "max feasible_frac, min median_H, min median_P, min repair_share"},
               )
    (ROOT / "00_config/config_final.json").write_text(json.dumps(cfg, indent=1))
    print("== ringkasan pilot (urut aturan pemilihan) ==")
    with pd.option_context("display.width", 200, "display.max_rows", 60):
        print(summary.to_string(index=False))
    print("\nterpilih (ga_repair):", best_rep["tag"], dict(best_rep))
    print("terpilih (ga_std)   :", best_std["tag"], dict(best_std))
    print("\nconfig_final.json:", json.dumps(cfg, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
