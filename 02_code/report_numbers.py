"""Lembar angka (numbers sheet) untuk naskah.

Membaca tabel hasil analisis dan mencetak tabel Markdown siap pakai, sehingga
setiap angka di naskah dapat ditelusuri ke 04_results/tables (yang berasal dari
03_experiments/raw). Tidak ada perhitungan baru di luar agregasi sederhana.

Pemakaian: python report_numbers.py [--label main]
Keluaran : 05_manuscript/numbers.md (juga dicetak ke stdout)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LBL = {"greedy": "Greedy", "ga_std": "GA", "ga_repair": "GA-R"}


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{x:.{nd}f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    args = ap.parse_args()
    tdir = ROOT / "04_results/tables"
    pi = pd.read_csv(tdir / f"{args.label}_descriptive.csv")
    st = pd.read_csv(tdir / f"{args.label}_stats.csv")
    cost = pd.read_csv(tdir / f"{args.label}_cost.csv")
    out = [f"# Numbers sheet — {args.label}", "",
           f"Sumber: `04_results/tables/{args.label}_*.csv` "
           f"(dari `03_experiments/raw/{args.label}.jsonl`).", ""]

    out += ["## 1. Karakteristik instance", "",
            "| Instance | Sessions | Rooms | Slots | Room fill | Pattern |",
            "|---|---|---|---|---|---|"]
    base = pi.drop_duplicates("instance").sort_values(["family", "instance"])
    for _, r in base.iterrows():
        out.append(f"| {r['instance']} | {int(r['n'])} | {int(r['n_rooms'])} | "
                   f"{int(r['n_slots'])} | {r['fill']:.3f} | {r['pattern']} |")

    out += ["", "## 2. Kinerja per metode (21 instance test)", "",
            "| Method | Feasible instances | Median H | Mean H | Median P | Median gens | Median runtime (s) | Repair share |",
            "|---|---|---|---|---|---|---|---|"]
    for _, r in cost.iterrows():
        sub = pi[pi["method"] == r["method"]]
        fe = int((sub["feasible_rate"] >= 0.5).sum())
        out.append(f"| {LBL.get(r['method'], r['method'])} | {fe}/{sub['instance'].nunique()} | "
                   f"{fmt(sub['median_H'].median())} | {fmt(sub['mean_H'].mean())} | "
                   f"{fmt(sub['median_P'].median())} | {fmt(sub['median_generations'].median())} | "
                   f"{fmt(sub['median_runtime_s'].median())} | {fmt(sub['median_repair_share'].median(), 3)} |")

    out += ["", "## 3. Median hard violations per pola ketersediaan", "",
            "| Pattern | Greedy | GA | GA-R |", "|---|---|---|---|"]
    for pat in ["A", "B", "C", "benchmark"]:
        cells = []
        for m in ("greedy", "ga_std", "ga_repair"):
            s = pi[(pi["method"] == m) & (pi["pattern"] == pat)]
            cells.append(fmt(s["median_H"].median()) if len(s) else "–")
        out.append(f"| {pat} | " + " | ".join(cells) + " |")

    out += ["", "## 4. Median penalti preferensi (P) per pola", "",
            "| Pattern | Greedy | GA | GA-R |", "|---|---|---|---|"]
    for pat in ["A", "B", "C", "benchmark"]:
        cells = []
        for m in ("greedy", "ga_std", "ga_repair"):
            s = pi[(pi["method"] == m) & (pi["pattern"] == pat)]
            cells.append(fmt(s["median_P"].median()) if len(s) else "–")
        out.append(f"| {pat} | " + " | ".join(cells) + " |")

    out += ["", "## 5. Uji statistik", "",
            "| Test | Metric | Comparison | n | statistic | p | p (Holm) | Cliff's delta | Effect |",
            "|---|---|---|---|---|---|---|---|---|"]
    for _, r in st.iterrows():
        out.append(f"| {r['test']} | {r['metric']} | {r['comparison']} | {fmt(r['n_units'])} | "
                   f"{fmt(r['statistic'], 3)} | {fmt(r['p_value'], 4)} | {fmt(r['p_holm'], 4)} | "
                   f"{fmt(r['cliffs_delta'], 3)} | {r['effect']} |")

    out += ["", "## 6. Rincian per instance", "",
            "| Instance | Pattern | n | GA med H | GA feasible | GA-R med H | GA-R feasible | GA med P | GA-R med P | GA gens | GA-R gens | GA-R repair share |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    idx = pi.set_index(["instance", "method"])
    for inst in base["instance"]:
        a = idx.loc[(inst, "ga_std")]
        b = idx.loc[(inst, "ga_repair")]
        out.append(f"| {inst} | {a['pattern']} | {int(a['n'])} | {fmt(a['median_H'])} | "
                   f"{a['feasible_rate']:.2f} | {fmt(b['median_H'])} | {b['feasible_rate']:.2f} | "
                   f"{fmt(a['median_P'])} | {fmt(b['median_P'])} | {fmt(a['median_generations'])} | "
                   f"{fmt(b['median_generations'])} | {fmt(b['median_repair_share'], 3)} |")

    abl_path = tdir / "ablation_descriptive.csv"
    if abl_path.exists():
        abl = pd.read_csv(abl_path)
        out += ["", "## 7. Ablation", "",
                "| Variant | Feasible instances | Median H | Median P | Median gens | Repair share |",
                "|---|---|---|---|---|---|"]
        if "variant" in abl.columns and abl["variant"].notna().any():
            for tag, g in abl.groupby("variant"):
                out.append(f"| {tag} | {int((g['feasible_rate'] >= 0.5).sum())}/{g['instance'].nunique()} | "
                           f"{fmt(g['median_H'].median())} | {fmt(g['median_P'].median())} | "
                           f"{fmt(g['median_generations'].median())} | {fmt(g['median_repair_share'].median(), 3)} |")

    text = "\n".join(out) + "\n"
    (ROOT / "05_manuscript").mkdir(parents=True, exist_ok=True)
    (ROOT / f"05_manuscript/numbers_{args.label}.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
