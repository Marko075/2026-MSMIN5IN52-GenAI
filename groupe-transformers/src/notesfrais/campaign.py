"""Campagne d'injection de pannes : modes naïf et protégé, plusieurs seeds, mesures agrégées."""
from __future__ import annotations

import csv
import json
import shutil
import statistics
import threading
import time
from pathlib import Path
from typing import Callable

from .chaos import ChaosMonkey
from .config import RESULTS_DIR, RUNS_DIR, RunConfig
from .dataset import build_messages, load_requests, submit
from .db import init_run_dbs
from .journal import Journal
from .metrics import compute_metrics, percentile
from .snapshot import snapshot
from .supervisor import Supervisor


def prepare_run(run_dir: Path, cfg: RunConfig, n_requests: int = 40, dup_rate: float = 0.15,
                requests: list[dict] | None = None) -> int:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    cfg.save(run_dir)
    init_run_dbs(run_dir)
    requests = requests if requests is not None else load_requests()[:n_requests]
    return submit(run_dir, build_messages(requests, cfg.seed, dup_rate))


def run_one(run_dir: Path, cfg: RunConfig, n_requests: int = 40, dup_rate: float = 0.15,
            kill_interval: tuple[float, float] | None = (0.3, 1.2), timeout: float = 600,
            on_snapshot: Callable[[dict], None] | None = None, snapshot_every: float = 0.5) -> dict:
    run_dir = Path(run_dir)
    n_messages = prepare_run(run_dir, cfg, n_requests, dup_rate)
    journal = Journal(run_dir, "supervisor", mode=cfg.mode)
    journal.write("campaign_start", seed=cfg.seed, messages=n_messages, kill_interval=kill_interval)
    supervisor = Supervisor(run_dir, journal)
    chaos = ChaosMonkey(run_dir, cfg.seed, kill_interval, Journal(run_dir, "chaos", mode=cfg.mode)) if kill_interval else None

    stop = threading.Event()

    def progress() -> None:
        """Transmet l'état courant à `on_snapshot` (barre de progression de la démo)."""
        while True:
            try:
                on_snapshot(snapshot(run_dir, cfg.mode))
            except Exception:  # noqa: BLE001 - une lecture ratée ne doit pas interrompre l'affichage
                pass
            if stop.wait(snapshot_every):
                on_snapshot(snapshot(run_dir, cfg.mode))
                return

    reporter = threading.Thread(target=progress, daemon=True) if on_snapshot is not None else None
    if reporter:
        reporter.start()
    if chaos:
        chaos.start()
    result = supervisor.run(timeout=timeout)
    if chaos:
        chaos.stop()
        chaos.join(timeout=5)
    stop.set()
    if reporter:
        reporter.join(timeout=10)
    metrics = compute_metrics(run_dir, cfg.mode)
    metrics["supervisor"] = result
    metrics["seed"] = cfg.seed
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return metrics


def aggregate(runs: list[dict]) -> dict:
    out = {}
    for mode in sorted({r["mode"] for r in runs}):
        rs = [r for r in runs if r["mode"] == mode]
        rec = [x for r in rs for x in r["recovery_samples"]]
        out[mode] = {
            "runs": len(rs),
            "requests": sum(r["requests"] for r in rs),
            "completion_rate": round(statistics.mean(r["completion_rate"] for r in rs), 4),
            "duplicate_effects": sum(r["duplicate_effects"] for r in rs),
            "requests_with_duplicates": sum(r["requests_with_duplicates"] for r in rs),
            "inconsistent_requests": sum(r["inconsistent_requests"] for r in rs),
            "compensations": sum(r["compensations"] for r in rs),
            "crashes": sum(r["crashes"] for r in rs),
            "faults_total": sum(r["faults_total"] for r in rs),
            "faults": {k: sum(r["faults"][k] for r in rs) for k in rs[0]["faults"]},
            "llm_calls": sum(r["llm_calls"] for r in rs),
            "llm_cache_hits": sum(r["llm_cache_hits"] for r in rs),
            "steps_replayed": sum(r["steps_replayed"] for r in rs),
            "idempotent_replays": sum(r["idempotent_replays"] for r in rs),
            "recovery_p50_s": percentile(rec, 50),
            "recovery_p95_s": percentile(rec, 95),
            "recovery_n": len(rec),
            "duration_s": round(sum(r["duration_s"] for r in rs), 1),
        }
    return out


def run_campaign(modes=("naive", "protected"), seeds=(0, 1, 2, 3, 4), n_requests: int = 40,
                 kill_interval=(0.3, 1.2), crash_prob: float = 0.01, out_runs: Path = RUNS_DIR / "campaign",
                 results_dir: Path = RESULTS_DIR, log: Callable[[str], None] = print) -> dict:
    runs = []
    started = time.time()
    for mode in modes:
        for seed in seeds:
            cfg = RunConfig(mode=mode, seed=seed, crash_prob=crash_prob)
            m = run_one(out_runs / f"{mode}-seed{seed}", cfg, n_requests, kill_interval=kill_interval)
            runs.append(m)
            log(f"[{mode:9s} seed={seed}] complétion={m['completion_rate']:.0%} doublons={m['duplicate_effects']:3d} "
                f"crashs={m['crashes']:3d} pannes={m['faults_total']:4d} compensations={m['compensations']} "
                f"reprise p50={m['recovery_s']['p50'] or 0:.2f}s durée={m['duration_s']:.1f}s")
    summary = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "seeds": list(seeds), "n_requests": n_requests,
               "kill_interval_s": list(kill_interval) if kill_interval else None, "crash_prob": crash_prob,
               "wall_time_s": round(time.time() - started, 1), "by_mode": aggregate(runs)}
    save_results(runs, summary, out_runs, results_dir)
    return summary


def save_results(runs: list[dict], summary: dict, out_runs: Path, results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (results_dir / "runs.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = ["mode", "seed", "requests", "messages", "completion_rate", "duplicate_effects",
              "requests_with_duplicates", "inconsistent_requests", "compensations", "crashes", "faults_total",
              "llm_calls", "llm_cache_hits", "steps_replayed", "duration_s"]
    with open(results_dir / "runs.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields + ["recovery_p50_s", "recovery_p95_s"], extrasaction="ignore")
        writer.writeheader()
        for r in runs:
            writer.writerow({**r, "recovery_p50_s": r["recovery_s"]["p50"], "recovery_p95_s": r["recovery_s"]["p95"]})
