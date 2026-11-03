"""Metode pembanding: greedy konstruktif, GA standar, GA + repair.

Akuntansi evaluasi (dikunci di 00_config/design_lock.md):
  Satu evaluasi = satu penilaian objektif atas satu kandidat:
    (a) penilaian lengkap satu jadwal (fitness individu GA / skor greedy), atau
    (b) satu kandidat perpindahan (ruang, slot) atau tukar-sesi yang diperiksa
        repair.
  Setiap penilaian yang dilakukan algoritma dibebankan; pembangunan indeks
  okupansi (array hitung) adalah pembukuan, bukan penilaian objektif, sehingga
  tidak dibebankan. Baseline greedy menilai pasangan (sesi, ruang, slot) satu
  per satu; jumlah evaluasi sebenarnya dilaporkan dan tidak dipotong budget
  (deterministik, tanpa titik henti setara).

Inisialisasi GA: greedy-seeded (lihat brief: "Greedy-Seeded").
  Individu 0 = greedy most-constrained-first deterministik; individu lain =
  greedy dengan urutan sesi dan tie-break acak. Setiap individu dibayar 1
  evaluasi (skor lengkapnya).

Objektif: leksikografis (H, P)
  H = pelanggaran hard (dosen, ruang, kelompok, kapasitas, slot terlarang)
  P = penalti preferensi (slot kosong di antara jam kuliah kelompok per hari)
"""

from __future__ import annotations

import time

import numpy as np

import model


# --------------------------------------------------------------------------
# Greedy konstruktif
# --------------------------------------------------------------------------
def _greedy_assignment(inst: model.Instance, rng: np.random.Generator | None = None,
                       mode: str = "det"):
    """Bangun penugasan rakus. mode: 'det' | 'rand'. Dibayar oleh pemanggil."""
    n, S, P = inst.n, inst.S, inst.P
    occ_t: dict[tuple[int, int], int] = {}
    occ_r: dict[tuple[int, int], int] = {}
    occ_g: dict[tuple[int, int], int] = {}
    gday: dict[tuple[int, int], set[int]] = {}
    room = np.full(n, -1, dtype=np.int32)
    slot = np.full(n, -1, dtype=np.int32)

    def gaps_of(g: int, d: int) -> int:
        s = gday.get((g, d))
        if not s:
            return 0
        return (max(s) - min(s) + 1) - len(s)

    order = list(range(n))
    if mode == "rand" and rng is not None:
        rng.shuffle(order)
    else:
        # most-constrained-first: ketersediaan dosen ketat, lalu ruang kompatibel
        order.sort(key=lambda i: (int(inst.forbidden[i].sum()), len(inst.room_ok_idx[i])))

    for i in order:
        t = int(inst.teacher_ix[i])
        groups = [int(g) for g in inst.pair_group[inst.pair_sess == i]]
        best = None
        for r in inst.room_ok_idx[i]:
            for s in range(S):
                d, per = divmod(s, P)
                dH = 0
                if occ_t.get((t, s), 0):
                    dH += 1
                if occ_r.get((int(r), s), 0):
                    dH += 1
                if inst.forbidden[i, s]:
                    dH += 1
                dP = 0
                for g in groups:
                    if occ_g.get((g, s), 0):
                        dH += 1
                    before = gaps_of(g, d)
                    cur = gday.setdefault((g, d), set())
                    cur.add(per)
                    dP += (max(cur) - min(cur) + 1) - len(cur) - before
                    cur.discard(per)
                jitter = rng.random() if (mode == "rand" and rng is not None) else 0.0
                key = (dH, dP, jitter, int(r), s)
                if best is None or key < best[0]:
                    best = (key, int(r), s)
        if best is None:  # tidak mungkin pada instance yang dipakai
            r, s = inst.random_gene(np.random.default_rng(0), i)
        else:
            _, r, s = best
        room[i], slot[i] = r, s
        occ_t[(t, s)] = occ_t.get((t, s), 0) + 1
        occ_r[(r, s)] = occ_r.get((r, s), 0) + 1
        for g in groups:
            occ_g[(g, s)] = occ_g.get((g, s), 0) + 1
            gday.setdefault((g, divmod(s, P)[0]), set()).add(divmod(s, P)[1])
    return room, slot


def _greedy_probes(inst: model.Instance) -> int:
    """Jumlah pasangan (sesi, ruang, slot) yang benar-benar dinilai greedy."""
    total = 0
    order = sorted(range(inst.n), key=lambda i: (int(inst.forbidden[i].sum()),
                                                 len(inst.room_ok_idx[i])))
    for i in order:
        total += len(inst.room_ok_idx[i]) * inst.S
    return total


