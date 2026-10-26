"""Script « chaos » : tue brutalement le worker à des instants aléatoires (psutil, portable)."""
from __future__ import annotations

import random
import threading
import time
from pathlib import Path

from .journal import Journal
from .supervisor import kill_tree
from .worker import ready_file


def current_worker_pid(run_dir: Path) -> int | None:
    try:
        return int(ready_file(run_dir).read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def kill_worker(run_dir: Path, journal: Journal, event: str = "manual_kill") -> int | None:
    """Tue le worker en cours ; journalise l'instant exact du kill (base du temps de reprise)."""
    pid = current_worker_pid(run_dir)
    if pid is None:
        return None
    ts = time.time()
    if kill_tree(pid):
        journal.write(event, worker_pid=pid, kill_ts=ts)
        return pid
    return None


class ChaosMonkey(threading.Thread):
    """Attend qu'un worker soit prêt, puis le tue après un délai aléatoire tiré dans `interval`.

    Attendre le signal « prêt » garantit que chaque worker fait un peu de travail : sans cela,
    des kills plus rapprochés que le démarrage de Python bloqueraient toute progression.
    """

    def __init__(self, run_dir: Path, seed: int, interval: tuple[float, float] = (0.3, 1.2),
                 journal: Journal | None = None, max_kills: int | None = None):
        super().__init__(daemon=True)
        self.run_dir = Path(run_dir)
        self.rng = random.Random(f"chaos-{seed}")
        self.interval = interval
        self.journal = journal or Journal(self.run_dir, "chaos")
        self.max_kills = max_kills
        self.kills = 0
        self.stop_event = threading.Event()

    def run(self) -> None:
        last_target = None
        while not self.stop_event.is_set():
            if self.max_kills is not None and self.kills >= self.max_kills:
                return
            pid = current_worker_pid(self.run_dir)
            if pid is None or pid == last_target:
                self.stop_event.wait(0.01)
                continue
            last_target = pid
            if self.stop_event.wait(self.rng.uniform(*self.interval)):
                return
            if current_worker_pid(self.run_dir) != pid:
                continue  # le worker a déjà fini ou crashé de lui-même
            if kill_worker(self.run_dir, self.journal, "chaos_kill") is not None:
                self.kills += 1

    def stop(self) -> None:
        self.stop_event.set()
