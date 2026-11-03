"""Builder spesifikasi job untuk pilot, eksperimen utama, dan ablation.

Menulis berkas JSON ke 00_config/jobs_<suite>.json. Runner
(`run_experiment.py`) mengeksekusi spesifikasi ini apa adanya, sehingga daftar
run bersifat tertelusur dan tidak ditentukan di dalam kode runner.

Pemakaian:
    python make_jobs.py pilot
    python make_jobs.py main
    python make_jobs.py ablation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG_DIR = ROOT / "00_config"

DEV_INSTANCES = [
    "01_data/pilot/pilot45B.json",
    "01_data/pilot/pilot45C.json",
    "01_data/benchmark/comp13.json",
    "01_data/benchmark/comp14.json",
]

TEST_SYNTHETIC = [f"01_data/synthetic/syn{s}{p}.json" for s in (30, 60, 90) for p in "ABC"]
TEST_BENCHMARK = [f"01_data/benchmark/comp{i:02d}.json" for i in range(1, 13)]
TEST_INSTANCES = TEST_SYNTHETIC + TEST_BENCHMARK

PILOT_GRID = {
    "pm": ["1/n", 0.02, 0.05],
    "repair_max_sessions": [1, 3, 5],
    "repair_attempts": [1, 2],
    "swap_attempts": [0, 1],
}

BASE = {
    "budget": 10000,
    "pop_size": 50,
    "pc": 0.8,
    "elitism": 2,
}


def _pm_value(pm, n: int) -> float:
    return 1.0 / n if pm == "1/n" else float(pm)


def build_pilot(seeds, budget, max_combos=None):
    """Satu kombinasi parameter = satu tag; dijalankan pada instance dev."""
    combos = []
    for pm in PILOT_GRID["pm"]:
        for k in PILOT_GRID["repair_max_sessions"]:
            for att in PILOT_GRID["repair_attempts"]:
                for sw in PILOT_GRID["swap_attempts"]:
                    combos.append({"pm": pm, "repair_max_sessions": k,
                                   "repair_attempts": att, "swap_attempts": sw})
    if max_combos:
        combos = combos[:max_combos]
    runs = []
    for combo in combos:
        tag = "pm{pm}_k{k}_a{att}_s{sw}".format(
            pm=str(combo["pm"]).replace(".", "p"),
            k=combo["repair_max_sessions"], att=combo["repair_attempts"],
            sw=combo["swap_attempts"])
        for inst in DEV_INSTANCES:
            for seed in seeds:
                cfg = dict(BASE, budget=budget, pm=combo["pm"],
                           repair_max_sessions=combo["repair_max_sessions"],
                           repair_attempts=combo["repair_attempts"],
                           swap_attempts=combo["swap_attempts"])
                runs.append({"instance": inst, "method": "ga_repair",
                             "seed": seed, "cfg": cfg, "tag": tag})
    # sweep pm untuk GA standar (agar baseline memperoleh penyetelan yang adil)
    for pm in PILOT_GRID["pm"]:
        tag = "std_pm" + str(pm).replace(".", "p")
        for inst in DEV_INSTANCES:
            for seed in seeds:
                runs.append({"instance": inst, "method": "ga_std", "seed": seed,
                             "cfg": dict(BASE, budget=budget, pm=pm),
                             "tag": tag})
    # baseline greedy (deterministik) pada instance dev
    for inst in DEV_INSTANCES:
        runs.append({"instance": inst, "method": "greedy", "seed": -1,
                     "cfg": dict(BASE, budget=budget), "tag": "greedy"})
    return {"suite": "pilot", "budget": budget, "runs": runs}


def build_main(seeds, budget, final_cfg):
    runs = []
    for inst in TEST_INSTANCES:
        runs.append({"instance": inst, "method": "greedy", "seed": -1,
                     "cfg": dict(final_cfg, budget=budget), "tag": "main"})
        for seed in seeds:
            runs.append({"instance": inst, "method": "ga_std", "seed": seed,
                         "cfg": dict(final_cfg, budget=budget), "tag": "main"})
            runs.append({"instance": inst, "method": "ga_repair", "seed": seed,
                         "cfg": dict(final_cfg, budget=budget), "tag": "main"})
    return {"suite": "main", "budget": budget, "runs": runs}


def build_ablation(seeds, budget, final_cfg):
    # Varian ablation dipilih agar tidak redundan dengan konfigurasi terkunci
    # (k=5, attempts=1, swap=0, seeding greedy). "Repair dimatikan" = ga_std
    # yang sudah ada di suite utama.
    variants = {
        "abl_attempts3": {"repair_attempts": 3},    # batas percobaan perpindahan
        "abl_k1": {"repair_max_sessions": 1},
        "abl_k10": {"repair_max_sessions": 10},
        "abl_swap_on": {"swap_attempts": 1},
        "abl_no_seed": {"seed_mode": "random"},     # inisialisasi acak
    }
    runs = []
    for name, override in variants.items():
        cfg = dict(final_cfg, budget=budget, **override)
        for inst in TEST_INSTANCES:
            for seed in seeds:
                runs.append({"instance": inst, "method": "ga_repair", "seed": seed,
                             "cfg": cfg, "tag": name})
    return {"suite": "ablation", "budget": budget, "runs": runs}


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "main"
    final_path = CFG_DIR / "config_final.json"
    final_cfg = json.loads(final_path.read_text()) if final_path.exists() else {}
    if which == "pilot":
        spec = build_pilot(seeds=[1, 2, 3], budget=10000)
    elif which == "main":
        spec = build_main(seeds=list(range(1, 21)), budget=int(final_cfg.get("budget", 10000)),
                          final_cfg=final_cfg)
    elif which == "ablation":
        spec = build_ablation(seeds=list(range(1, 21)), budget=int(final_cfg.get("budget", 10000)),
                              final_cfg=final_cfg)
    else:
        raise SystemExit(f"suite tidak dikenal: {which}")
    out = CFG_DIR / f"jobs_{which}.json"
    out.write_text(json.dumps(spec, indent=1))
    print(f"{out.relative_to(ROOT)}: {len(spec['runs'])} run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
