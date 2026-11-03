"""Analisis hasil eksperimen: tabel, statistik, dan gambar.

Semua angka berasal dari berkas mentah 03_experiments/raw/<suite>.jsonl.
Tidak ada angka yang ditulis manual di skrip ini.

Pemakaian:
    python analyze.py --raw 03_experiments/raw/main.jsonl --label main
    python analyze.py --raw 03_experiments/raw/ablation.jsonl --label ablation

Keluaran:
    04_results/tables/<label>_descriptive.csv
    04_results/tables/<label>_by_family.csv
    04_results/tables/<label>_stats.csv
    04_results/tables/<label>_cost.csv
    04_results/tables/<label>_tables.xlsx
    04_results/figures/<label>_*.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import friedmanchisquare, wilcoxon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
METHOD_LABEL = {"greedy": "Greedy", "ga_std": "GA (standard)",
                "ga_repair": "GA + repair"}
COLORS = {"greedy": "#4d4d4d", "ga_std": "#1f77b4", "ga_repair": "#d62728"}

# Label gambar: versi Inggris (default) dan Indonesia (naskah terjemahan).
TXT = {
    "en": {
        "pat_title": "availability pattern {pat}",
        "bench_title": "public benchmark",
        "x_evals": "objective evaluations used",
        "y_mean_h": "mean best hard violations (%)",
        "y_h_med": "hard violations of best solution (median over seeds)",
        "title_quality": "Solution quality across 21 test instances",
        "xt_loose": "loose (A)", "xt_medium": "medium (B)",
        "xt_tight": "tight (C)", "xt_bench": "benchmark",
        "y_feas_share": "share of instances solved to feasibility",
        "x_gens": "generations completed at equal budget",
        "x_wall": "wall-clock seconds per run",
        "y_h": "hard violations (median)",
        "x_sessions": "number of sessions",
    },
    "id": {
        "pat_title": "pola ketersediaan {pat}",
        "bench_title": "benchmark publik",
        "x_evals": "evaluasi objektif terpakai",
        "y_mean_h": "rata-rata pelanggaran hard terbaik (%)",
        "y_h_med": "pelanggaran hard solusi terbaik (median atas seed)",
        "title_quality": "Kualitas solusi pada 21 instance uji",
        "xt_loose": "longgar (A)", "xt_medium": "sedang (B)",
        "xt_tight": "ketat (C)", "xt_bench": "benchmark",
        "y_feas_share": "porsi instance yang mencapai kelayakan",
        "x_gens": "generasi selesai pada anggaran sama",
        "x_wall": "detik waktu dinding per run",
        "y_h": "pelanggaran hard (median)",
        "x_sessions": "jumlah sesi",
    },
}
LANG = "en"


def t(key: str, **kw) -> str:
    s = TXT[LANG][key]
    return s.format(**kw) if kw else s


# --------------------------------------------------------------------------
def load_raw(path: Path) -> pd.DataFrame:
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    ok = df[df["status"] == "ok"].copy()
    bad = df[df["status"] != "ok"]
    if len(bad):
        print(f"PERINGATAN: {len(bad)} run tidak ok (dilaporkan sebagai gagal):")
        print(bad.groupby(["method", "status"]).size().to_string())
    return ok, bad


def pattern_of(name: str) -> str:
    for p in ("A", "B", "C"):
        if name.endswith(p) and name.startswith("syn"):
            return p
    return "benchmark"


def size_of(name: str) -> str:
    if name.startswith("syn"):
        return name[3:5]
    return "benchmark"


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> tuple[float, str]:
    """Cliff's delta berpasangan (a vs b). delta > 0 berarti a lebih besar."""
    diff = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    pos, neg = int((diff > 0).sum()), int((diff < 0).sum())
    n = pos + neg
    if n == 0:
        return 0.0, "negligible"
    d = (pos - neg) / n
    mag = abs(d)
    tag = ("negligible" if mag < 0.147 else "small" if mag < 0.33
           else "medium" if mag < 0.474 else "large")
    return d, tag


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * pvals[idx]
        running = max(running, val)
        adj[idx] = min(1.0, running)
    return list(adj)


