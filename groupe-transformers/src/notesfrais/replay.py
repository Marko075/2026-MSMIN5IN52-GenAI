"""Replay terminal d'une campagne enregistrée : rien n'est exécuté, on relit les instantanés."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .config import RESULTS_DIR
from .console import BOLD, RESET, enable_ansi, progress_line


def replay_terminal(recording: Path | None = None, speed: float = 4.0) -> int:
    enable_ansi()
    if recording is None:
        candidates = sorted((RESULTS_DIR / "recordings").glob("*.snapshots.jsonl"))
        if not candidates:
            print("Aucun enregistrement : lancez `python -m notesfrais campaign` ou `python -m demo`.")
            return 1
        recordings = candidates
    else:
        recordings = [Path(recording)]
    for path in recordings:
        frames = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not frames:
            continue
        total = len(frames[-1]["requests"]) or 40
        label = f"{BOLD}{path.name.replace('.snapshots.jsonl', ''):18s}{RESET}"
        prev = frames[0]["t"]
        for frame in frames:
            time.sleep(max(0.0, (frame["t"] - prev) / speed))
            prev = frame["t"]
            print(progress_line(frame, total, label), end="", flush=True)
        print()
    return 0
