"""Interface en ligne de commande : `python -m notesfrais <commande>`.

Les imports sont faits dans chaque commande : le worker, relancé des dizaines de fois par la
campagne, ne charge ni Streamlit, ni pandas, ni Semantic Kernel.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _run_dir(value: str) -> Path:
    return Path(value).resolve()


def cmd_worker(args) -> int:
    from .worker import run_worker
    return run_worker(args.run_dir)


def cmd_init(args) -> int:
    from .campaign import prepare_run
    from .config import RunConfig
    cfg = RunConfig(mode=args.mode, seed=args.seed, llm=args.llm, crash_at=args.crash_at or [])
    n = prepare_run(args.run_dir, cfg, args.n, args.dup_rate)
    print(f"{n} messages déposés dans {args.run_dir} (mode {args.mode}, LLM {args.llm})")
    return 0


def cmd_supervise(args) -> int:
    from .chaos import ChaosMonkey
    from .config import RunConfig
    from .journal import Journal
    from .supervisor import Supervisor
    cfg = RunConfig.load(args.run_dir)
    sup = Supervisor(args.run_dir, Journal(args.run_dir, "supervisor", mode=cfg.mode))
    chaos = None
    if args.chaos:
        chaos = ChaosMonkey(args.run_dir, cfg.seed, tuple(args.kill_interval), Journal(args.run_dir, "chaos", mode=cfg.mode))
        chaos.start()
    result = sup.run(timeout=args.timeout)
    if chaos:
        chaos.stop()
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_chaos(args) -> int:
    """Chaos autonome, à lancer à côté d'un `supervise` déjà en cours."""
    from .chaos import ChaosMonkey
    from .journal import Journal
    chaos = ChaosMonkey(args.run_dir, args.seed, tuple(args.kill_interval), Journal(args.run_dir, "chaos"),
                        max_kills=args.max_kills)
    chaos.start()
    try:
        chaos.join()
    except KeyboardInterrupt:
        chaos.stop()
    print(f"{chaos.kills} kills")
    return 0


def cmd_kill(args) -> int:
    from .chaos import kill_worker
    from .journal import Journal
    pid = kill_worker(args.run_dir, Journal(args.run_dir, "dashboard"), "manual_kill")
    print(f"worker {pid} tué" if pid else "aucun worker en cours")
    return 0


def cmd_status(args) -> int:
    from .config import RunConfig
    from .metrics import compute_metrics
    cfg = RunConfig.load(args.run_dir)
    print(json.dumps(compute_metrics(args.run_dir, cfg.mode), indent=2, ensure_ascii=False))
    return 0


def cmd_resume(args) -> int:
    from .worker import resume_suspended
    print(f"{resume_suspended(args.run_dir)} demande(s) remise(s) en file")
    return 0


def cmd_campaign(args) -> int:
    from .campaign import run_campaign
    summary = run_campaign(modes=args.modes, seeds=args.seeds, n_requests=args.n,
                           kill_interval=tuple(args.kill_interval), crash_prob=args.crash_prob)
    print(json.dumps(summary["by_mode"], indent=2, ensure_ascii=False))
    if not args.no_report:
        from .report import build_report
        print(f"rapport : {build_report()}")
    return 0


def cmd_run_live(args) -> int:
    """Un run complet (préparation + superviseur + chaos), lancé en arrière-plan par le tableau de bord."""
    from .campaign import run_one
    from .config import RunConfig
    cfg = RunConfig(mode=args.mode, seed=args.seed, crash_prob=args.crash_prob,
                    service_latency=(0.03, 0.08), llm_latency=(0.05, 0.15))
    kill = None if args.no_chaos else tuple(args.kill_interval)
    m = run_one(args.run_dir, cfg, args.n, kill_interval=kill)
    print(json.dumps({k: m[k] for k in ("completion_rate", "duplicate_effects", "crashes")}))
    return 0


def cmd_report(args) -> int:
    from .report import build_report
    print(f"rapport : {build_report()}")
    return 0


def cmd_real_run(args) -> int:
    from .realrun import real_run
    result = real_run(n=args.n, crash=not args.no_crash)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))
    return 0


