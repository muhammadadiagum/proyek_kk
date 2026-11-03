"""Membandingkan setiap varian ablation dengan konfigurasi terkunci pada suite utama.

Unit analisis = instance (median 20 seed per instance). Pembanding = baris
`ga_repair` pada 03_experiments/raw/main.jsonl (konfigurasi terkunci).
Uji: Wilcoxon berpasangan + Cliff's delta, Holm atas seluruh varian.

Pemakaian: python ablation_compare.py
Keluaran : 04_results/tables/ablation_compare.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "03_experiments/raw"


def per_instance(path: Path, method: str | None = None) -> pd.DataFrame:
    rows = [json.loads(l) for l in path.open()]
    df = pd.DataFrame(rows)
    if method:
        df = df[df["method"] == method]
    g = (df.groupby(["tag", "instance_name"])
           .agg(median_H=("best_H", "median"),
                median_P=("best_P", "median"),
                feasible_rate=("feasible", "mean"),
                generations=("generations", "median"),
                repair_share=("repair_share", "median"))
           .reset_index())
    return g


def cliffs(x: np.ndarray, y: np.ndarray) -> float:
    gt = sum((xi > yi) for xi in x for yi in y)
    lt = sum((xi < yi) for xi in x for yi in y)
    n = len(x) * len(y)
    return (gt - lt) / n if n else np.nan


def holm(p: list[float]) -> list[float]:
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    prev = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * p[idx])
        prev = max(prev, val)
        adj[idx] = prev
    return adj.tolist()


def main() -> int:
    base = per_instance(RAW / "main.jsonl", "ga_repair").set_index("instance_name")
    abl = per_instance(RAW / "ablation.jsonl")
    out = []
    for tag, g in abl.groupby("tag"):
        g = g.set_index("instance_name").reindex(base.index)
        for metric in ("median_H", "median_P"):
            a = base[metric].to_numpy(float)
            b = g[metric].to_numpy(float)
            diff = b - a
            if np.allclose(diff, 0):
                stat, p = np.nan, 1.0
            else:
                stat, p = wilcoxon(b, a, zero_method="wilcox")
            out.append({"variant": tag, "metric": metric, "n": int(len(a)),
                        "median_variant": float(np.nanmedian(b)),
                        "median_locked": float(np.nanmedian(a)),
                        "wins": int((diff < 0).sum()), "losses": int((diff > 0).sum()),
                        "ties": int((diff == 0).sum()),
                        "statistic": float(stat) if stat == stat else np.nan,
                        "p_value": float(p), "cliffs_delta": cliffs(b, a),
                        "feasible_share_variant": float(g["feasible_rate"].mean()),
                        "feasible_share_locked": float(base["feasible_rate"].mean()),
                        "repair_share_variant": float(g["repair_share"].median()),
                        "generations_variant": float(g["generations"].median())})
    df = pd.DataFrame(out)
    for metric, idx in df.groupby("metric").groups.items():
        df.loc[idx, "p_holm"] = holm(df.loc[idx, "p_value"].tolist())
    out_path = ROOT / "04_results/tables/ablation_compare.csv"
    df.to_csv(out_path, index=False)
    pd.set_option("display.width", 200)
    print(df.round(4).to_string(index=False))
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