def run_greedy(inst: model.Instance, cfg: dict) -> dict:
    t0 = time.perf_counter()
    room, slot = _greedy_assignment(inst, None, "det")
    H, Pm = inst.score(room, slot)
    check = model.validate(inst.data, room.tolist(), slot.tolist())
    evals = _greedy_probes(inst)
    return {
        "method": "greedy",
        "seed": -1,
        "room": room,
        "slot": slot,
        "best_H": H,
        "best_P": Pm,
        "feasible": H == 0,
        "evals": evals,
        "evals_to_first_feasible": evals if H == 0 else None,
        "repair_probes": 0,
        "repair_failures": 0,
        "repair_sessions": 0,
        "repair_swaps": 0,
        "budget_limited": 0,
        "runtime_s": round(time.perf_counter() - t0, 4),
        "trace": [(evals, H, Pm)],
        "generations": 0,
        "validated_H": check["H"],
        "validated_P": check["P"],
        "room_changes": check["room_changes"],
    }


# --------------------------------------------------------------------------
# Operator GA
# --------------------------------------------------------------------------
def _tournament(fits: list[tuple[int, int]], rng: np.random.Generator, k: int = 3) -> int:
    idx = rng.integers(len(fits), size=k)
    best = int(idx[0])
    for j in idx[1:]:
        j = int(j)
        if fits[j] < fits[best]:
            best = j
    return best


def _crossover(p1, p2, rng: np.random.Generator):
    mask = rng.random(len(p1[0])) < 0.5
    room = np.where(mask, p1[0], p2[0]).astype(np.int32)
    slot = np.where(mask, p1[1], p2[1]).astype(np.int32)
    return room, slot


def _mutate(room, slot, inst: model.Instance, rng: np.random.Generator, pm: float) -> None:
    """Mutasi per gen: ganti slot, atau ganti ruang, atau keduanya."""
    for i in np.flatnonzero(rng.random(len(room)) < pm):
        i = int(i)
        u = rng.random()
        if u < 0.45:
            slot[i] = int(rng.integers(inst.S))
        elif u < 0.90:
            room[i] = int(rng.choice(inst.room_ok_idx[i]))
        else:
            room[i], slot[i] = inst.random_gene(rng, i)


# --------------------------------------------------------------------------
# Repair: pindahkan sesi bermasalah ke pasangan (ruang, slot) valid dengan
# tambahan penalti terkecil; bila tidak ada slot bebas, coba tukar sesi.
# Setiap kandidat yang diperiksa = 1 evaluasi.
# --------------------------------------------------------------------------
class _Occupancy:
    def __init__(self, inst: model.Instance, room: np.ndarray, slot: np.ndarray):
        self.inst = inst
        self.t = np.zeros((inst.n_teachers, inst.S), dtype=np.int32)
        self.r = np.zeros((inst.R, inst.S), dtype=np.int32)
        self.g = np.zeros((inst.n_groups, inst.S), dtype=np.int32)
        self.gocc = np.zeros((inst.n_groups, inst.D, inst.P), dtype=bool)
        np.add.at(self.t, (inst.teacher_ix, slot), 1)
        np.add.at(self.r, (room, slot), 1)
        np.add.at(self.g, (inst.pair_group, slot[inst.pair_sess]), 1)
        days, pers = slot[inst.pair_sess] // inst.P, slot[inst.pair_sess] % inst.P
        self.gocc[inst.pair_group, days, pers] = True

    def gaps(self, g: int, d: int) -> int:
        row = self.gocc[g, d]
        if not row.any():
            return 0
        idx = np.flatnonzero(row)
        return int(idx[-1] - idx[0] + 1 - len(idx))

    def groups_of(self, i: int):
        return inst_pair_group(self.inst, i)

    def remove(self, i: int, room, slot) -> None:
        s, r = int(slot[i]), int(room[i])
        inst = self.inst
        self.t[inst.teacher_ix[i], s] -= 1
        self.r[r, s] -= 1
        gs = inst.pair_group[inst.pair_sess == i]
        self.g[gs, s] -= 1
        d, p = divmod(s, inst.P)
        for g in gs:
            if self.g[int(g), s] == 0:
                self.gocc[int(g), d, p] = False

    def add(self, i: int, room, slot) -> None:
        s, r = int(slot[i]), int(room[i])
        inst = self.inst
        self.t[inst.teacher_ix[i], s] += 1
        self.r[r, s] += 1
        gs = inst.pair_group[inst.pair_sess == i]
        self.g[gs, s] += 1
        d, p = divmod(s, inst.P)
        for g in gs:
            self.gocc[int(g), d, p] = True


def inst_pair_group(inst: model.Instance, i: int):
    return inst.pair_group[inst.pair_sess == i]


