"""Runner eksperimen: mengeksekusi spesifikasi job JSON secara paralel.

Setiap run menulis satu baris JSON ke 03_experiments/raw/<suite>.jsonl
(append), memuat konfigurasi lengkap, hasil, jejak evaluasi, versi, dan
identitas host — cukup untuk mereproduksi dan menelusuri setiap angka di
naskah.

Pemakaian:
    python run_experiment.py --spec 00_config/jobs_main.json [--jobs 12]
                             [--out 03_experiments/raw/main.jsonl]

Log stdout/stderr: 03_experiments/logs/run_<suite>_<timestamp>.log
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "02_code"))

import numpy as np  # noqa: E402

import model  # noqa: E402
import methods  # noqa: E402

_INST_CACHE: dict[str, model.Instance] = {}


def _instance(path: str) -> model.Instance:
    if path not in _INST_CACHE:
        _INST_CACHE[path] = model.load(str(ROOT / path))
    return _INST_CACHE[path]


def run_one(job: dict) -> dict:
    inst = _instance(job["instance"])
    cfg = dict(job["cfg"])
    if job["method"] == "ga_std" and cfg.get("pm_std"):
        cfg["pm"] = cfg["pm_std"]
    if isinstance(cfg.get("pm"), str):  # "1/n"
        cfg["pm"] = 1.0 / inst.n
    method = job["method"]
    t0 = time.perf_counter()
    try:
        if method == "greedy":
            res = methods.run_greedy(inst, cfg)
        else:
            res = methods.run_ga(inst, int(job["seed"]), cfg,
                                 method == "ga_repair", method)
        status = "ok"
        if method != "greedy" and (res["validated_H"] != res["best_H"]
                                   or res["validated_P"] != res["best_P"]):
            status = "validation_mismatch"
    except Exception as exc:  # run gagal dicatat, bukan dibuang
        res = {"method": method, "best_H": None, "best_P": None, "feasible": False,
               "evals": None, "evals_to_first_feasible": None, "generations": None,
               "repair_probes": None, "repair_sessions": None, "repair_swaps": None,
               "repair_failures": None, "budget_limited": None,
               "runtime_s": round(time.perf_counter() - t0, 4), "trace": [],
               "validated_H": None, "validated_P": None}
        status = "error:" + type(exc).__name__
    row = {
        "suite": job.get("suite"),
        "tag": job.get("tag"),
        "instance": job["instance"],
        "instance_name": inst.name,
        "family": inst.family,
        "n": inst.n,
        "n_slots": inst.S,
        "n_rooms": inst.R,
        "fill": round(inst.n / (inst.R * inst.S), 4),
        "method": method,
        "seed": job["seed"],
        "cfg": cfg,
        "status": status,
        **{k: res.get(k) for k in (
            "best_H", "best_P", "feasible", "evals", "evals_to_first_feasible",
            "generations", "repair_probes", "repair_sessions", "repair_swaps",
            "repair_failures", "budget_limited", "runtime_s", "validated_H",
            "validated_P")},
        "trace": res.get("trace", []),
        "wall_clock": datetime.now().isoformat(timespec="seconds"),
        "pid": os.getpid(),
    }
    if row["evals"]:
        row["repair_share"] = round((row["repair_probes"] or 0) / row["evals"], 4)
    else:
        row["repair_share"] = None
    return row


def host_info() -> dict:
    try:
        cpu = subprocess.run(["lscpu"], capture_output=True, text=True).stdout
        model_name = next((l.split(":", 1)[1].strip() for l in cpu.splitlines()
                           if l.startswith("Model name")), "unknown")
        cores = next((l.split(":", 1)[1].strip() for l in cpu.splitlines()
                      if l.startswith("CPU(s)")), "unknown")
    except Exception:
        model_name, cores = "unknown", "unknown"
    return {
        "hostname": socket.gethostname(),
        "cpu": model_name,
        "cores": cores,
        "mem_gb": round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9, 1),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    spec = json.loads((ROOT / args.spec).read_text())
    suite = spec.get("suite", "run")
    runs = spec["runs"][: args.limit] if args.limit else spec["runs"]
    out = ROOT / (args.out or f"03_experiments/raw/{suite}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    logs = ROOT / "03_experiments/logs"
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs / f"run_{suite}_{stamp}.log"

    hinfo = host_info()
    print(f"[{stamp}] suite={suite} runs={len(runs)} jobs={args.jobs} out={out}")
    print(f"host: {hinfo}")
    print(f"log : {log_path}")

    t0 = time.perf_counter()
    done = 0
    with open(out, "a", encoding="utf-8") as fh, open(log_path, "a", encoding="utf-8") as lg:
        lg.write(json.dumps({"host": hinfo, "suite": suite, "runs": len(runs),
                             "spec": args.spec, "start": stamp}) + "\n")
        with Pool(processes=args.jobs) as pool:
            for row in pool.imap_unordered(run_one, runs, chunksize=1):
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                done += 1
                if done % 25 == 0 or done == len(runs):
                    el = time.perf_counter() - t0
                    print(f"  {done}/{len(runs)} run selesai ({el:.1f}s, "
                          f"{el / done:.2f}s/run)", flush=True)
        lg.write(json.dumps({"done": done, "elapsed_s": round(time.perf_counter() - t0, 1)}) + "\n")
    print(f"selesai: {done} run, {time.perf_counter() - t0:.1f}s → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