# --------------------------------------------------------------------------
def per_instance(df: pd.DataFrame) -> pd.DataFrame:
    """Agregasi seed → satu baris per (instance, method)."""
    rows = []
    for (inst, method, tag), g in df.groupby(["instance_name", "method", "tag"]):
        rows.append({
            "instance": inst,
            "method": method,
            "variant": tag,
            "family": g["family"].iloc[0],
            "n": int(g["n"].iloc[0]),
            "n_slots": int(g["n_slots"].iloc[0]),
            "n_rooms": int(g["n_rooms"].iloc[0]),
            "fill": float(g["fill"].iloc[0]),
            "pattern": pattern_of(inst),
            "size": size_of(inst),
            "runs": len(g),
            "feasible_rate": float((g["best_H"] == 0).mean()),
            "median_H": float(g["best_H"].median()),
            "mean_H": float(g["best_H"].mean()),
            "std_H": float(g["best_H"].std(ddof=0)),
            "min_H": int(g["best_H"].min()),
            "median_P": float(g["best_P"].median()),
            "mean_P": float(g["best_P"].mean()),
            "median_runtime_s": float(g["runtime_s"].median()),
            "median_generations": float(g["generations"].median()) if g["generations"].notna().any() else np.nan,
            "median_repair_share": float(g["repair_share"].dropna().median()) if g["repair_share"].notna().any() else np.nan,
            "median_evals_to_first": float(g["evals_to_first_feasible"].dropna().median()) if g["evals_to_first_feasible"].notna().any() else np.nan,
            "frac_reached_feasible": float(g["evals_to_first_feasible"].notna().mean()),
        })
    return pd.DataFrame(rows)