def _session_violations(inst: model.Instance, occ: _Occupancy, room, slot, i: int) -> int:
    s, r = int(slot[i]), int(room[i])
    c = int(occ.t[inst.teacher_ix[i], s]) - 1 + int(occ.r[r, s]) - 1
    for g in inst_pair_group(inst, i):
        c += int(occ.g[int(g), s]) - 1
    c += int(inst.cap[r] < inst.students[i])
    c += int(inst.forbidden[i, s])
    return c


def _slot_free_for(inst: model.Instance, occ: _Occupancy, i: int, r: int, s: int) -> bool:
    """True bila sesi i dapat ditempatkan di (r, s) tanpa pelanggaran hard."""
    if int(occ.t[inst.teacher_ix[i], s]) > 0:
        return False
    if int(occ.r[r, s]) > 0:
        return False
    for g in inst_pair_group(inst, i):
        if int(occ.g[int(g), s]) > 0:
            return False
    if int(inst.cap[r]) < int(inst.students[i]):
        return False
    if inst.forbidden[i, s]:
        return False
    return True


def _repair_by_swap(inst: model.Instance, occ: _Occupancy, room, slot, i: int,
                    rng: np.random.Generator, budget: model.Budget, swaps: int,
                    stats: dict) -> bool:
    """Tidak ada slot bebas: coba tukar sesi i dengan sesi lain (ejection).

    occ sudah dalam keadaan tanpa sesi i; setiap sesi lain yang diperiksa
    dihitung satu evaluasi.
    """
    best = None
    for _ in range(swaps):
        if budget.left <= 0:
            stats["budget_limited"] += 1
            break
        j = int(rng.integers(inst.n))
        if j == i:
            continue
        rj, sj = int(room[j]), int(slot[j])
        if rj == int(room[i]) and sj == int(slot[i]):
            continue
        if not budget.spend():
            break
        stats["probes"] += 1
        occ.remove(j, room, slot)
        ok_i = _slot_free_for(inst, occ, i, rj, sj)
        ok_j = _slot_free_for(inst, occ, j, int(room[i]), int(slot[i]))
        if ok_i and ok_j:
            di, pi = divmod(sj, inst.P)
            dj, pj = divmod(int(slot[i]), inst.P)
            delta = 0
            for g in inst_pair_group(inst, i):
                g = int(g)
                before = occ.gaps(g, di)
                occ.gocc[g, di, pi] = True
                delta += occ.gaps(g, di) - before
                occ.gocc[g, di, pi] = False
            for g in inst_pair_group(inst, j):
                g = int(g)
                before = occ.gaps(g, dj)
                occ.gocc[g, dj, pj] = True
                delta += occ.gaps(g, dj) - before
                occ.gocc[g, dj, pj] = False
            if best is None or delta < best[0]:
                best = (delta, j)
        occ.add(j, room, slot)
    if best is None:
        occ.add(i, room, slot)
        stats["failures"] += 1
        return False
    j = best[1]
    occ.remove(j, room, slot)
    ri, si = int(room[i]), int(slot[i])
    room[i], slot[i] = int(room[j]), int(slot[j])
    room[j], slot[j] = ri, si
    occ.add(i, room, slot)
    occ.add(j, room, slot)
    stats["sessions"] += 1
    stats["swaps"] += 1
    return True


def _repair(inst: model.Instance, room, slot, rng: np.random.Generator,
            budget: model.Budget, cfg: dict, stats: dict) -> None:
    occ = _Occupancy(inst, room, slot)
    viol = [i for i in range(inst.n) if _session_violations(inst, occ, room, slot, i) > 0]
    if not viol:
        return
    rng.shuffle(viol)
    max_sessions = int(cfg["repair_max_sessions"])
    attempts = int(cfg["repair_attempts"])
    swaps = int(cfg.get("swap_attempts", 0))
    for i in viol[:max_sessions]:
        if budget.left <= 0:
            stats["budget_limited"] += 1
            return
        occ.remove(i, room, slot)
        blocked = occ.t[inst.teacher_ix[i]] > 0
        gs = [int(g) for g in inst_pair_group(inst, i)]
        for g in gs:
            blocked |= occ.g[g] > 0
        free_rooms = occ.r == 0  # (R, S)
        cap_ok = inst.room_ok[i]
        cand_slots = [s for s in range(inst.S)
                      if not blocked[s] and not inst.forbidden[i, s]
                      and cap_ok[free_rooms[:, s]].any()]
        if not cand_slots:
            if swaps and _repair_by_swap(inst, occ, room, slot, i, rng, budget, swaps, stats):
                continue
            occ.add(i, room, slot)
            stats["failures"] += 1
            continue
        pick = rng.choice(len(cand_slots), size=min(attempts, len(cand_slots)), replace=False)
        best = None
        for k in pick:
            s = cand_slots[int(k)]
            if not budget.spend():
                break
            stats["probes"] += 1
            d, _ = divmod(s, inst.P)
            delta = 0
            for g in gs:  # perubahan jumlah jeda kelompok pada hari tujuan
                before = occ.gaps(g, d)
                occ.gocc[g, d, s % inst.P] = True
                delta += occ.gaps(g, d) - before
                occ.gocc[g, d, s % inst.P] = False
            rooms_free = [int(r) for r in np.flatnonzero(cap_ok & free_rooms[:, s])]
            r = min(rooms_free, key=lambda rr: int(inst.cap[rr]))  # best-fit capacity
            key = (delta, int(inst.cap[r]) - int(inst.students[i]), r, s)
            if best is None or key < best[0]:
                best = (key, r, s)
        if best is None:
            occ.add(i, room, slot)
            stats["budget_limited"] += 1
            return
        _, r, s = best
        room[i], slot[i] = r, s
        occ.add(i, room, slot)
        stats["sessions"] += 1