def cmd_check_llm(args) -> int:
    from .llm import SemanticKernelLLM, parse_extraction
    llm = SemanticKernelLLM(record=False)
    raw = llm.complete("Déjeuner client le 12/10/2026, 34,50 €.", request_id="CHECK")
    print("modèle :", llm.model)
    print("réponse validée :", parse_extraction(raw))
    print("appels réels utilisés :", llm.budget.used(), "/", llm.budget.max_calls)
    return 0


def _streamlit() -> int:
    import subprocess
    from .config import GROUP_DIR
    app = Path(__file__).with_name("dashboard.py")
    # toolbarMode=viewer : masque le bouton « Deploy » et le menu développeur de Streamlit.
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(app), "--server.headless=false",
                            "--client.toolbarMode=viewer"],
                           cwd=str(GROUP_DIR))


def cmd_dashboard(args) -> int:
    return _streamlit()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m notesfrais", description="Workflow résilient de notes de frais (B5)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("worker", help="processus worker (lancé par le superviseur)")
    s.add_argument("--run-dir", type=_run_dir, required=True)
    s.set_defaults(fn=cmd_worker)

    s = sub.add_parser("init", help="prépare un run et dépose les messages")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.add_argument("--mode", choices=["protected", "naive"], default="protected")
    s.add_argument("--llm", choices=["simulated", "replay", "real"], default="simulated")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--n", type=int, default=40)
    s.add_argument("--dup-rate", type=float, default=0.15)
    s.add_argument("--crash-at", nargs="*", help="points de crash déterministes, ex. virement.after_effect")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("supervise", help="lance le worker sous supervision (relance après crash)")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.add_argument("--chaos", action="store_true", help="active le chaos (kills aléatoires)")
    s.add_argument("--kill-interval", type=float, nargs=2, default=[0.3, 1.2])
    s.add_argument("--timeout", type=float, default=900)
    s.set_defaults(fn=cmd_supervise)

    s = sub.add_parser("chaos", help="tue le worker à intervalles aléatoires")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--kill-interval", type=float, nargs=2, default=[0.3, 1.2])
    s.add_argument("--max-kills", type=int, default=None)
    s.set_defaults(fn=cmd_chaos)

    s = sub.add_parser("kill", help="tue le worker maintenant")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.set_defaults(fn=cmd_kill)

    s = sub.add_parser("status", help="mesures d'un run")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("resume", help="remet en file les demandes suspendues")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/manuel"))
    s.set_defaults(fn=cmd_resume)

    s = sub.add_parser("campaign", help="campagne d'injection de pannes (naïf vs protégé)")
    s.add_argument("--modes", nargs="+", default=["naive", "protected"])
    s.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    s.add_argument("--n", type=int, default=40)
    s.add_argument("--kill-interval", type=float, nargs=2, default=[0.3, 1.2])
    s.add_argument("--crash-prob", type=float, default=0.01)
    s.add_argument("--no-report", action="store_true")
    s.set_defaults(fn=cmd_campaign)

    s = sub.add_parser("run-live", help="un run avec chaos (utilisé par le tableau de bord)")
    s.add_argument("--run-dir", type=_run_dir, default=_run_dir("runs/live/protected"))
    s.add_argument("--mode", choices=["protected", "naive"], default="protected")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--n", type=int, default=40)
    s.add_argument("--kill-interval", type=float, nargs=2, default=[0.5, 1.5])
    s.add_argument("--crash-prob", type=float, default=0.0)
    s.add_argument("--no-chaos", action="store_true")
    s.set_defaults(fn=cmd_run_live)

    s = sub.add_parser("report", help="génère results/report.html")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("real-run", help="vrai LLM (OpenRouter) sur 10 demandes, avec un crash pour tester le cache")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--no-crash", action="store_true")
    s.set_defaults(fn=cmd_real_run)

    s = sub.add_parser("check-llm", help="un seul appel réel pour vérifier la clé OpenRouter")
    s.set_defaults(fn=cmd_check_llm)

    s = sub.add_parser("dashboard", help="tableau de bord Streamlit")
    s.set_defaults(fn=cmd_dashboard)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)
