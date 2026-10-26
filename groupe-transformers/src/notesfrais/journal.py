"""Journal JSON Lines : un fichier par processus, fusionnés par horodatage à la lecture."""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path


class Journal:
    def __init__(self, run_dir: Path, source: str, run_id: str | None = None, mode: str | None = None):
        self.path = Path(run_dir) / f"{source}.jsonl"
        self.source = source
        self.run_id = run_id or Path(run_dir).name
        self.mode = mode
        self._lock = threading.Lock()

    def write(self, event: str, request_id: str | None = None, step: str | None = None,
              duration_ms: float | None = None, **extra) -> dict:
        record = {
            "ts": time.time(),
            "run_id": self.run_id,
            "source": self.source,
            "pid": os.getpid(),
            "event": event,
        }
        if self.mode:
            record["mode"] = self.mode
        if request_id is not None:
            record["request_id"] = request_id
        if step is not None:
            record["step"] = step
        if duration_ms is not None:
            record["duration_ms"] = round(duration_ms, 2)
        record.update(extra)
        line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
        with self._lock:
            # Ouverture/fermeture à chaque ligne : la ligne est remise à l'OS avant un éventuel kill.
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(line)
        return record


class NullJournal(Journal):
    def __init__(self):  # noqa: D401 - journal muet pour les tests unitaires
        self.source = "null"
        self.run_id = "null"
        self.mode = None
        self.records: list[dict] = []

    def write(self, event: str, request_id=None, step=None, duration_ms=None, **extra) -> dict:
        record = {"ts": time.time(), "event": event, "request_id": request_id, "step": step,
                  "pid": os.getpid(), **extra}
        self.records.append(record)
        return record


def read_journal(run_dir: Path) -> list[dict]:
    """Fusionne tous les *.jsonl du run. Une ligne tronquée par un kill est ignorée, pas fatale."""
    events: list[dict] = []
    for path in sorted(Path(run_dir).glob("*.jsonl")):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            continue
    events.sort(key=lambda e: e.get("ts", 0))
    return events