# --------------------------------------------------------------------------
# GA (greedy-seeded, budget-aware)
# --------------------------------------------------------------------------
def run_ga(inst: model.Instance, seed: int, cfg: dict, repair_on: bool,
           method_name: str) -> dict:
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    budget = model.Budget(cfg["budget"])
    stats = {"probes": 0, "failures": 0, "budget_limited": 0, "sessions": 0, "swaps": 0}
    popsize = cfg["pop_size"]
    trace: list[tuple[int, int, int]] = []

    pop, fits = [], []
    first_feasible = None
    best_fit = (10 ** 9, 10 ** 9)
    best_ind = None

    # inisialisasi: greedy-seeded (default) atau acak (ablation)
    seed_mode = cfg.get("seed_mode", "greedy")
    for k in range(popsize):
        if not budget.spend():
            break
        if seed_mode == "random":
            room = np.empty(inst.n, dtype=np.int32)
            slot = np.empty(inst.n, dtype=np.int32)
            for i in range(inst.n):
                room[i], slot[i] = inst.random_gene(rng, i)
        else:
            room, slot = _greedy_assignment(inst, rng, "det" if k == 0 else "rand")
        fit = inst.score(room, slot)
        pop.append((room, slot))
        fits.append(fit)
        if fit < best_fit:
            best_fit, best_ind = fit, (room.copy(), slot.copy())
        if first_feasible is None and fit[0] == 0:
            first_feasible = budget.used

    generations = 0
    while budget.left > 0:
        order = sorted(range(len(fits)), key=lambda k: fits[k])
        new_pop = [(pop[j][0].copy(), pop[j][1].copy()) for j in order[: cfg["elitism"]]]
        new_fits = [fits[j] for j in order[: cfg["elitism"]]]
        while len(new_pop) < popsize and budget.left > 0:
            if rng.random() < cfg["pc"]:
                p1 = pop[_tournament(fits, rng)]
                p2 = pop[_tournament(fits, rng)]
                room, slot = _crossover(p1, p2, rng)
            else:
                src = pop[_tournament(fits, rng)]
                room, slot = src[0].copy(), src[1].copy()
            _mutate(room, slot, inst, rng, cfg["pm"])
            if repair_on:
                _repair(inst, room, slot, rng, budget, cfg, stats)
            if not budget.spend():
                break
            fit = inst.score(room, slot)
            new_pop.append((room, slot))
            new_fits.append(fit)
            if fit < best_fit:
                best_fit, best_ind = fit, (room.copy(), slot.copy())
            if first_feasible is None and fit[0] == 0:
                first_feasible = budget.used
        if len(new_pop) <= cfg["elitism"]:
            break
        pop, fits = new_pop, new_fits
        generations += 1
        trace.append((budget.used, best_fit[0], best_fit[1]))

    room, slot = best_ind
    check = model.validate(inst.data, room.tolist(), slot.tolist())
    return {
        "method": method_name,
        "seed": seed,
        "room": room,
        "slot": slot,
        "best_H": int(best_fit[0]),
        "best_P": int(best_fit[1]),
        "feasible": int(best_fit[0]) == 0,
        "evals": budget.used,
        "evals_to_first_feasible": first_feasible,
        "repair_probes": stats["probes"],
        "repair_sessions": stats["sessions"],
        "repair_swaps": stats["swaps"],
        "repair_failures": stats["failures"],
        "budget_limited": stats["budget_limited"],
        "runtime_s": round(time.perf_counter() - t0, 4),
        "trace": trace,
        "generations": generations,
        "validated_H": check["H"],
        "validated_P": check["P"],
        "room_changes": check["room_changes"],
    }


DEFAULT_CFG = {
    "budget": 10000,
    "pop_size": 50,
    "pc": 0.8,
    "pm": 0.05,
    "elitism": 2,
    "repair_attempts": 3,
    "repair_max_sessions": 20,
    "swap_attempts": 3,
    "seed_mode": "greedy",
}
