"""Exécution avec le vrai LLM (OpenRouter) sur 10 demandes variées, avec un crash forcé juste après
l'appel LLM pour vérifier que la reprise utilise le cache au lieu de rappeler le modèle."""
from __future__ import annotations

import json

from .campaign import prepare_run
from .config import LLM_MAX_CALLS, RESULTS_DIR, RUNS_DIR, RunConfig
from .dataset import load_requests
from .db import workflow_db
from .llm import LLMBudget
from .metrics import compute_metrics
from .supervisor import Supervisor

# Français/anglais, EUR/USD/GBP/CHF, refus (plafond, date future, date ancienne), compensation.
REAL_IDS = ["R001", "R005", "R008", "R010", "R017", "R021", "R029", "R033", "R034", "R037"]
FIELDS = ["montant", "devise", "categorie", "date"]


def _match(field: str, expected, got) -> bool:
    if got is None:
        return False
    if field == "montant":
        return abs(float(expected) - float(got)) < 0.01
    return str(expected) == str(got)


def real_run(n: int = 10, crash: bool = True) -> dict:
    by_id = {r["request_id"]: r for r in load_requests()}
    requests = [by_id[i] for i in REAL_IDS[:n]]
    budget = LLMBudget()
    before = budget.used()
    if before + 2 * len(requests) > LLM_MAX_CALLS:
        raise SystemExit(f"budget insuffisant : {before} appels déjà utilisés sur {LLM_MAX_CALLS}")
    run_dir = RUNS_DIR / "real"
    cfg = RunConfig(mode="protected", llm="real", seed=7,
                    crash_at=["extraction.after_effect"] if crash else [],
                    p_llm_invalid_json=0.0, p_llm_unavailable=0.0, service_latency=(0.0, 0.01),
                    retry_attempts=3, retry_base_delay=1.0, retry_max_delay=4.0)
    prepare_run(run_dir, cfg, requests=requests, dup_rate=0.1)
    sup = Supervisor(run_dir).run(timeout=900)
    metrics = compute_metrics(run_dir, "protected")

    conn = workflow_db(run_dir)
    rows = []
    for req in requests:
        out = conn.execute("SELECT output FROM steps WHERE request_id=? AND step='extraction'",
                           (req["request_id"],)).fetchone()
        status = conn.execute("SELECT status, reason FROM requests WHERE request_id=?",
                              (req["request_id"],)).fetchone()
        got = json.loads(out["output"]) if out and out["output"] else {}
        rows.append({
            "request_id": req["request_id"], "scenario": req["scenario"], "texte": req["texte"],
            "attendu": req["attendu"], "obtenu": got,
            "champs_corrects": {f: _match(f, req["attendu"][f], got.get(f)) for f in FIELDS},
            "statut": status["status"] if status else None, "raison": status["reason"] if status else None,
        })
    conn.close()
    used = budget.used() - before
    summary = {
        "model": json.loads(budget.path.read_text(encoding="utf-8").splitlines()[-1]).get("model"),
        "requests": len(requests),
        "real_llm_calls": used,
        "llm_cache_hits": metrics["llm_cache_hits"],
        "crashes": sup["restarts"],
        "duplicate_effects": metrics["duplicate_effects"],
        "statuses": metrics["statuses"],
        "field_accuracy": {f: round(sum(r["champs_corrects"][f] for r in rows) / len(rows), 3) for f in FIELDS},
        "exact_match_rate": round(sum(all(r["champs_corrects"].values()) for r in rows) / len(rows), 3),
        "budget_used_total": budget.used(),
        "budget_max": LLM_MAX_CALLS,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "real_llm.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=2,
                                                          ensure_ascii=False), encoding="utf-8")
    return {"summary": summary, "rows": rows}