def stats_tables(pi: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Uji berpasangan per instance: GA standar vs GA+repair (dan 3-metode).

    Untuk suite ablation, satu instance muncul pada beberapa varian, sehingga unit
    analisis menjadi (instance, varian); untuk suite utama unitnya instance saja.
    """
    if pi["variant"].nunique() > 1:
        pi = pi.copy()
        pi["instance"] = pi["instance"] + "|" + pi["variant"].astype(str)
    wide = pi.pivot(index="instance", columns="method", values="median_H")
    wide_p = pi.pivot(index="instance", columns="method", values="median_P")
    rows = []
    methods = [m for m in ("greedy", "ga_std", "ga_repair") if m in wide.columns]
    if {"ga_std", "ga_repair"} <= set(methods):
        for metric, w in (("H", wide), ("P", wide_p)):
            a, b = w["ga_std"].to_numpy(), w["ga_repair"].to_numpy()
            stat, p = wilcoxon(a, b, zero_method="wilcox")
            d, mag = cliffs_delta(b, a)  # positif = repair lebih besar (buruk utk H)
            rows.append({"test": "wilcoxon_paired", "metric": metric,
                         "comparison": "ga_repair_vs_ga_std", "n_units": len(a),
                         "statistic": float(stat), "p_value": float(p),
                         "p_holm": float(p), "cliffs_delta": float(d),
                         "effect": mag,
                         "median_std": float(np.median(a)), "median_repair": float(np.median(b))})
    if len(methods) >= 3:
        for metric, w in (("H", wide), ("P", wide_p)):
            arrays = [w[m].to_numpy() for m in methods]
            stat, p = friedmanchisquare(*arrays)
            rows.append({"test": "friedman", "metric": metric,
                         "comparison": "+".join(methods), "n_units": len(arrays[0]),
                         "statistic": float(stat), "p_value": float(p),
                         "p_holm": float(p), "cliffs_delta": np.nan, "effect": "",
                         "median_std": np.nan, "median_repair": np.nan})
        # post-hoc berpasangan + Holm
        pairs = [(methods[i], methods[j]) for i in range(len(methods))
                 for j in range(i + 1, len(methods))]
        raw_p = []
        for a, b in pairs:
            stat, p = wilcoxon(wide[a].to_numpy(), wide[b].to_numpy(), zero_method="wilcox")
            raw_p.append(float(p))
        adj = holm(raw_p)
        for (a, b), p, pa in zip(pairs, raw_p, adj):
            d, mag = cliffs_delta(wide[b].to_numpy(), wide[a].to_numpy())
            rows.append({"test": "posthoc_wilcoxon_holm", "metric": "H",
                         "comparison": f"{b}_vs_{a}", "n_units": len(wide),
                         "statistic": np.nan, "p_value": p, "p_holm": pa,
                         "cliffs_delta": float(d), "effect": mag,
                         "median_std": float(wide[a].median()),
                         "median_repair": float(wide[b].median())})
    # McNemar atas feasible (mayoritas seed)
    feas = pi.assign(f=(pi["feasible_rate"] >= 0.5)).pivot(index="instance", columns="method", values="f")
    if {"ga_std", "ga_repair"} <= set(feas.columns):
        b = int((feas["ga_repair"] & ~feas["ga_std"]).sum())
        c = int((~feas["ga_repair"] & feas["ga_std"]).sum())
        if b + c > 0:
            from scipy.stats import binomtest
            p = float(binomtest(b, b + c, 0.5).pvalue)
            rows.append({"test": "mcnemar_exact", "metric": "feasible",
                         "comparison": "ga_repair_vs_ga_std", "n_units": int(b + c),
                         "statistic": float(b), "p_value": p, "p_holm": p,
                         "cliffs_delta": np.nan, "effect": "",
                         "median_std": float(feas["ga_std"].mean()),
                         "median_repair": float(feas["ga_repair"].mean())})
    return pd.DataFrame(rows), pi


def cost_table(pi: pd.DataFrame) -> pd.DataFrame:
    g = pi.groupby("method").agg(
        instances=("instance", "count"),
        median_runtime_s=("median_runtime_s", "median"),
        median_generations=("median_generations", "median"),
        median_repair_share=("median_repair_share", "median"),
        feasible_rate=("feasible_rate", "mean"),
        median_H=("median_H", "median"),
        median_P=("median_P", "median"),
    ).reset_index()
    return g.sort_values("median_H")


# --------------------------------------------------------------------------
def fig_convergence(df: pd.DataFrame, out: Path) -> None:
    """Rata-rata best_H terhadap evaluasi terpakai, per pola ketersediaan."""
    patterns = [p for p in ("A", "B", "C", "benchmark")]
    fig, axes = plt.subplots(1, len(patterns), figsize=(4.0 * len(patterns), 3.2),
                             sharey=False)
    for ax, pat in zip(np.atleast_1d(axes), patterns):
        sub = df[df["instance_name"].map(pattern_of) == pat]
        for method in ("ga_std", "ga_repair"):
            s = sub[sub["method"] == method]
            if s.empty:
                continue
            max_ev = 10000
            grid = np.linspace(0, max_ev, 201)
            curves = []
            for _, g in s.groupby("seed"):
                tr = [t for t in g["trace"].iloc[0]] if len(g) else []
                if not tr:
                    continue
                xs = [0] + [t[0] for t in tr]
                ys = [tr[0][1]] + [t[1] for t in tr]
                curves.append(np.interp(grid, xs, ys))
            if not curves:
                continue
            arr = np.vstack(curves)
            ax.plot(grid, arr.mean(axis=0), label=METHOD_LABEL[method],
                    color=COLORS[method], lw=1.6)
            ax.fill_between(grid, arr.mean(axis=0) - arr.std(axis=0) / np.sqrt(len(arr)),
                            arr.mean(axis=0) + arr.std(axis=0) / np.sqrt(len(arr)),
                            color=COLORS[method], alpha=0.15, lw=0)
        ax.set_title(t("pat_title", pat=pat) if pat != "benchmark" else t("bench_title"))
        ax.set_xlabel(t("x_evals"))
        ax.set_ylabel(t("y_mean_h"))
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)


def fig_box(pi: pd.DataFrame, out: Path) -> None:
    methods = [m for m in ("greedy", "ga_std", "ga_repair") if m in set(pi["method"])]
    data = [pi[pi["method"] == m]["median_H"].to_numpy() for m in methods]
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    bp = ax.boxplot(data, tick_labels=[METHOD_LABEL[m] for m in methods],
                    patch_artist=True, widths=0.55)
    for patch, m in zip(bp["boxes"], methods):
        patch.set_facecolor(COLORS[m]); patch.set_alpha(0.55)
    for i, d in enumerate(data, start=1):
        ax.scatter(np.full(len(d), i) + np.random.default_rng(0).normal(0, 0.05, len(d)),
                   d, s=14, color="#222222", alpha=0.7, zorder=3)
    ax.set_ylabel(t("y_h_med"))
    ax.set_title(t("title_quality"))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)


def fig_feasible(pi: pd.DataFrame, out: Path) -> None:
    pats = ["A", "B", "C", "benchmark"]
    methods = [m for m in ("ga_std", "ga_repair") if m in set(pi["method"])]
    width = 0.8 / max(1, len(methods))
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    x = np.arange(len(pats))
    for k, m in enumerate(methods):
        vals = []
        for pat in pats:
            s = pi[(pi["method"] == m) & (pi["pattern"] == pat)]
            vals.append(float((s["feasible_rate"] >= 0.5).mean()) if len(s) else 0.0)
        ax.bar(x + k * width, vals, width, label=METHOD_LABEL[m], color=COLORS[m], alpha=0.85)
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels([t("xt_loose"), t("xt_medium"), t("xt_tight"), t("xt_bench")])
    ax.set_ylabel(t("y_feas_share"))
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)


def fig_cost(pi: pd.DataFrame, out: Path) -> None:
    methods = [m for m in ("ga_std", "ga_repair") if m in set(pi["method"])]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0))
    for m in methods:
        s = pi[pi["method"] == m]
        axes[0].scatter(s["median_generations"], s["median_H"], s=22,
                        label=METHOD_LABEL[m], color=COLORS[m], alpha=0.8)
        axes[1].scatter(s["median_runtime_s"], s["median_H"], s=22,
                        label=METHOD_LABEL[m], color=COLORS[m], alpha=0.8)
    axes[0].set_xlabel(t("x_gens"))
    axes[1].set_xlabel(t("x_wall"))
    for ax in axes:
        ax.set_ylabel(t("y_h"))
        ax.grid(alpha=0.25)
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)


def fig_scaling(pi: pd.DataFrame, out: Path) -> None:
    methods = [m for m in ("greedy", "ga_std", "ga_repair") if m in set(pi["method"])]
    sizes = ["30", "60", "90"]
    fig, axes = plt.subplots(1, 3, figsize=(9.0, 2.9), sharey=False)
    for ax, pat in zip(axes, "ABC"):
        for m in methods:
            ys = []
            for sz in sizes:
                s = pi[(pi["method"] == m) & (pi["pattern"] == pat) & (pi["size"] == sz)]
                ys.append(float(s["median_H"].median()) if len(s) else np.nan)
            ax.plot(sizes, ys, marker="o", label=METHOD_LABEL[m], color=COLORS[m])
        ax.set_title(t("pat_title", pat=pat))
        ax.set_xlabel(t("x_sessions"))
        ax.grid(alpha=0.25)
        ax.legend(frameon=False, fontsize=7)
    axes[0].set_ylabel(t("y_h"))
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="03_experiments/raw/main.jsonl")
    ap.add_argument("--label", default="main")
    ap.add_argument("--lang", default="en", choices=["en", "id"],
                    help="bahasa label gambar (en = naskah Inggris, id = naskah Indonesia)")
    ap.add_argument("--figdir", default="04_results/figures",
                    help="folder keluaran gambar (relatif ke akar proyek)")
    args = ap.parse_args()
    global LANG
    LANG = args.lang
    raw = ROOT / args.raw
    ok, bad = load_raw(raw)
    pi = per_instance(ok)
    tables = ROOT / "04_results/tables"
    figs = ROOT / args.figdir
    tables.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    st, _ = stats_tables(pi)
    cost = cost_table(pi)
    byfam = pi.assign(avail=pi["pattern"]).groupby(["method", "avail", "size"]).agg(
        instances=("instance", "count"),
        feasible_share=("feasible_rate", lambda s: float((s >= 0.5).mean())),
        median_H=("median_H", "median"),
        median_P=("median_P", "median"),
    ).reset_index()

    pi.to_csv(tables / f"{args.label}_descriptive.csv", index=False)
    byfam.to_csv(tables / f"{args.label}_by_family.csv", index=False)
    st.to_csv(tables / f"{args.label}_stats.csv", index=False)
    cost.to_csv(tables / f"{args.label}_cost.csv", index=False)
    with pd.ExcelWriter(tables / f"{args.label}_tables.xlsx") as xw:
        pi.to_excel(xw, sheet_name="per_instance", index=False)
        byfam.to_excel(xw, sheet_name="by_family", index=False)
        st.to_excel(xw, sheet_name="stats", index=False)
        cost.to_excel(xw, sheet_name="cost", index=False)
        if len(bad):
            bad.to_excel(xw, sheet_name="failed_runs", index=False)

    fig_convergence(ok, figs / f"{args.label}_fig1_convergence.png")
    fig_box(pi, figs / f"{args.label}_fig2_quality_box.png")
    fig_feasible(pi, figs / f"{args.label}_fig3_feasible_rate.png")
    fig_cost(pi, figs / f"{args.label}_fig4_cost.png")
    fig_scaling(pi, figs / f"{args.label}_fig5_scaling.png")

    print(f"instances: {pi['instance'].nunique()} | runs ok: {len(ok)} | failed: {len(bad)}")
    print("\n== cost & quality by method ==")
    print(cost.to_string(index=False))
    print("\n== statistical tests ==")
    print(st.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
