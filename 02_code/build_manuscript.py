"""Menyusun naskah final dari bagian draf + tabel hasil (semua angka dari CSV/JSONL).

Alur:
  manuscript_source.md (seluruh teks naskah, satu berkas)
  + tabel yang dihasilkan dari 04_results/tables/*.csv
  + daftar referensi 07_literature/references.md
  -> 05_manuscript/manuscript.md -> 05_manuscript/*.docx (via md2docx.py)

Semua placeholder {{...}} wajib terisi; skrip gagal jika ada yang tersisa,
sehingga naskah tidak pernah berisi angka karangan atau nilai "TBD".

Pemakaian: python 02_code/build_manuscript.py [--label main]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "05_manuscript"
TAB = ROOT / "04_results/tables"
LBL = {"greedy": "Greedy", "ga_std": "GA", "ga_repair": "GA-R"}
ORDER = ["greedy", "ga_std", "ga_repair"]

# Bahasa naskah: "en" (berkas utama) atau "id" (versi Indonesia di 05_manuscript/idn/).
LANG = "en"

# Judul tabel per bahasa.
CAPTIONS = {
    "en": {
        "instances": "**Table 1.** Characterisation of the 21 test instances: number of sessions, "
                     "rooms and slots, room occupancy (sessions divided by rooms × slots), mean "
                     "lecturer availability (share of slots open to each session) and availability "
                     "pattern.",
        "main_performance": "**Table 2.** Quality and reliability per method over the 21 test "
                            "instances (median over instances of the per-instance median over 20 seeds).",
        "main_stats": "**Table 3.** Paired statistical tests over the 21 test instances, with "
                      "Holm correction and Cliff's delta.",
        "main_by_pattern": "**Table 4.** Performance by instance family: mean feasible share, median "
                           "hard violations and median preference penalty per method.",
        "cost": "**Table 5.** Computational cost per method: wall-clock time, completed generations, "
                "share of the evaluation budget spent on repair, and evaluations needed to reach the "
                "first feasible timetable on benchmark instances.",
        "ablation_compare": "**Table 6.** Ablation: each variant compared with the locked configuration "
                            "on the same 21 instances (paired per instance, Holm correction across variants).",
        "scaling": "**Table 7.** Effect of instance size and availability pattern on the synthetic "
                   "family (median per instance).",
        "appendix": "**Table A1.** Per-instance results, median over 20 seeds.",
        "ablation": "",
    },
    "id": {
        "instances": "**Tabel 1.** Karakterisasi 21 instance uji: jumlah sesi, ruang, dan slot, "
                     "okupansi ruang (sesi dibagi ruang × slot), ketersediaan dosen rata-rata "
                     "(porsi slot yang terbuka bagi setiap sesi), dan pola ketersediaan.",
        "main_performance": "**Tabel 2.** Kualitas dan keandalan per metode pada 21 instance uji "
                            "(median atas instance dari median per instance atas 20 seed).",
        "main_stats": "**Tabel 3.** Uji statistik berpasangan pada 21 instance uji, dengan koreksi "
                      "Holm dan Cliff's delta.",
        "main_by_pattern": "**Tabel 4.** Kinerja menurut keluarga instance: rata-rata porsi layak, "
                           "median pelanggaran hard, dan median penalti preferensi per metode.",
        "cost": "**Tabel 5.** Biaya komputasi per metode: waktu dinding, generasi yang selesai, "
                "porsi anggaran evaluasi yang dipakai untuk repair, dan jumlah evaluasi sampai "
                "jadwal layak pertama pada instance benchmark.",
        "ablation_compare": "**Tabel 6.** Ablation: setiap varian dibandingkan dengan konfigurasi "
                            "terkunci pada 21 instance yang sama (berpasangan per instance, koreksi "
                            "Holm antarvarians).",
        "scaling": "**Tabel 7.** Pengaruh ukuran instance dan pola ketersediaan pada keluarga "
                   "sintetis (median per instance).",
        "appendix": "**Tabel A1.** Hasil per instance, median dari 20 seed.",
        "ablation": "",
    },
}

# Judul kolom tabel: versi Indonesia (kunci = baris judul persis versi Inggris).
ID_HEADERS = {
    "| Instance | Sessions | Rooms | Slots | Room occupancy | Mean availability | Pattern |":
        "| Instance | Sesi | Ruang | Slot | Okupansi ruang | Ketersediaan rata-rata | Pola |",
    "| Method | Instances with feasible majority | Median *H* | Mean *H* | Median *P* | Generations | "
    "Runtime (s) | Repair share of budget |":
        "| Metode | Instance dengan mayoritas layak | Median *H* | Rata-rata *H* | Median *P* | "
        "Generasi | Waktu (s) | Porsi anggaran untuk repair |",
    "| Test | Metric | Comparison | Instances | Statistic | *p* | *p* (Holm) | Cliff's *d* |":
        "| Uji | Metrik | Perbandingan | Instance | Statistik | *p* | *p* (Holm) | Cliff's *d* |",
    "| Family | Instances | Greedy feasible / *H* / *P* | GA feasible / *H* / *P* | "
    "GA-R feasible / *H* / *P* |":
        "| Keluarga | Instance | Greedy layak / *H* / *P* | GA layak / *H* / *P* | "
        "GA-R layak / *H* / *P* |",
    "| Method | Runtime all (s) | Runtime benchmark (s) | Generations | Repair share | "
    "Feasible benchmark runs | Evaluations to first feasible (median of those runs) |":
        "| Metode | Waktu semua (s) | Waktu benchmark (s) | Generasi | Porsi repair | "
        "Run benchmark layak | Evaluasi sampai layak pertama (median run tersebut) |",
    "| Variant | Median *H* | *H* worse / better / tie | Median *P* | Feasible share | Repair share | "
    "Generations | *p* (Holm, *P*) |":
        "| Varian | Median *H* | *H* lebih buruk / lebih baik / seri | Median *P* | Porsi layak | "
        "Porsi repair | Generasi | *p* (Holm, *P*) |",
    "| Sessions | Pattern | GA median *H* | GA-R median *H* | GA median *P* | GA-R median *P* |":
        "| Sesi | Pola | Median *H* GA | Median *H* GA-R | Median *P* GA | Median *P* GA-R |",
    "| Instance | GA med *H* | GA feasible | GA-R med *H* | GA-R feasible | GA med *P* | "
    "GA-R med *P* | GA gens | GA-R gens | GA-R repair share |":
        "| Instance | Med *H* GA | GA layak | Med *H* GA-R | GA-R layak | Med *P* GA | "
        "Med *P* GA-R | Gen GA | Gen GA-R | Porsi repair GA-R |",
}

# Sel tabel yang perlu diterjemahkan (hanya diterapkan pada baris tabel).
ID_CELLS = [
    ("| never |", "| tidak pernah |"),
    ("wilcoxon paired", "Wilcoxon berpasangan"),
    ("posthoc wilcoxon holm", "post-hoc Wilcoxon (Holm)"),
    ("mcnemar exact", "McNemar eksak"),
    ("ga repair vs ga std", "GA-R vs GA"),
    ("ga repair vs greedy", "GA-R vs Greedy"),
    ("ga std vs greedy", "GA vs Greedy"),
]


MARKER = re.compile(r"^(- |\* |\d+\.\s)")


def localise_tables(doc: str) -> str:
    """Terjemahkan judul kolom dan sel tabel ke bahasa Indonesia.

    Hanya baris tabel (diawali "|") yang disentuh, sehingga istilah di dalam
    paragraf tidak ikut berubah.
    """
    out = []
    for line in doc.splitlines():
        if line.startswith("|"):
            line = ID_HEADERS.get(line, line)
            for en, idn in ID_CELLS:
                line = line.replace(en, idn)
        out.append(line)
    return "\n".join(out)


def unwrap(text: str) -> str:
    """Gabungkan baris yang dipotong (hard-wrap) menjadi satu baris per paragraf.

    Draf ditulis dengan lebar ~78 karakter, sehingga satu paragraf terpecah
    menjadi beberapa baris. DOCX menerjemahkan tiap baris menjadi paragraf
    terpisah, yang membuat teks tidak bisa diratakan kiri-kanan. Blok yang
    memang berdiri sendiri (heading, tabel, gambar, komentar) dibiarkan.
    """
    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            out.append(" ".join(buf))
            buf.clear()

    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            flush()
            out.append("")
            continue
        if s.startswith(("#", "|", "![", "<!--")):
            flush()
            out.append(s)
            continue
        if MARKER.match(s):
            flush()
            buf.append(s)
            continue
        buf.append(s)
    flush()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def f(x, nd=2):
    if x is None or pd.isna(x):
        return "–"
    if isinstance(x, (int,)):
        return str(x)
    return f"{float(x):.{nd}f}"


# ---------------------------------------------------------------- tables ----
def table_performance(label: str) -> str:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    cost = pd.read_csv(TAB / f"{label}_cost.csv").set_index("method")
    rows = ["| Method | Instances with feasible majority | Median *H* | Mean *H* | "
            "Median *P* | Generations | Runtime (s) | Repair share of budget |",
            "|---|---|---|---|---|---|---|---|"]
    for m in ORDER:
        sub = pi[pi["method"] == m]
        c = cost.loc[m]
        rows.append(
            f"| {LBL[m]} | {int((sub['feasible_rate'] >= 0.5).sum())}/{sub['instance'].nunique()} | "
            f"{f(sub['median_H'].median())} | {f(sub['mean_H'].mean())} | "
            f"{f(sub['median_P'].median())} | {f(sub['median_generations'].median(), 0)} | "
            f"{f(sub['median_runtime_s'].median())} | {f(sub['median_repair_share'].median(), 3)} |")
    return "\n".join(rows)


def table_stats(label: str) -> str:
    st = pd.read_csv(TAB / f"{label}_stats.csv")
    keep = st[st["test"].isin(["wilcoxon_paired", "friedman", "posthoc_wilcoxon_holm",
                              "mcnemar_exact"])]
    rows = ["| Test | Metric | Comparison | Instances | Statistic | *p* | *p* (Holm) | Cliff's *d* |",
            "|---|---|---|---|---|---|---|---|"]
    for _, r in keep.iterrows():
        rows.append(f"| {r['test'].replace('_', ' ')} | {r['metric']} | "
                    f"{str(r['comparison']).replace('_vs_', ' vs ').replace('+', ', ')} | "
                    f"{int(r['n_units'])} | {f(r['statistic'], 3)} | {f(r['p_value'], 4)} | "
                    f"{f(r['p_holm'], 4)} | {f(r['cliffs_delta'], 2)} |")
    return "\n".join(rows)


def table_by_pattern(label: str) -> str:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    rows = ["| Family | Instances | Feasible share | Median *H* | Median *P* |", "|---|---|---|---|---|"]
    for fam in ["A", "B", "C", "benchmark"]:
        s = pi[pi["pattern"] == fam]
        if s.empty:
            continue
        cells = []
        for m in ORDER:
            g = s[s["method"] == m]
            cells.append(f"{LBL[m]}: {f(g['feasible_rate'].mean())} / {f(g['median_H'].median())} / "
                         f"{f(g['median_P'].median())}")
        rows.append(f"| {fam if fam != 'benchmark' else 'public benchmark'} | {s['instance'].nunique()} | "
                    + " | ".join(cells) + " |")
    head = ["| Family | Instances | Greedy feasible / *H* / *P* | GA feasible / *H* / *P* | "
            "GA-R feasible / *H* / *P* |", "|---|---|---|---|---|"]
    return "\n".join(head + [r for r in rows[2:]])


def table_cost(label: str) -> str:
    """Biaya per metode. Kolom evaluasi-ke-layak dihitung dari JSONL mentah
    (median atas run yang berhasil, benchmark saja), bukan median dari median."""
    cost = pd.read_csv(TAB / f"{label}_cost.csv").set_index("method")
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    raw = [json.loads(l) for l in (ROOT / f"03_experiments/raw/{label}.jsonl").open()]
    bm_runs = [r for r in raw if r["family"] == "benchmark"]
    rows = ["| Method | Runtime all (s) | Runtime benchmark (s) | Generations | Repair share | "
            "Feasible benchmark runs | Evaluations to first feasible (median of those runs) |",
            "|---|---|---|---|---|---|---|"]
    for m in ORDER:
        sub = pi[pi["method"] == m]
        bm = sub[sub["pattern"] == "benchmark"]
        runs = [r for r in bm_runs if r["method"] == m]
        succ = [r["evals_to_first_feasible"] for r in runs
                if r.get("evals_to_first_feasible") is not None]
        rows.append(f"| {LBL[m]} | {f(cost.loc[m, 'median_runtime_s'])} | "
                    f"{f(bm['median_runtime_s'].median())} | {f(sub['median_generations'].median(), 0)} | "
                    f"{f(sub['median_repair_share'].median(), 3)} | "
                    f"{len(succ)}/{len(runs)} | "
                    f"{f(pd.Series(succ).median(), 0) if succ else 'never'} |")
    return "\n".join(rows)


def table_ablation() -> str:
    p = TAB / "ablation_descriptive.csv"
    if not p.exists():
        return "_Ablation belum dianalisis._"
    abl = pd.read_csv(p)
    rows = ["| Variant | Feasible share | Median *H* | Median *P* | Generations | Repair share |",
            "|---|---|---|---|---|---|"]
    order = ["abl_attempts3", "abl_k1", "abl_k10", "abl_swap_on", "abl_no_seed"]
    for tag in order:
        g = abl[abl["variant"] == tag]
        if g.empty:
            continue
        rows.append(f"| {tag} | {f(g['feasible_rate'].mean())} | {f(g['median_H'].median())} | "
                    f"{f(g['median_P'].median())} | {f(g['median_generations'].median(), 0)} | "
                    f"{f(g['median_repair_share'].median(), 3)} |")
    return "\n".join(rows)


def table_ablation_compare() -> str:
    p = TAB / "ablation_compare.csv"
    if not p.exists():
        return "_Ablation comparison belum dihitung._"
    df = pd.read_csv(p)
    rows = ["| Variant | Median *H* | *H* worse / better / tie | Median *P* | Feasible share | "
            "Repair share | Generations | *p* (Holm, *P*) |",
            "|---|---|---|---|---|---|---|---|"]
    for tag, g in df.groupby("variant", sort=False):
        h = g[g["metric"] == "median_H"].iloc[0]
        pp = g[g["metric"] == "median_P"].iloc[0]
        rows.append(f"| {tag} | {f(h['median_variant'])} | {int(h['losses'])} / {int(h['wins'])} / "
                    f"{int(h['ties'])} | {f(pp['median_variant'])} | {f(h['feasible_share_variant'])} | "
                    f"{f(h['repair_share_variant'], 3)} | {f(h['generations_variant'], 0)} | "
                    f"{f(pp['p_holm'], 4)} |")
    return "\n".join(rows)


def table_scaling(label: str) -> str:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    syn = pi[pi["pattern"].isin(["A", "B", "C"])]
    sizes = sorted(syn["n"].unique())
    rows = ["| Sessions | Pattern | GA median *H* | GA-R median *H* | GA median *P* | GA-R median *P* |",
            "|---|---|---|---|---|---|"]
    for sz in sizes:
        for pat in ["A", "B", "C"]:
            g = syn[(syn["n"] == sz) & (syn["pattern"] == pat)]
            a = g[g["method"] == "ga_std"]
            b = g[g["method"] == "ga_repair"]
            if a.empty or b.empty:
                continue
            rows.append(f"| {int(sz)} | {pat} | {f(a['median_H'].median())} | {f(b['median_H'].median())} | "
                        f"{f(a['median_P'].median())} | {f(b['median_P'].median())} |")
    return "\n".join(rows)


def instance_availability(name: str) -> float:
    """Rata-rata porsi slot yang tersedia bagi tiap sesi (1 - forbidden.mean())."""
    import sys
    sys.path.insert(0, str(ROOT / "02_code"))
    import model as M  # noqa: PLC0415

    for sub in ("synthetic", "pilot", "benchmark"):
        path = ROOT / f"01_data/{sub}/{name}.json"
        if path.exists():
            inst = M.load(path)
            return float(1.0 - inst.forbidden.mean())
    return float("nan")


def table_instances(label: str) -> str:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    base = pi.drop_duplicates("instance").sort_values(["family", "instance"])
    rows = ["| Instance | Sessions | Rooms | Slots | Room occupancy | Mean availability | Pattern |",
            "|---|---|---|---|---|---|---|"]
    for _, r in base.iterrows():
        rows.append(f"| {r['instance']} | {int(r['n'])} | {int(r['n_rooms'])} | {int(r['n_slots'])} | "
                    f"{f(r['fill'], 3)} | {f(instance_availability(r['instance']), 3)} | {r['pattern']} |")
    return "\n".join(rows)


def table_appendix(label: str) -> str:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    idx = pi.set_index(["instance", "method"])
    inst = sorted(pi["instance"].unique())
    rows = ["| Instance | GA med *H* | GA feasible | GA-R med *H* | GA-R feasible | GA med *P* | "
            "GA-R med *P* | GA gens | GA-R gens | GA-R repair share |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for i in inst:
        try:
            a = idx.loc[(i, "ga_std")]
            b = idx.loc[(i, "ga_repair")]
        except KeyError:
            continue
        rows.append(f"| {i} | {f(a['median_H'])} | {f(a['feasible_rate'])} | {f(b['median_H'])} | "
                    f"{f(b['feasible_rate'])} | {f(a['median_P'])} | {f(b['median_P'])} | "
                    f"{f(a['median_generations'], 0)} | {f(b['median_generations'], 0)} | "
                    f"{f(b['median_repair_share'], 3)} |")
    return "\n".join(rows)


# ------------------------------------------------------------ placeholders ----
def placeholder_values(label: str) -> dict[str, str]:
    pi = pd.read_csv(TAB / f"{label}_descriptive.csv")
    cost = pd.read_csv(TAB / f"{label}_cost.csv").set_index("method")
    cfg = json.loads((ROOT / "00_config/config_final.json").read_text())
    rows = [json.loads(l) for l in (ROOT / f"03_experiments/raw/{label}.jsonl").open()]

    def n_inst_feas(m):
        s = pi[pi["method"] == m]
        return str(int((s["feasible_rate"] >= 0.5).sum()))

    med_h = {m: pi[pi["method"] == m]["median_H"].median() for m in ORDER}
    gens = cost.loc["ga_std", "median_generations"] / cost.loc["ga_repair", "median_generations"]
    share = cost.loc["ga_repair", "median_repair_share"]
    probes = sum(r.get("repair_probes", 0) for r in rows if r["method"] == "ga_repair")
    fails = sum(r.get("repair_failures", 0) for r in rows if r["method"] == "ga_repair")
    pilot = [json.loads(l) for l in (ROOT / "03_experiments/raw/pilot.jsonl").open()]
    # Tag pilot untuk konfigurasi terkunci: pm1/n_k5_a1_s0 (12 run = 4 instance dev x 3 seed)
    pf = [r for r in pilot if r["method"] == "ga_repair" and r["tag"] == "pm1/n_k5_a1_s0"]
    # Baseline pembanding: GA standar dengan pm = 1/n (tag std_pm1/n, 12 run dev)
    ps = [r for r in pilot if r["method"] == "ga_std" and r["tag"] == "std_pm1/n"]

    if LANG == "id":
        # pemisah ribuan mengikuti kebiasaan Indonesia: 10.000
        ang = f"{cfg['budget']:,}".replace(",", ".")
        locked = (f"mutasi 1/*n* per gen, *k* = {cfg['repair_max_sessions']} sesi yang diperbaiki, "
                  f"{cfg['repair_attempts']} slot kandidat per sesi, tanpa fallback swap, "
                  f"inisialisasi berbenih greedy, populasi {cfg['pop_size']}, crossover "
                  f"{cfg['pc']}, {cfg['elitism']} elit, anggaran {ang}")
    else:
        locked = (f"mutation 1/*n* per gene, *k* = {cfg['repair_max_sessions']} repaired sessions, "
                  f"{cfg['repair_attempts']} candidate slot per session, no swap fallback, "
                  f"greedy-seeded initialisation, population {cfg['pop_size']}, crossover "
                  f"{cfg['pc']}, {cfg['elitism']} elites, budget {cfg['budget']:,}")

    def med(vals):
        import statistics as st
        return f"{st.median(vals):.2f}" if vals else "–"

    return {
        "n_inst": str(pi["instance"].nunique()),
        "ga_std_feas_inst": n_inst_feas("ga_std"),
        "ga_repair_feas_inst": n_inst_feas("ga_repair"),
        "med_H_std": f"{med_h['ga_std']:.0f}",
        "med_H_repair": f"{med_h['ga_repair']:.0f}",
        "repair_share": f"{share*100:.0f}%",
        "gens_ratio": f"{gens:.1f}",
        "budget": (f"{cfg['budget']:,}".replace(",", ".") if LANG == "id" else f"{cfg['budget']:,}"),
        "pc": f"{cfg['pc']}",
        "pm_desc": ("1/*n* (0.033 pada 30 sesi turun menjadi 0.006 pada 160 sesi)" if LANG == "id"
                    else "1/*n* (0.033 at 30 sessions down to 0.006 at 160)"),
        "k_repair": str(cfg["repair_max_sessions"]),
        "repair_attempts": str(cfg["repair_attempts"]),
        "locked_cfg": locked,
        "pilot_runs": str(len(pilot)),
        "pilot_feas_repair": str(sum(1 for r in pf if r["feasible"])),
        "pilot_runs_repair": str(len(pf)),
        "pilot_H_repair": med([r["best_H"] for r in pf]),
        "pilot_P_repair": med([r["best_P"] for r in pf]),
        "pilot_feas_std": str(sum(1 for r in ps if r["feasible"])),
        "pilot_runs_std": str(len(ps)),
        "pilot_H_std": med([r["best_H"] for r in ps]),
        "probe_total": f"{probes/1e6:.2f} million",
        "probe_fail_pct": f"{fails/probes*100:.0f}%" if probes else "–",
    }


TABLE_FUNCS = {
    "main_performance": lambda label: table_performance(label),
    "main_stats": table_stats,
    "main_by_pattern": table_by_pattern,
    "cost": table_cost,
    "ablation": lambda label: table_ablation(),
    "ablation_compare": lambda label: table_ablation_compare(),
    "scaling": table_scaling,
    "instances": table_instances,
    "appendix": table_appendix,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    ap.add_argument("--lang", default="en", choices=["en", "id"],
                    help="en = naskah Inggris (berkas utama), id = versi Indonesia di 05_manuscript/idn/")
    args = ap.parse_args()
    global LANG
    LANG = args.lang
    src_dir = MAN / "idn" if LANG == "id" else MAN

    # Satu berkas sumber untuk seluruh teks naskah (lihat manuscript_source.md).
    # unwrap() tetap dipanggil agar sumber yang ter-hard-wrap pun aman.
    src_name = "manuscript_source_id.md" if LANG == "id" else "manuscript_source.md"
    source = unwrap((src_dir / src_name).read_text())
    refs_path = ROOT / "07_literature/references.md"
    if refs_path.exists():
        # buang judul dan baris catatan build; naskah hanya memuat daftar entri
        lines = refs_path.read_text().splitlines()
        keep = [re.sub(r"^\d+\.\s+", "", l) for l in lines
                if l.strip() and not l.startswith("#") and not l.startswith("Jumlah entri")
                and not l.startswith("Metadata")]
        # gaya naskah: penulis-tahun di teks, daftar tanpa nomor
        refs = "\n\n".join(keep).strip()
    else:
        refs = "_References not built._"

    body = source

    # sisipkan tabel
    captions = CAPTIONS[LANG]

    def insert_table(match):
        key = match.group(1)
        fn = TABLE_FUNCS.get(key)
        if fn is None:
            raise SystemExit(f"unknown table key: {key}")
        cap = captions.get(key, "")
        body = fn(args.label)
        return (cap + "\n\n" + body) if cap else body

    body = re.sub(r"\{\{TABLE:([a-z_]+)\}\}", insert_table, body)

    # isi placeholder teks
    for k, v in placeholder_values(args.label).items():
        body = body.replace("{{" + k + "}}", v)

    # sisipkan tabel instance di §4.3 bila diminta
    body = body.replace("{{INSTANCE_TABLE}}", table_instances(args.label))

    left = sorted(set(re.findall(r"\{\{([a-zA-Z_]+)\}\}", body)))
    if left:
        raise SystemExit(f"placeholder belum terisi: {left}")

    if LANG == "id":
        appendix = ("\n\n## Lampiran A. Hasil per instance\n\n"
                    "Median dari 20 seed per instance; kelayakan adalah porsi seed yang jadwal "
                    "terbaiknya memenuhi seluruh kendala hard.\n\n"
                    + table_appendix(args.label) + "\n")
        refs_heading = "## Daftar Pustaka"
    else:
        appendix = ("\n\n## Appendix A. Per-instance results\n\n"
                    "Median over 20 seeds per instance; feasibility is the share of seeds whose "
                    "best timetable satisfies all hard constraints.\n\n"
                    + table_appendix(args.label) + "\n")
        refs_heading = "## References"

    doc = body + "\n\n" + refs_heading + "\n\n" + refs + appendix

    if LANG == "id":
        doc = localise_tables(doc)

    out = src_dir / ("manuscript_id.md" if LANG == "id" else "manuscript.md")
    out.write_text(doc)
    words = len(re.findall(r"\b\w+\b", doc))
    print(f"wrote {out} ({len(doc)} chars, ~{words} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
