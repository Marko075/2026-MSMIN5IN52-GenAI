"""Retries bornés avec backoff exponentiel et jitter (cf. CoursIA 09_Production_Patterns)."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .faults import TransientError

T = TypeVar("T")


class RetryExhausted(Exception):
    def __init__(self, attempts: int, last_error: Exception):
        super().__init__(f"{attempts} essais épuisés : {last_error!r}")
        self.attempts = attempts
        self.last_error = last_error


@dataclass
class RetryPolicy:
    attempts: int = 5
    base_delay: float = 0.02
    max_delay: float = 0.3

    def delay(self, attempt: int, rng: random.Random) -> float:
        raw = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        return raw * (0.5 + rng.random() / 2)  # jitter : évite que tous les clients réessaient ensemble


def call_with_retry(fn: Callable[[], T], policy: RetryPolicy, rng: random.Random,
                    on_retry: Callable[[int, Exception, float], None] | None = None,
                    sleep: Callable[[float], None] = time.sleep) -> T:
    """Seules les TransientError sont réessayées ; une PermanentError remonte immédiatement."""
    for attempt in range(1, policy.attempts + 1):
        try:
            return fn()
        except TransientError as exc:
            if attempt == policy.attempts:
                raise RetryExhausted(attempt, exc) from exc
            wait = policy.delay(attempt, rng)
            if on_retry is not None:
                on_retry(attempt, exc, wait)
            sleep(wait)
    raise AssertionError("inatteignable")
