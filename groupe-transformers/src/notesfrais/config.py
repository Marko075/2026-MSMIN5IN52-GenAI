"""Chemins, constantes et configuration d'une exécution (run)."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

GROUP_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = GROUP_DIR / "src"
DATA_DIR = GROUP_DIR / "data"
RESULTS_DIR = GROUP_DIR / "results"
RUNS_DIR = GROUP_DIR / "runs"

PROMPT_VERSION = "v1"
DEFAULT_MODEL = "qwen/qwen3.8-flash"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MAX_CALLS = 150
# Date de référence fixe : les règles de contrôle restent déterministes quel que soit le jour d'exécution.
REFERENCE_DATE = date(2026, 10, 20)

CRASH_EXIT_CODE = 70


def load_env() -> None:
    """Charge groupe-transformers/.env sans jamais afficher son contenu."""
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - dépendance optionnelle en mode simulé
        return
    load_dotenv(GROUP_DIR / ".env", override=False)


def llm_settings() -> dict:
    load_env()
    return {
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "base_url": os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL),
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
    }


@dataclass
class RunConfig:
    """Paramètres partagés par le superviseur, le worker et le tableau de bord (run_dir/config.json)."""

    mode: str = "protected"  # "protected" ou "naive"
    seed: int = 0
    llm: str = "simulated"  # "simulated", "replay" ou "real"
    exit_when_idle: bool = True
    # Latences simulées (secondes) : avant l'effet, puis réponse réseau après l'effet.
    service_latency: tuple[float, float] = (0.01, 0.04)
    llm_latency: tuple[float, float] = (0.02, 0.06)
    # Pannes transitoires des services factices et du LLM simulé.
    p_service_error: float = 0.10  # erreur 500 avant l'effet
    p_service_timeout_after: float = 0.05  # timeout APRÈS l'effet : la réponse est perdue
    p_llm_invalid_json: float = 0.05
    p_llm_unavailable: float = 0.03
    # Crash du worker : points déterministes (déclenchés une seule fois) et probabilité par point.
    crash_at: list[str] = field(default_factory=list)
    crash_prob: float = 0.0
    # Retries bornés avec backoff exponentiel et jitter.
    retry_attempts: int = 5
    retry_base_delay: float = 0.02
    retry_max_delay: float = 0.3

    def save(self, run_dir: Path) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "config.json").write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, run_dir: Path) -> "RunConfig":
        raw = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
        for key in ("service_latency", "llm_latency"):
            raw[key] = tuple(raw[key])
        return cls(**raw)
