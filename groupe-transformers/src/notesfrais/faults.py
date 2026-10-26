"""Injection de pannes : erreurs transitoires (services, LLM) et points de crash du worker."""
from __future__ import annotations

import os
import random
from pathlib import Path

from .config import CRASH_EXIT_CODE


class TransientError(Exception):
    """Erreur qui justifie un nouvel essai (timeout, 500, API indisponible)."""


class PermanentError(Exception):
    """Erreur définitive : réessayer ne changera rien (adresse invalide, clé refusée...)."""


class SimulatedCrash(BaseException):
    """Crash simulé en mode in-process (tests). BaseException : aucun `except Exception` ne l'avale."""


class FaultInjector:
    """Tire une panne pour une cible donnée, soit selon un script (tests), soit au hasard (campagne)."""

    def __init__(self, rng: random.Random, probabilities: dict[str, list[tuple[str, float]]] | None = None,
                 script: dict[str, list[str | None]] | None = None):
        self.rng = rng
        self.probabilities = probabilities or {}
        # Listes partagées (pas de copie) : un script consommé reste consommé après un crash simulé.
        self.script = script or {}

    def draw(self, target: str) -> str | None:
        queue = self.script.get(target)
        if queue:
            return queue.pop(0)
        roll = self.rng.random()
        cumulative = 0.0
        for kind, p in self.probabilities.get(target, []):
            cumulative += p
            if roll < cumulative:
                return kind
        return None


class CrashController:
    """Points de crash nommés, par exemple `virement.after_effect`.

    - `crash_at` : points déterministes, déclenchés une seule fois par run (marqueur fichier, donc
      valable d'un processus à l'autre) ;
    - `crash_prob` : probabilité de crash à chaque point (campagne) ;
    - `hard=True` : `os._exit` (vrai crash du processus), sinon `SimulatedCrash` (tests in-process).
    """

    def __init__(self, run_dir: Path, crash_at: list[str] | None = None, crash_prob: float = 0.0,
                 rng: random.Random | None = None, hard: bool = True, journal=None):
        self.run_dir = Path(run_dir)
        self.crash_at = set(crash_at or [])
        self.crash_prob = crash_prob
        self.rng = rng or random.Random()
        self.hard = hard
        self.journal = journal

    def _marker(self, name: str) -> Path:
        return self.run_dir / f"crash_fired.{name}"

    def point(self, name: str, request_id: str | None = None) -> None:
        reason = None
        if name in self.crash_at and not self._marker(name).exists():
            self._marker(name).write_text("fired", encoding="utf-8")
            reason = "deterministic"
        elif self.crash_prob and self.rng.random() < self.crash_prob:
            reason = "random"
        if reason is None:
            return
        if self.journal is not None:
            self.journal.write("crash_point", request_id=request_id, point=name, reason=reason)
        if self.hard:
            os._exit(CRASH_EXIT_CODE)
        raise SimulatedCrash(name)
