"""`python -m demo` : scénario complet en moins de 2 minutes, sans réseau ni clé.

1. 40 notes de frais traitées en mode NAÏF sous chaos : les effets en double apparaissent en rouge.
2. Les mêmes 40 notes, les mêmes pannes, en mode PROTÉGÉ : 0 doublon.
3. Comparatif final et rapport HTML.
"""
from __future__ import annotations

import json
import shutil
import sys
import time

from notesfrais.campaign import run_one
from notesfrais.config import RESULTS_DIR, RUNS_DIR, RunConfig
from notesfrais.console import BOLD, DIM, GREEN, RED, RESET, YELLOW, enable_ansi, progress_line

N_REQUESTS = 40
SEED = 42
KILL_INTERVAL = (0.3, 0.9)


def run_mode(mode: str, label: str) -> dict:
    cfg = RunConfig(mode=mode, seed=SEED, crash_prob=0.01)
    print(f"\n{BOLD}{label}{RESET}")
    m = run_one(RUNS_DIR / "demo" / mode, cfg, N_REQUESTS, kill_interval=KILL_INTERVAL, snapshot_every=0.3,
                on_snapshot=lambda s: print(progress_line(s, N_REQUESTS, mode.ljust(9)), end="", flush=True))
    print()
    return m


def color_dup(n: int) -> str:
    return f"{RED}{BOLD}{n}{RESET}" if n else f"{GREEN}{BOLD}0{RESET}"


def main() -> int:
    enable_ansi()
    started = time.time()
    print(f"{BOLD}B5 — workflow agentique résilient et idempotent{RESET}")
    print(f"{DIM}{N_REQUESTS} notes de frais · le worker est tué au hasard toutes les {KILL_INTERVAL[0]}–{KILL_INTERVAL[1]} s"
          f" · pannes 500/timeout des services · doublons de livraison · LLM simulé{RESET}")
    naive = run_mode("naive", "① Mode NAÏF : pas d'état d'étape, pas de clé d'idempotence")
    protected = run_mode("protected", "② Mode PROTÉGÉ : étapes persistées, clés d'idempotence, cache LLM, compensation")

    rows = [
        ("Demandes terminées", f"{naive['completed']}/{naive['requests']}", f"{protected['completed']}/{protected['requests']}"),
        ("Crashs du worker", naive["crashes"], protected["crashes"]),
        ("Pannes injectées", naive["faults_total"], protected["faults_total"]),
        ("Effets en double", color_dup(naive["duplicate_effects"]), color_dup(protected["duplicate_effects"])),
        ("  dont virements", color_dup(naive["duplicate_by_kind"].get("payment", 0)),
         color_dup(protected["duplicate_by_kind"].get("payment", 0))),
        ("Demandes incohérentes", color_dup(naive["inconsistent_requests"]), color_dup(protected["inconsistent_requests"])),
        ("Compensations", naive["compensations"], protected["compensations"]),
        ("Appels LLM", naive["llm_calls"], protected["llm_calls"]),
        ("Reprise p50 (s)", f"{naive['recovery_s']['p50'] or 0:.2f}", f"{protected['recovery_s']['p50'] or 0:.2f}"),
    ]
    print(f"\n{BOLD}{'':26s}{'NAÏF':>14s}{'PROTÉGÉ':>14s}{RESET}")
    for label, a, b in rows:
        pad_a = 14 + (len(str(a)) - len(_strip(str(a))))
        pad_b = 14 + (len(str(b)) - len(_strip(str(b))))
        print(f"{label:26s}{str(a):>{pad_a}s}{str(b):>{pad_b}s}")

    demo_rec = RESULTS_DIR / "recordings"
    demo_rec.mkdir(parents=True, exist_ok=True)
    for mode in ("naive", "protected"):
        shutil.copy(RUNS_DIR / "demo" / mode / "snapshots.jsonl", demo_rec / f"demo-{mode}.snapshots.jsonl")
    (RESULTS_DIR / "demo_last.json").write_text(json.dumps({"naive": naive, "protected": protected}, indent=2,
                                                           ensure_ascii=False), encoding="utf-8")
    print(f"\n{YELLOW}Durée totale : {time.time() - started:.0f} s{RESET} · "
          f"replay : python -m notesfrais replay · tableau de bord : python -m notesfrais dashboard")
    return 0


def _strip(text: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


if __name__ == "__main__":
    sys.exit(main())
