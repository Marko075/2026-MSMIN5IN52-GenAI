"""Étape 2 : extraction structurée par LLM.

Trois implémentations interchangeables :
- `SimulatedLLM` : déterministe, sans réseau (tests, campagne, démo de secours) ;
- `ReplayLLM` : rejoue des réponses réelles enregistrées (`data/llm_recordings.jsonl`) ;
- `SemanticKernelLLM` : Semantic Kernel + connecteur OpenAI pointé sur OpenRouter.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import time
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .config import DATA_DIR, LLM_MAX_CALLS, PROMPT_VERSION, RESULTS_DIR, llm_settings
from .faults import FaultInjector, PermanentError, TransientError

RECORDINGS_PATH = DATA_DIR / "llm_recordings.jsonl"
USAGE_PATH = RESULTS_DIR / "llm_usage.jsonl"


class Expense(BaseModel):
    """Schéma de sortie imposé au LLM."""

    model_config = ConfigDict(extra="forbid")
    montant: float = Field(gt=0, lt=100000)
    devise: Literal["EUR", "USD", "GBP", "CHF"]
    categorie: Literal["repas", "transport", "hebergement", "materiel", "autre"]
    date: date
    motif: str = Field(min_length=3, max_length=200)


SYSTEM_PROMPT = """Tu extrais les informations d'une note de frais écrite en texte libre.
Réponds UNIQUEMENT avec un objet JSON, sans texte autour, de la forme :
{"montant": <nombre positif>, "devise": "EUR"|"USD"|"GBP"|"CHF",
 "categorie": "repas"|"transport"|"hebergement"|"materiel"|"autre",
 "date": "AAAA-MM-JJ", "motif": "<résumé court en français>"}
Règles : montant sans symbole ni séparateur de milliers ; date de la dépense au format ISO ;
carburant, péage, parking, taxi, train, avion, location de voiture et transports en commun = transport ;
hôtel = hebergement ; restaurant, déjeuner, dîner = repas ; équipement et fournitures = materiel."""


class LLMUnavailable(TransientError):
    pass


class InvalidLLMOutput(Exception):
    pass


class BudgetExceeded(PermanentError):
    pass


def text_key(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()


def cache_key(model: str, text: str) -> str:
    """Clé du cache d'extraction : modèle + version du prompt + texte normalisé."""
    return hashlib.sha256(f"{model}|{PROMPT_VERSION}|{text_key(text)}".encode()).hexdigest()


def user_prompt(text: str, repair_hint: str | None = None) -> str:
    prompt = f"Note de frais :\n<<<\n{text}\n>>>"
    if repair_hint:
        prompt += ("\n\nTa réponse précédente était invalide (" + repair_hint[:300] +
                   "). Renvoie uniquement un JSON conforme au schéma.")
    return prompt


def parse_extraction(raw: str) -> dict:
    """Valide la réponse brute du LLM. Lève InvalidLLMOutput si le JSON ou le schéma sont faux."""
    cleaned = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.S)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise InvalidLLMOutput(f"JSON invalide : {exc.msg}") from exc
    try:
        expense = Expense.model_validate(data)
    except ValidationError as exc:
        raise InvalidLLMOutput(f"schéma non respecté : {exc.errors()[0]['msg']}") from exc
    return json.loads(expense.model_dump_json())


# --------------------------------------------------------------------------- simulé

_CATEGORY_WORDS = [
    ("hebergement", ["hôtel", "hotel", "nuit"]),
    ("repas", ["déjeuner", "dîner", "diner", "repas", "lunch", "dinner", "petit-déjeuner"]),
    ("transport", ["train", "taxi", "vol ", "flight", "essence", "péage", "parking", "navigo", "métro",
                   "location de voiture", "billet"]),
    ("materiel", ["clavier", "souris", "câble", "casque", "ssd", "ordinateur", "fournitures"]),
]


def heuristic_extract(text: str) -> dict:
    """Extraction par règles pour un texte inconnu du jeu synthétique (mode simulé)."""
    low = text.lower()
    currency = "EUR"
    for code, marks in {"USD": ["usd", "$"], "GBP": ["gbp", "£"], "CHF": ["chf"]}.items():
        if any(m in low for m in marks):
            currency = code
    amounts = re.findall(r"(\d[\d  ]*(?:[.,]\d{1,2})?)\s*(?:€|eur|euros?|usd|gbp|chf)", low)
    amount = float(amounts[-1].replace(" ", "").replace(" ", "").replace(",", ".")) if amounts else 10.0
    category = "autre"
    for cat, words in _CATEGORY_WORDS:
        if any(w in low for w in words):
            category = cat
            break
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text) or re.search(r"(\d{2})[/.](\d{2})[/.](\d{4})", text)
    if m and len(m.group(1)) == 4:
        iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    elif m:
        iso = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    else:
        iso = "2026-10-01"
    return {"montant": amount, "devise": currency, "categorie": category, "date": iso,
            "motif": text.strip()[:60] or "note de frais"}


