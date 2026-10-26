"""Superviseur : lance le worker dans un processus séparé et le relance après chaque crash."""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil

from .config import SRC_DIR
from .journal import Journal


def worker_command(run_dir: Path) -> list[str]:
    return [sys.executable, "-m", "notesfrais", "worker", "--run-dir", str(run_dir)]


def worker_env() -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def kill_tree(pid: int) -> bool:
    """Tue brutalement un processus et ses enfants (équivalent portable de kill -9)."""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    targets = proc.children(recursive=True) + [proc]
    for p in targets:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass
    return True


class Supervisor:
    def __init__(self, run_dir: Path, journal: Journal | None = None, max_restarts: int = 2000):
        self.run_dir = Path(run_dir)
        self.journal = journal or Journal(self.run_dir, "supervisor")
        self.max_restarts = max_restarts
        self.proc: subprocess.Popen | None = None
        self.restarts = 0
        self.stop_event = threading.Event()

    def _spawn(self) -> None:
        stderr = open(self.run_dir / "worker_stderr.log", "ab")
        self.proc = subprocess.Popen(worker_command(self.run_dir), stdout=subprocess.DEVNULL, stderr=stderr,
                                     env=worker_env(), cwd=str(self.run_dir))
        stderr.close()
        (self.run_dir / "worker.pid").write_text(str(self.proc.pid), encoding="utf-8")
        self.journal.write("worker_spawned", worker_pid=self.proc.pid, restart=self.restarts)

    def run(self, timeout: float = 900) -> dict:
        started = time.time()
        self._spawn()
        status = "finished"
        while True:
            rc = self.proc.poll()
            if rc is None:
                if self.stop_event.is_set() or time.time() - started > timeout:
                    status = "stopped" if self.stop_event.is_set() else "timeout"
                    kill_tree(self.proc.pid)
                    self.proc.wait()
                    self.journal.write("supervisor_stop", reason=status)
                    break
                time.sleep(0.02)
                continue
            if rc == 0:
                self.journal.write("worker_exited", returncode=0)
                break
            self.journal.write("worker_crashed", worker_pid=self.proc.pid, returncode=rc)
            self.restarts += 1
            if self.restarts > self.max_restarts:
                status = "too_many_restarts"
                break
            self._spawn()
        for name in ("worker.pid", "worker.ready"):
            try:
                (self.run_dir / name).unlink()
            except FileNotFoundError:
                pass
        return {"status": status, "restarts": self.restarts, "elapsed_s": round(time.time() - started, 2)}
