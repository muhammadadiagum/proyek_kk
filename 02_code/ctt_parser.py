"""Parser instance Curriculum-Based Course Timetabling (ITC2007) -> model internal.

Format .ctt (ITC2007 Track 2):
    Name / Courses / Rooms / Days / Periods_per_day / Curricula / Constraints
    COURSES:              <id> <teacher> <lectures> <minWorkingDays> <students> [<nrooms> <room..>]
    ROOMS:                <id> <capacity>
    CURRICULA:            <id> <ncourses> <course..>
    UNAVAILABILITY_CONSTRAINTS: <course> <day> <period>
    END.

Model internal dipakai bersama oleh instance benchmark dan instance sintetis:
    {
      "name", "family": "benchmark"|"synthetic",
      "n_days", "periods_per_day", "n_slots",
      "rooms": [{"id", "capacity"}],
      "sessions": [{"id", "course", "teacher", "groups": [gid], "students"}],
      "teachers": [tid], "groups": [gid],
      "forbidden": [[slot, ...] per session]   # slot terlarang utk sesi (unavailability)
    }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def parse_ctt(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = [ln.rstrip() for ln in text.splitlines()]
    header: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    current = None
    for raw in lines:
        ln = raw.strip()
        if not ln:
            continue
        if ln.upper() == "END.":
            break
        if ln.endswith(":") and not ln.upper().startswith(("COURSE", "ROOM", "CURRIC", "UNAVAIL")):
            current = None
            continue
        key, sep, val = ln.partition(":")
        if sep and key.strip() in {
            "Name", "Courses", "Rooms", "Days", "Periods_per_day",
            "Curricula", "Constraints", "Courses", "Rooms",
        }:
            header[key.strip()] = val.strip()
            current = None
            continue
        if key.strip() in {"COURSES", "ROOMS", "CURRICULA", "UNAVAILABILITY_CONSTRAINTS"}:
            current = key.strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(ln)

    n_days = int(header["Days"])
    per_day = int(header["Periods_per_day"])
    n_slots = n_days * per_day

    rooms = []
    for ln in sections.get("ROOMS", []):
        rid, cap = ln.split()[:2]
        rooms.append({"id": rid, "capacity": int(cap)})

    courses = {}
    for ln in sections.get("COURSES", []):
        parts = ln.split()
        cid, teacher, lectures, min_wd, students = parts[0], parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        allowed_rooms = parts[6:] if len(parts) > 6 else []
        courses[cid] = {
            "teacher": teacher,
            "lectures": lectures,
            "min_working_days": min_wd,
            "students": students,
            "allowed_rooms": allowed_rooms,
        }

    curricula = {}
    for ln in sections.get("CURRICULA", []):
        parts = ln.split()
        curricula[parts[0]] = parts[2:]

    course_groups: dict[str, list[str]] = {c: [] for c in courses}
    for gid, members in curricula.items():
        for c in members:
            course_groups.setdefault(c, []).append(gid)

    sessions = []
    for cid, c in courses.items():
        for k in range(c["lectures"]):
            sessions.append({
                "id": f"{cid}#{k + 1}",
                "course": cid,
                "teacher": c["teacher"],
                "groups": list(course_groups.get(cid, [])),
                "students": c["students"],
                "allowed_rooms": list(c["allowed_rooms"]),
            })

    forbidden = [[] for _ in sessions]
    for ln in sections.get("UNAVAILABILITY_CONSTRAINTS", []):
        cid, day, period = ln.split()[:3]
        slot = int(day) * per_day + int(period)
        for i, s in enumerate(sessions):
            if s["course"] == cid:
                forbidden[i].append(slot)

    teachers = sorted({s["teacher"] for s in sessions})
    groups = sorted({g for s in sessions for g in s["groups"]})
    return {
        "name": path.stem,
        "family": "benchmark",
        "source_name": header.get("Name", path.stem),
        "n_days": n_days,
        "periods_per_day": per_day,
        "n_slots": n_slots,
        "rooms": rooms,
        "sessions": sessions,
        "teachers": teachers,
        "groups": groups,
        "forbidden": forbidden,
    }


def stats(inst: dict) -> dict:
    n_s = len(inst["sessions"])
    return {
        "name": inst["name"],
        "source_name": inst.get("source_name", inst["name"]),
        "sessions": n_s,
        "rooms": len(inst["rooms"]),
        "slots": inst["n_slots"],
        "cells": len(inst["rooms"]) * inst["n_slots"],
        "fill_ratio": round(n_s / (len(inst["rooms"]) * inst["n_slots"]), 3),
        "teachers": len(inst["teachers"]),
        "groups": len(inst["groups"]),
        "unavail_total": sum(len(f) for f in inst["forbidden"]),
        "unavail_mean_per_session": round(sum(len(f) for f in inst["forbidden"]) / max(n_s, 1), 2),
        "min_capacity": min(r["capacity"] for r in inst["rooms"]),
        "max_capacity": max(r["capacity"] for r in inst["rooms"]),
        "students_max": max(s["students"] for s in inst["sessions"]),
        "cap_ok_all": all(any(r["capacity"] >= s["students"] for r in inst["rooms"]) for s in inst["sessions"]),
    }


if __name__ == "__main__":
    src_dir = Path(sys.argv[1])
    rows = []
    for p in sorted(src_dir.glob("*.ctt")):
        inst = parse_ctt(p)
        rows.append(stats(inst))
    hdr = list(rows[0].keys())
    print(",".join(hdr))
    for r in rows:
        print(",".join(str(r[h]) for h in hdr))
