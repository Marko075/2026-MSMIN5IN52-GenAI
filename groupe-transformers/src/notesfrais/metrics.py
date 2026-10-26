"""Mesures d'un run : complétion, effets dupliqués, incohérences, compensations, temps de reprise."""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from pathlib import Path

from . import TERMINAL_STATUSES
from .db import connect, services_db, workflow_db
from .journal import read_journal

CRASH_EVENTS = ("chaos_kill", "manual_kill", "crash_point")


def final_statuses(run_dir: Path, mode: str) -> dict[str, str]:
    conn = workflow_db(run_dir)
    try:
        if mode == "protected":
            rows = conn.execute("SELECT request_id, status FROM requests").fetchall()
            return {r["request_id"]: r["status"] for r in rows}
        rows = conn.execute("SELECT request_id, outcome FROM inbox WHERE acked_at IS NOT NULL ORDER BY acked_at").fetchall()
        return {r["request_id"]: r["outcome"] for r in rows}
    finally:
        conn.close()


def effect_counts(run_dir: Path) -> dict[str, Counter]:
    path = Path(run_dir) / "services.db"
    # Lecture seule : pas de script de schéma (donc pas d'écriture) quand la base existe déjà.
    conn = connect(path) if path.exists() else services_db(run_dir)
    try:
        counts: dict[str, Counter] = defaultdict(Counter)
        for r in conn.execute("SELECT request_id, kind, COUNT(*) AS n FROM effects GROUP BY request_id, kind"):
            counts[r["request_id"]][r["kind"]] = r["n"]
        return counts
    finally:
        conn.close()


def duplicate_effects(counts: dict[str, Counter]) -> dict:
    by_kind = Counter()
    requests = set()
    for rid, kinds in counts.items():
        for kind, n in kinds.items():
            if n > 1:
                by_kind[kind] += n - 1
                requests.add(rid)
    return {"total": sum(by_kind.values()), "by_kind": dict(by_kind), "requests": sorted(requests)}


def inconsistencies(statuses: dict[str, str], counts: dict[str, Counter]) -> list[str]:
    """Une demande est cohérente si ses effets nets correspondent à son statut final."""
    bad = []
    for rid in set(statuses) | set(counts):
        c = counts.get(rid, Counter())
        net = c["payment"] - c["refund"]
        status = statuses.get(rid)
        ok = {
            "DONE": net == 1 and c["email"] == 1,
            "REJECTED": net == 0,
            "COMPENSATED": c["payment"] == 1 and net == 0 and c["refund"] == 1,
            "FAILED": net == 0,
        }.get(status, net == 0 and c["email"] == 0)
        if not ok:
            bad.append(rid)
    return sorted(bad)


def crash_moments(events: list[dict]) -> list[tuple[float, int]]:
    out = []
    for e in events:
        if e.get("event") in ("chaos_kill", "manual_kill"):
            out.append((e.get("kill_ts", e["ts"]), e.get("worker_pid")))
        elif e.get("event") == "crash_point":
            out.append((e["ts"], e.get("pid")))
    return out


def recovery_times(events: list[dict]) -> list[float]:
    """Temps entre un crash et la première étape terminée par le worker relancé."""
    done = [(e["ts"], e.get("pid")) for e in events if e.get("event") == "step_done" and e.get("source") == "worker"]
    times = []
    for t_crash, pid in crash_moments(events):
        nxt = next((ts for ts, p in done if ts > t_crash and p != pid), None)
        if nxt is not None:
            times.append(nxt - t_crash)
    return times


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round(q / 100 * (len(values) - 1))))
    return values[idx]


def compute_metrics(run_dir: Path, mode: str) -> dict:
    run_dir = Path(run_dir)
    events = read_journal(run_dir)
    statuses = final_statuses(run_dir, mode)
    counts = effect_counts(run_dir)
    conn = workflow_db(run_dir)
    n_messages = conn.execute("SELECT COUNT(*) FROM inbox").fetchone()[0]
    submitted = [r[0] for r in conn.execute("SELECT DISTINCT request_id FROM inbox")]
    conn.close()
    ev = Counter(e.get("event") for e in events)
    llm_faults = ev["llm_invalid_output"] + sum(
        1 for e in events if e.get("event") == "retry" and e.get("step") == "extraction")
    kills = ev["chaos_kill"] + ev["manual_kill"]
    terminal = [rid for rid in submitted if statuses.get(rid) in TERMINAL_STATUSES]
    rec = recovery_times(events)
    steps_done = Counter((e.get("request_id"), e.get("step")) for e in events if e.get("event") == "step_done")
    dup = duplicate_effects(counts)
    ts = [e["ts"] for e in events if "ts" in e]
    return {
        "mode": mode,
        "run": run_dir.name,
        "requests": len(submitted),
        "messages": n_messages,
        "completed": len(terminal),
        "completion_rate": round(len(terminal) / len(submitted), 4) if submitted else 0.0,
        "statuses": dict(Counter(statuses.get(rid, "EN_COURS") for rid in submitted)),
        "duplicate_effects": dup["total"],
        "duplicate_by_kind": dup["by_kind"],
        "requests_with_duplicates": len(dup["requests"]),
        "inconsistent_requests": len(inconsistencies({r: statuses.get(r) for r in submitted}, counts)),
        "compensations": sum(1 for rid in submitted if statuses.get(rid) == "COMPENSATED"),
        "payments": sum(c["payment"] for c in counts.values()),
        "refunds": sum(c["refund"] for c in counts.values()),
        "emails": sum(c["email"] for c in counts.values()),
        "faults": {
            "worker_kills": kills,
            "crash_points": ev["crash_point"],
            "service_faults": ev["fault_injected"],
            "llm_faults": llm_faults,
            "duplicate_deliveries": n_messages - len(submitted),
        },
        "crashes": kills + ev["crash_point"],
        "faults_total": kills + ev["crash_point"] + ev["fault_injected"] + llm_faults + n_messages - len(submitted),
        "retries": ev["retry"],
        "idempotent_replays": ev["idempotent_replay"],
        "duplicates_ignored": ev["duplicate_ignored"],
        "llm_calls": ev["llm_call"],
        "llm_cache_hits": ev["llm_cache_hit"],
        "steps_replayed": sum(n - 1 for n in steps_done.values() if n > 1),
        "recovery_s": {
            "n": len(rec),
            "p50": percentile(rec, 50),
            "p95": percentile(rec, 95),
            "mean": round(statistics.mean(rec), 4) if rec else None,
        },
        "recovery_samples": [round(x, 4) for x in rec],
        "duration_s": round(max(ts) - min(ts), 2) if ts else 0.0,
    }
