"""Core model, scorer and independent validator for the course timetabling study.

Unified instance model (see ctt_parser.py docstring):
    instance = {
        "name", "family", "n_days", "periods_per_day", "n_slots",
        "rooms":   [{"id", "capacity"}],
        "sessions":[{"id","course","teacher","groups","students","allowed_rooms"}],
        "teachers","groups",
        "forbidden": [[slot,...] per session],
    }

Objective (lexicographic, pre-registered in 00_config/design_lock.md):
    1. minimise H = number of hard-constraint violations
       H = teacher clashes + room clashes + student-group clashes
           + capacity violations + forbidden-slot (unavailability) uses
    2. among solutions with H = 0, minimise P = preference penalty
       P = total idle slots inside student-group days (class gaps)

Accounting: ONE evaluation = one scoring of a (hard, soft) pair for one
candidate schedule, or one candidate (room, slot) pair probed by repair.
Scorer.spend() therefore charges 1 per call.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np


class Budget:
    """Evaluation budget: one unit per (hard, soft) pair scoring."""

    __slots__ = ("limit", "used")

    def __init__(self, limit: int):
        self.limit = int(limit)
        self.used = 0

    def spend(self, k: int = 1) -> bool:
        if self.used + k > self.limit:
            return False
        self.used += k
        return True

    @property
    def left(self) -> int:
        return self.limit - self.used

    @property
    def exhausted(self) -> bool:
        return self.used >= self.limit


class Instance:
    """Pre-computed index arrays for fast scoring."""

    def __init__(self, data: dict):
        self.data = data
        self.name = data["name"]
        self.family = data.get("family", "unknown")
        self.source_name = data.get("source_name", self.name)
        S = data["n_slots"]
        self.S = S
        self.D = data["n_days"]
        self.P = data["periods_per_day"]
        self.n = len(data["sessions"])
        self.R = len(data["rooms"])

        self.cap = np.array([r["capacity"] for r in data["rooms"]], dtype=np.int32)
        self.students = np.array([s["students"] for s in data["sessions"]], dtype=np.int32)
        teachers = data["teachers"]
        tix = {t: i for i, t in enumerate(teachers)}
        self.teacher_ix = np.array([tix[s["teacher"]] for s in data["sessions"]], dtype=np.int32)
        self.n_teachers = len(teachers)

        groups = data["groups"]
        gix = {g: i for i, g in enumerate(groups)}
        self.n_groups = len(groups)
        p_s, p_g = [], []
        for i, s in enumerate(data["sessions"]):
            for g in s["groups"]:
                p_s.append(i)
                p_g.append(gix[g])
        self.pair_sess = np.array(p_s, dtype=np.int32)
        self.pair_group = np.array(p_g, dtype=np.int32)

        forb = np.zeros((self.n, S), dtype=bool)
        for i, slots in enumerate(data["forbidden"]):
            if slots:
                forb[i, slots] = True
        self.forbidden = forb

        # room use feasibility: capacity + optional allowed-room restriction
        ok = self.cap[None, :] >= self.students[:, None]
        for i, s in enumerate(data["sessions"]):
            allowed = s.get("allowed_rooms") or []
            if allowed:
                keep = np.array([r["id"] in allowed for r in data["rooms"]], dtype=bool)
                ok[i] &= keep
        self.room_ok = ok  # (n, R) bool
        self.room_ok_idx = [np.flatnonzero(ok[i]) for i in range(self.n)]

        # per-course session index (for room-stability reporting)
        courses: dict[str, list[int]] = {}
        for i, s in enumerate(data["sessions"]):
            courses.setdefault(s["course"], []).append(i)
        self.course_sessions = list(courses.values())

    # ---------- scoring ----------
    def hard(self, room: np.ndarray, slot: np.ndarray) -> int:
        S = self.S
        h = 0
        for ix in (self.teacher_ix, room):
            keys = ix.astype(np.int64) * S + slot
            cnt = np.bincount(keys, minlength=(int(ix.max()) + 1) * S)
            h += int((cnt[cnt > 1] - 1).sum())
        keys = self.pair_group.astype(np.int64) * S + slot[self.pair_sess]
        cnt = np.bincount(keys, minlength=self.n_groups * S)
        h += int((cnt[cnt > 1] - 1).sum())
        h += int((self.cap[room] < self.students).sum())
        h += int(self.forbidden[np.arange(self.n), slot].sum())
        return h

    def soft(self, slot: np.ndarray) -> int:
        """Idle slots inside student-group days (class gaps)."""
        S = self.S
        occ = np.zeros(self.n_groups * S, dtype=bool)
        occ[self.pair_group.astype(np.int64) * S + slot[self.pair_sess]] = True
        occ = occ.reshape(self.n_groups, self.D, self.P)
        anyocc = occ.any(axis=2)
        first = occ.argmax(axis=2)
        last = self.P - 1 - occ[:, :, ::-1].argmax(axis=2)
        span = np.where(anyocc, last - first + 1, 0)
        return int((span - occ.sum(axis=2)).sum())

    def room_changes(self, room: np.ndarray) -> int:
        tot = 0
        for idx in self.course_sessions:
            tot += len(set(room[idx].tolist())) - 1
        return tot

    def score(self, room: np.ndarray, slot: np.ndarray) -> tuple[int, int]:
        return self.hard(room, slot), self.soft(slot)

    def violated(self, room: np.ndarray, slot: np.ndarray) -> np.ndarray:
        """Sessions taking part in at least one hard violation (repair targets)."""
        S = self.S
        bad = np.zeros(self.n, dtype=bool)
        for ix in (self.teacher_ix, room):
            keys = ix.astype(np.int64) * S + slot
            cnt = np.bincount(keys, minlength=(int(ix.max()) + 1) * S)
            bad |= cnt[keys] > 1
        keys = self.pair_group.astype(np.int64) * S + slot[self.pair_sess]
        cnt = np.bincount(keys, minlength=self.n_groups * S)
        clash_pair = cnt[keys] > 1
        bad[self.pair_sess[clash_pair]] = True
        bad |= self.cap[room] < self.students
        bad |= self.forbidden[np.arange(self.n), slot]
        return np.flatnonzero(bad)

    def breakdown(self, room: np.ndarray, slot: np.ndarray) -> dict:
        S = self.S
        out = {}
        for tag, ix in (("teacher", self.teacher_ix), ("room", room)):
            keys = ix.astype(np.int64) * S + slot
            cnt = np.bincount(keys, minlength=(int(ix.max()) + 1) * S)
            out[f"H_{tag}"] = int((cnt[cnt > 1] - 1).sum())
        keys = self.pair_group.astype(np.int64) * S + slot[self.pair_sess]
        cnt = np.bincount(keys, minlength=self.n_groups * S)
        out["H_group"] = int((cnt[cnt > 1] - 1).sum())
        out["H_capacity"] = int((self.cap[room] < self.students).sum())
        out["H_forbidden"] = int(self.forbidden[np.arange(self.n), slot].sum())
        out["H"] = sum(v for k, v in out.items() if k.startswith("H_") and k != "H")
        out["P"] = self.soft(slot)
        out["room_changes"] = self.room_changes(room)
        return out

    # ---------- helpers ----------
    def random_gene(self, rng: np.random.Generator, i: int) -> tuple[int, int]:
        r = int(rng.choice(self.room_ok_idx[i]))
        s = int(rng.integers(self.S))
        return r, s

    def describe(self) -> dict:
        d = self.data
        return {
            "name": self.name,
            "family": self.family,
            "source_name": self.source_name,
            "sessions": self.n,
            "rooms": self.R,
            "slots": self.S,
            "days": self.D,
            "periods_per_day": self.P,
            "cells": self.R * self.S,
            "fill_ratio": round(self.n / (self.R * self.S), 4),
            "teachers": self.n_teachers,
            "groups": self.n_groups,
            "forbidden_share": round(float(self.forbidden.mean()), 4),
            "sessions_per_teacher": round(self.n / self.n_teachers, 2),
            "sessions_per_group": round(float(len(self.pair_sess) / max(self.n_groups, 1)), 2),
        }


def load(path: str | Path) -> Instance:
    with open(path, encoding="utf-8") as fh:
        return Instance(json.load(fh))


def save(inst: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(inst, fh, indent=1)


# --------------------------------------------------------------------------
# Independent validator: plain Python, no shared code with the scorer above.
# Used as the validity check required by the brief ("uji validitas satu
# contoh"): it must reproduce H and P of the fast scorer on a produced
# timetable, otherwise every table in the article inherits a silent bug.
# --------------------------------------------------------------------------
def validate(data: dict, room: Sequence[int], slot: Sequence[int]) -> dict:
    sessions = data["sessions"]
    rooms = data["rooms"]
    D, P = data["n_days"], data["periods_per_day"]
    n = len(sessions)
    assert len(room) == n and len(slot) == n, "assignment length mismatch"

    # excess counting: a slot with c sessions of the same teacher costs (c-1),
    # matching the scorer's definition (pairwise counting would over-count).
    t_cnt: dict[tuple[str, int], int] = {}
    r_cnt: dict[tuple[int, int], int] = {}
    g_cnt: dict[tuple[str, int], int] = {}
    cap_viol = forb_viol = 0
    for i in range(n):
        si = int(slot[i])
        ri = int(room[i])
        t_cnt[(sessions[i]["teacher"], si)] = t_cnt.get((sessions[i]["teacher"], si), 0) + 1
        r_cnt[(ri, si)] = r_cnt.get((ri, si), 0) + 1
        for g in sessions[i]["groups"]:
            g_cnt[(g, si)] = g_cnt.get((g, si), 0) + 1
        if rooms[ri]["capacity"] < sessions[i]["students"]:
            cap_viol += 1
        allowed = sessions[i].get("allowed_rooms") or []
        if allowed and rooms[ri]["id"] not in allowed:
            cap_viol += 1
        if si in data["forbidden"][i]:
            forb_viol += 1
    teacher_clash = sum(c - 1 for c in t_cnt.values() if c > 1)
    room_clash = sum(c - 1 for c in r_cnt.values() if c > 1)
    group_clash = sum(c - 1 for c in g_cnt.values() if c > 1)

    groups = data["groups"]
    occ = {g: [set() for _ in range(D)] for g in groups}
    for i in range(n):
        day, per = divmod(slot[i], P)
        for g in sessions[i]["groups"]:
            occ[g][day].add(per)
    gaps = 0
    for g in groups:
        for day in range(D):
            if occ[g][day]:
                gaps += (max(occ[g][day]) - min(occ[g][day]) + 1) - len(occ[g][day])

    changes = 0
    by_course: dict[str, set[int]] = {}
    for i in range(n):
        by_course.setdefault(sessions[i]["course"], set()).add(room[i])
    for c, rr in by_course.items():
        changes += len(rr) - 1

    return {
        "H_teacher": teacher_clash,
        "H_room": room_clash,
        "H_group": group_clash,
        "H_capacity": cap_viol,
        "H_forbidden": forb_viol,
        "H": teacher_clash + room_clash + group_clash + cap_viol + forb_viol,
        "P": gaps,
        "room_changes": changes,
        "feasible": (teacher_clash + room_clash + group_clash + cap_viol + forb_viol) == 0,
    }
