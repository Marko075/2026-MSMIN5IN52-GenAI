"""Processus worker : traite la file jusqu'à ce qu'elle soit vide (ou indéfiniment)."""
from __future__ import annotations

import os
import time
from pathlib import Path

from .config import RunConfig
from .db import tx, workflow_db
from .engine import build_engine


def ready_file(run_dir: Path) -> Path:
    return Path(run_dir) / "worker.ready"


def run_worker(run_dir: Path) -> int:
    run_dir = Path(run_dir)
    cfg = RunConfig.load(run_dir)
    engine = build_engine(run_dir, cfg, hard_crash=True)
    engine.journal.write("worker_started", llm=cfg.llm)
    # Le PID réel de l'interpréteur (sous Windows, le python.exe d'un venv est un lanceur intermédiaire).
    ready_file(run_dir).write_text(str(os.getpid()), encoding="utf-8")
    while True:
        if engine.tick():
            continue
        if cfg.exit_when_idle:
            engine.journal.write("worker_idle_exit")
            try:
                ready_file(run_dir).unlink()
            except FileNotFoundError:
                pass
            return 0
        time.sleep(0.2)


def resume_suspended(run_dir: Path) -> int:
    """Remet en file les demandes suspendues (LLM indisponible, compensation à reprendre)."""
    conn = workflow_db(Path(run_dir))
    with tx(conn):
        count = conn.execute("UPDATE requests SET status=CASE WHEN reason LIKE 'compensation%' THEN 'COMPENSATING'"
                             " ELSE 'RUNNING' END, updated_at=? WHERE status='SUSPENDED'",
                             (time.time(),)).rowcount
    conn.close()
    return count
