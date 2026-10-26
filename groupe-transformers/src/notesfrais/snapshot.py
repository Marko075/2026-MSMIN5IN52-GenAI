"""État observable d'un run, calculé depuis le journal et le registre des effets.

Le même instantané alimente le tableau de bord en direct et le replay (il est enregistré pendant la
campagne dans `snapshots.jsonl`), ce qui permet de rejouer une démo sans rien exécuter.
"""
from __future__ import annotations

import time
from pathlib import Path

import psutil

from . import STEPS, TERMINAL_STATUSES
from .chaos import current_worker_pid
from .journal import read_journal
from .metrics import duplicate_effects, effect_counts, percentile, recovery_times

STEP_CODES = {"run": "r", "done": "d", "fail": "f"}
LOG_EVENTS = {"chaos_kill", "manual_kill", "crash_point", "worker_spawned", "worker_crashed", "request_resumed",
              "duplicate_ignored", "idempotent_replay", "effect_applied", "fault_injected", "retry",
              "llm_cache_hit", "request_final", "permanent_error", "step_failed", "worker_exited"}


def snapshot(run_dir: Path, mode: str | None = None) -> dict:
    run_dir = Path(run_dir)
    events = read_journal(run_dir)
    requests: dict[str, dict] = {}
    kills = crash_points = faults = 0
    for e in events:
        ev = e.get("event")
        rid = e.get("request_id")
        mode = mode or e.get("mode")
        if ev in ("chaos_kill", "manual_kill"):
            kills += 1
        elif ev == "crash_point":
            crash_points += 1
        elif ev == "fault_injected":
            faults += 1
        if rid is None:
            continue
        entry = requests.setdefault(rid, {"steps": {}, "status": None, "runs": 0, "resumed": 0})
        if ev == "request_start":
            entry["steps"] = {}
            entry["status"] = None
            entry["runs"] += 1
        elif ev == "request_resumed":
            entry["resumed"] += 1
        elif ev == "step_start":
            entry["steps"][e["step"]] = "run"
        elif ev == "step_done":
            entry["steps"][e["step"]] = "done"
        elif ev == "step_failed":
            entry["steps"][e["step"]] = "fail"
        elif ev == "request_final":
            entry["status"] = e.get("status")
    counts = effect_counts(run_dir) if (run_dir / "services.db").exists() else {}
    dup = duplicate_effects(counts)
    rec = recovery_times(events)
    compact = {}
    for rid, entry in sorted(requests.items()):
        if entry["runs"] == 0 and entry["status"] is None and not entry["steps"]:
            continue
        codes = "".join(STEP_CODES.get(entry["steps"].get(s), ".") for s in STEPS + ["compensation"])
        compact[rid] = {"s": codes, "st": entry["status"], "n": entry["runs"], "rs": entry["resumed"],
                        "dup": rid in dup["requests"]}
    finished = sum(1 for r in compact.values() if r["st"] in TERMINAL_STATUSES)
    pid = current_worker_pid(run_dir)
    log = [
        {k: e.get(k) for k in ("ts", "event", "request_id", "step", "status", "fault", "kind", "attempt",
                               "worker_pid", "point", "error") if e.get(k) is not None}
        for e in events if e.get("event") in LOG_EVENTS
    ][-40:]
    return {
        "t": time.time(),
        "mode": mode,
        "worker_alive": bool(pid and psutil.pid_exists(pid)),
        "finished": any(e.get("event") in ("worker_exited", "supervisor_stop") for e in events[-5:]),
        "counters": {
            "terminees": finished,
            "en_cours": sum(1 for r in compact.values() if r["st"] not in TERMINAL_STATUSES),
            "pannes_injectees": kills + crash_points + faults,
            "kills": kills + crash_points,
            "effets_en_double": dup["total"],
            "compensations": sum(1 for r in compact.values() if r["st"] == "COMPENSATED"),
            "reprise_p50_s": percentile(rec, 50),
            "reprise_p95_s": percentile(rec, 95),
            "paiements": sum(c["payment"] for c in counts.values()),
        },
        "requests": compact,
        "log": log,
    }
