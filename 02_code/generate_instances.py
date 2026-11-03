"""Generator instance sintetis untuk studi repair GA pada penjadwalan kuliah.

Prinsip (sesuai brief Kelompok 1): instance TIDAK dibuat acak lalu diuji
feasible/tidak, tetapi dibangun dari jadwal yang SUDAH DIKETAHUI FEASIBLE,
kemudian kendala ditambahkan sedemikian rupa sehingga jadwal tersebut tetap
memenuhi semua hard constraint. Dengan cara itu setiap instance dijamin
memiliki solusi feasible (H = 0) dan kelayakan bukan lagi pertanyaan terbuka.

Konstruksi:
 1. Sesi dibentuk dari (dosen, kelompok mahasiswa, jumlah mahasiswa).
 2. Jadwal basis feasible dibangun dengan penempatan rakus berulang:
    tiap sesi mendapat satu sel (ruang, slot) unik tanpa konflik dosen,
    ruang, atau kelompok, dan kapasitas ruang mencukupi.
 3. Ketersediaan dosen = slot yang dipakai dosen itu pada jadwal basis,
    ditambah sebagian slot lain menurut pola ketersediaan:
       A longgar : 60% slot sisa tersedia
       B sedang  : 30% slot sisa tersedia
       C ketat   : 10% slot sisa tersedia
 4. Instance + jadwal basis disimpan; seed generator dicatat.

Pemakaian:
    python 02_code/generate_instances.py            # 9 instance utama + 3 pilot
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "02_code"))

import model  # noqa: E402

DAYS, PERIODS = 5, 6
SLOTS = DAYS * PERIODS
CAPACITIES = [50, 80, 110, 140, 170, 200]
PATTERNS = {"A": 0.60, "B": 0.30, "C": 0.10}


def build(rng: np.random.Generator, n_sessions: int, n_rooms: int,
          n_teachers: int, n_groups: int, seed: int, tag: str,
          pattern: str) -> tuple[dict, list[int], list[int]]:
    rooms = [{"id": f"R{i + 1}", "capacity": CAPACITIES[i]} for i in range(n_rooms)]

    # --- sessions ---------------------------------------------------------
    sessions = []
    teacher_of, group_of = [], []
    for i in range(n_sessions):
        teacher = f"T{i % n_teachers:02d}"
        group = f"G{i % n_groups:02d}"
        students = int(rng.integers(15, CAPACITIES[n_rooms - 1] + 1))
        sessions.append({
            "id": f"S{i + 1:03d}",
            "course": f"C{i + 1:03d}",
            "teacher": teacher,
            "groups": [group],
            "students": students,
            "allowed_rooms": [],
        })
        teacher_of.append(teacher)
        group_of.append(group)

    ok_room = [[ri for ri, r in enumerate(rooms) if r["capacity"] >= s["students"]]
               for s in sessions]

    # --- base feasible schedule (retry until construction succeeds) -------
    for attempt in range(200):
        slot_rooms = [set() for _ in range(SLOTS)]
        slot_teach = [set() for _ in range(SLOTS)]
        slot_group = [set() for _ in range(SLOTS)]
        base_slot = [-1] * n_sessions
        base_room = [-1] * n_sessions
        # most-constrained-first: sessions with fewer compatible rooms placed earlier
        key = np.array([len(ok_room[i]) for i in range(n_sessions)]) + rng.random(n_sessions) * 0.5
        order = np.argsort(key)
        failed = False
        for i in order:
            i = int(i)
            candidates = []
            for s in range(SLOTS):
                if teacher_of[i] in slot_teach[s] or group_of[i] in slot_group[s]:
                    continue
                free_rooms = [r for r in ok_room[i] if r not in slot_rooms[s]]
                if free_rooms:
                    candidates.append((len(slot_rooms[s]), s, free_rooms))
            if not candidates:
                failed = True
                break
            candidates.sort(key=lambda t: t[0])          # prefer least-loaded slots
            least = [c for c in candidates if c[0] == candidates[0][0]]
            _, pick, free_rooms = least[int(rng.integers(len(least)))]
            room = int(rng.choice(free_rooms))
            base_slot[i] = pick
            base_room[i] = room
            slot_rooms[pick].add(room)
            slot_teach[pick].add(teacher_of[i])
            slot_group[pick].add(group_of[i])
        if not failed:
            break
    else:  # pragma: no cover
        raise RuntimeError(f"could not construct feasible base schedule for seed {seed}")

    # --- lecturer availability (keeps the base schedule feasible) ---------
    share = PATTERNS[pattern]
    forbidden: list[list[int]] = [[] for _ in range(n_sessions)]
    avail_slots: dict[str, list[int]] = {}
    for t in sorted(set(teacher_of)):
        used = sorted({base_slot[i] for i in range(n_sessions) if teacher_of[i] == t})
        rest = [s for s in range(SLOTS) if s not in used]
        k = int(round(share * len(rest)))
        extra = sorted(rng.choice(rest, size=k, replace=False).tolist())
        avail_slots[t] = sorted(set(used) | set(extra))
    for i in range(n_sessions):
        forbidden[i] = [s for s in range(SLOTS) if s not in avail_slots[teacher_of[i]]]

    inst = {
        "name": tag,
        "family": "synthetic",
        "source_name": tag,
        "generator": {
            "script": "02_code/generate_instances.py",
            "seed": seed,
            "pattern": pattern,
            "pattern_extra_share": share,
            "n_sessions": n_sessions,
            "n_rooms": n_rooms,
            "n_teachers": n_teachers,
            "n_groups": n_groups,
            "days": DAYS,
            "periods_per_day": PERIODS,
            "capacities": CAPACITIES[:n_rooms],
            "students_range": [15, CAPACITIES[n_rooms - 1]],
            "construction": "base feasible schedule first, constraints added around it",
            "base_attempt": attempt + 1,
        },
        "n_days": DAYS,
        "periods_per_day": PERIODS,
        "n_slots": SLOTS,
        "rooms": rooms,
        "sessions": sessions,
        "teachers": sorted(set(teacher_of)),
        "groups": sorted(set(group_of)),
        "forbidden": forbidden,
        "base_solution": {"room": base_room, "slot": base_slot},
    }
    return inst, base_room, base_slot


def emit(inst: dict, out_dir: Path) -> dict:
    model.save({k: v for k, v in inst.items() if k != "base_solution"}, out_dir / f"{inst['name']}.json")
    brute = model.validate(inst, inst["base_solution"]["room"], inst["base_solution"]["slot"])
    fast = model.Instance({k: v for k, v in inst.items() if k != "base_solution"})
    H, P = fast.score(np.array(inst["base_solution"]["room"]), np.array(inst["base_solution"]["slot"]))
    assert brute["H"] == H, f"validator/scorer mismatch H on {inst['name']}: {brute['H']} vs {H}"
    assert brute["P"] == P, f"validator/scorer mismatch P on {inst['name']}: {brute['P']} vs {P}"
    assert H == 0, f"base schedule not feasible on {inst['name']} (H={H})"
    row = fast.describe()
    row.update({
        "generator_seed": inst["generator"]["seed"],
        "pattern": inst["generator"]["pattern"],
        "availability_share": round(1 - float(fast.forbidden.mean()), 4),
        "base_P": P,
        "base_room_changes": brute["room_changes"],
    })
    return row


def main() -> None:
    out_main = ROOT / "01_data" / "synthetic"
    out_pilot = ROOT / "01_data" / "pilot"
    out_main.mkdir(parents=True, exist_ok=True)
    out_pilot.mkdir(parents=True, exist_ok=True)

    specs = []
    seed = 1000
    for n in (30, 60, 90):
        for pattern in ("A", "B", "C"):
            seed += 1
            specs.append(dict(
                n_sessions=n, n_rooms=n // 15, n_teachers=n // 5, n_groups=n // 6,
                seed=seed, tag=f"syn{n}{pattern}", pattern=pattern,
            ))
    # pilot instances: different size and different seeds, never used for results
    for pattern in ("B", "C"):
        seed += 1
        specs.append(dict(
            n_sessions=45, n_rooms=3, n_teachers=9, n_groups=8,
            seed=seed, tag=f"pilot45{pattern}", pattern=pattern,
        ))

    rows = []
    for spec in specs:
        rng = np.random.default_rng(spec["seed"])
        inst, base_room, base_slot = build(rng, spec["n_sessions"], spec["n_rooms"],
                                           spec["n_teachers"], spec["n_groups"],
                                           spec["seed"], spec["tag"], spec["pattern"])
        target = out_pilot if spec["tag"].startswith("pilot") else out_main
        row = emit(inst, target)
        rows.append(row)
        print(f"{row['name']:12s} sessions={row['sessions']:3d} rooms={row['rooms']:2d} "
              f"fill={row['fill_ratio']:.2f} avail={row['availability_share']:.3f} base_P={row['base_P']}")

    hdr = list(rows[0].keys())
    with open(out_main.parent / "instance_characteristics.csv", "w", encoding="utf-8") as fh:
        fh.write(",".join(hdr) + "\n")
        for r in rows:
            fh.write(",".join(str(r[h]) for h in hdr) + "\n")
    print(f"\n{len(rows)} instance ditulis; karakteristik: {out_main.parent / 'instance_characteristics.csv'}")


if __name__ == "__main__":
    main()
