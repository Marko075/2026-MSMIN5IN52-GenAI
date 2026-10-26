"""Affichage terminal (couleurs ANSI, y compris sous Windows) partagé par la démo et le replay."""
from __future__ import annotations

import os
import sys

RED, GREEN, YELLOW, BOLD, DIM, RESET = "\033[91m", "\033[92m", "\033[93m", "\033[1m", "\033[2m", "\033[0m"


def enable_ansi() -> None:
    if os.name == "nt":
        os.system("")  # active le mode VT100 de la console Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def progress_line(snap: dict, total: int, label: str) -> str:
    c = snap["counters"]
    dup = c["effets_en_double"]
    dup_txt = f"{RED}{BOLD}{dup} effets en double{RESET}" if dup else f"{GREEN}0 effet en double{RESET}"
    bar_len = 24
    filled = int(bar_len * c["terminees"] / max(total, 1))
    bar = "█" * filled + "░" * (bar_len - filled)
    return (f"\r{label} [{bar}] {c['terminees']:2d}/{total}  crashs {YELLOW}{c['kills']:2d}{RESET}  "
            f"pannes {c['pannes_injectees']:3d}  {dup_txt}  compensations {c['compensations']}   ")