class SimulatedLLM:
    """LLM factice : renvoie la vérité terrain du jeu synthétique (ou une heuristique), avec latence
    et pannes injectables (API indisponible, JSON invalide)."""

    model = "simulated"
    real = False

    def __init__(self, truth: dict[str, dict] | None = None, faults: FaultInjector | None = None,
                 rng: random.Random | None = None, latency: tuple[float, float] = (0.0, 0.0)):
        self.truth = truth or {}
        self.rng = rng or random.Random(0)
        self.faults = faults or FaultInjector(self.rng)
        self.latency = latency
        self.calls = 0

    def complete(self, text: str, repair_hint: str | None = None, request_id: str | None = None) -> str:
        self.calls += 1
        if self.latency[1] > 0:
            time.sleep(self.rng.uniform(*self.latency))
        fault = self.faults.draw("llm")
        if fault == "unavailable":
            raise LLMUnavailable("LLM simulé : 503")
        if fault == "invalid_json":
            return '{"montant": "trente-quatre euros", "devise": '
        answer = self.truth.get(text_key(text)) or heuristic_extract(text)
        return json.dumps(answer, ensure_ascii=False)


class ReplayLLM(SimulatedLLM):
    """Rejoue les réponses réelles enregistrées ; à défaut, se comporte comme le LLM simulé."""

    model = "replay"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recordings: dict[str, str] = {}
        if RECORDINGS_PATH.exists():
            for line in RECORDINGS_PATH.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self.recordings[rec["text_key"]] = rec["raw"]

    def complete(self, text: str, repair_hint: str | None = None, request_id: str | None = None) -> str:
        recorded = self.recordings.get(text_key(text))
        if recorded is not None and repair_hint is None:
            self.calls += 1
            return recorded
        return super().complete(text, repair_hint, request_id)


# --------------------------------------------------------------------------- réel

class LLMBudget:
    """Compteur persistant des appels réels (results/llm_usage.jsonl), plafonné pour tout le projet."""

    def __init__(self, path=USAGE_PATH, max_calls: int = LLM_MAX_CALLS):
        self.path = path
        self.max_calls = max_calls

    def used(self) -> int:
        if not self.path.exists():
            return 0
        return sum(1 for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip())

    def check(self) -> None:
        if self.used() >= self.max_calls:
            raise BudgetExceeded(f"budget LLM atteint ({self.max_calls} appels)")

    def record(self, **fields) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.time(), **fields}, ensure_ascii=False) + "\n")


class SemanticKernelLLM:
    """Vrai LLM : Semantic Kernel (comme dans le cours), connecteur OpenAI pointé sur OpenRouter."""

    real = True

    def __init__(self, budget: LLMBudget | None = None, record: bool = True, model: str | None = None):
        settings = llm_settings()
        key = settings["api_key"]
        if not key or not key.startswith("sk-") or "REMPLACE" in key:
            raise PermanentError("OPENROUTER_API_KEY absente ou non renseignée dans groupe-transformers/.env")
        # Imports paresseux : le worker simulé ne paie pas le coût d'import de Semantic Kernel.
        import asyncio

        from openai import AsyncOpenAI
        from semantic_kernel import Kernel
        from semantic_kernel.connectors.ai.open_ai import (OpenAIChatCompletion,
                                                           OpenAIChatPromptExecutionSettings)

        self.model = model or settings["model"]
        self.budget = budget or LLMBudget()
        self.record_responses = record
        self.loop = asyncio.new_event_loop()
        client = AsyncOpenAI(api_key=key, base_url=settings["base_url"], timeout=60, max_retries=0)
        self.service = OpenAIChatCompletion(ai_model_id=self.model, async_client=client, service_id="extraction")
        self.kernel = Kernel()
        self.kernel.add_service(self.service)
        self.settings = OpenAIChatPromptExecutionSettings(
            service_id="extraction", temperature=0, max_tokens=1500,
            response_format={"type": "json_object"})
        self.calls = 0

    def complete(self, text: str, repair_hint: str | None = None, request_id: str | None = None) -> str:
        from semantic_kernel.contents import ChatHistory

        self.budget.check()
        history = ChatHistory()
        history.add_system_message(SYSTEM_PROMPT)
        history.add_user_message(user_prompt(text, repair_hint))
        started = time.time()
        self.calls += 1
        try:
            result = self.loop.run_until_complete(
                self.service.get_chat_message_content(history, self.settings))
        except Exception as exc:  # noqa: BLE001 - on classe l'erreur, sans jamais l'afficher avec la clé
            status = getattr(getattr(exc, "__cause__", None), "status_code", None)
            self.budget.record(model=self.model, request_id=request_id, ok=False, error=type(exc).__name__,
                               status=status, latency_s=round(time.time() - started, 2))
            if status in (401, 403):
                raise PermanentError(f"clé OpenRouter refusée (HTTP {status})") from None
            raise LLMUnavailable(f"{type(exc).__name__} (HTTP {status})") from None
        raw = str(result.content if hasattr(result, "content") else result)
        usage = (result.metadata or {}).get("usage") if hasattr(result, "metadata") else None
        self.budget.record(model=self.model, request_id=request_id, ok=True,
                           latency_s=round(time.time() - started, 2),
                           prompt_tokens=getattr(usage, "prompt_tokens", None),
                           completion_tokens=getattr(usage, "completion_tokens", None))
        if self.record_responses and repair_hint is None:
            RECORDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(RECORDINGS_PATH, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"text_key": text_key(text), "model": self.model, "raw": raw},
                                    ensure_ascii=False) + "\n")
        return raw


def llm_fault_probabilities(p_invalid: float, p_unavailable: float) -> list[tuple[str, float]]:
    return [("invalid_json", p_invalid), ("unavailable", p_unavailable)]
