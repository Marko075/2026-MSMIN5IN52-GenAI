"""Tests unitaires : schéma LLM, règles, services idempotents, journal, budget, retries."""
import json
import random

import pytest

from notesfrais.db import services_db
from notesfrais.faults import FaultInjector, PermanentError, TransientError
from notesfrais.journal import Journal, read_journal
from notesfrais.llm import BudgetExceeded, InvalidLLMOutput, LLMBudget, parse_extraction
from notesfrais.retry import RetryExhausted, RetryPolicy, call_with_retry
from notesfrais.rules import apply_rules
from notesfrais.services import IdempotencyConflict, PaymentService

GOOD = {"montant": 34.5, "devise": "EUR", "categorie": "repas", "date": "2026-10-12", "motif": "Déjeuner client"}


def test_parse_accepts_fenced_json():
    assert parse_extraction("```json\n" + json.dumps(GOOD) + "\n```")["montant"] == 34.5


@pytest.mark.parametrize("bad", [
    "pas du json",
    json.dumps({**GOOD, "montant": -3}),
    json.dumps({**GOOD, "devise": "JPY"}),
    json.dumps({**GOOD, "inconnu": 1}),
    json.dumps({k: v for k, v in GOOD.items() if k != "date"}),
])
def test_parse_rejects_invalid(bad):
    with pytest.raises(InvalidLLMOutput):
        parse_extraction(bad)


def test_rules():
    assert apply_rules(GOOD)["decision"] == "APPROVED"
    assert apply_rules({**GOOD, "montant": 41})["decision"] == "REJECTED"
    assert apply_rules({**GOOD, "date": "2026-11-01"})["decision"] == "REJECTED"
    assert apply_rules({**GOOD, "devise": "CHF", "montant": 36})["amount_eur"] == 37.8


def _payment(tmp_path, script=None):
    return PaymentService(services_db(tmp_path), FaultInjector(random.Random(0), script=script or {}),
                          random.Random(0))


def test_payment_idempotency_key(tmp_path):
    svc = _payment(tmp_path)
    first = svc.charge("K1", "R1", 10.0, "E01")
    second = svc.charge("K1", "R1", 10.0, "E01")
    assert first == second
    assert svc.conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0] == 1


def test_payment_without_key_duplicates(tmp_path):
    svc = _payment(tmp_path)
    svc.charge(None, "R1", 10.0, "E01")
    svc.charge(None, "R1", 10.0, "E01")
    assert svc.conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0] == 2


def test_idempotency_conflict(tmp_path):
    svc = _payment(tmp_path)
    svc.charge("K1", "R1", 10.0, "E01")
    with pytest.raises(IdempotencyConflict):
        svc.charge("K1", "R1", 99.0, "E01")


def test_journal_ignores_truncated_line(tmp_path):
    j = Journal(tmp_path, "worker")
    j.write("step_done", request_id="R1", step="controle")
    with open(tmp_path / "worker.jsonl", "a", encoding="utf-8") as fh:
        fh.write('{"ts": 1, "event": "step_do')  # ligne coupée par un kill
    events = read_journal(tmp_path)
    assert [e["event"] for e in events] == ["step_done"]


def test_budget_guard(tmp_path):
    budget = LLMBudget(path=tmp_path / "usage.jsonl", max_calls=2)
    budget.record(ok=True)
    budget.check()
    budget.record(ok=True)
    with pytest.raises(BudgetExceeded):
        budget.check()


def test_retry_bounded_and_only_transient():
    calls = []

    def flaky():
        calls.append(1)
        raise TransientError("503")

    with pytest.raises(RetryExhausted):
        call_with_retry(flaky, RetryPolicy(attempts=3, base_delay=0), random.Random(0), sleep=lambda s: None)
    assert len(calls) == 3

    def permanent():
        calls.append(1)
        raise PermanentError("non")

    calls.clear()
    with pytest.raises(PermanentError):
        call_with_retry(permanent, RetryPolicy(attempts=3), random.Random(0), sleep=lambda s: None)
    assert len(calls) == 1


def test_backoff_grows_and_is_capped():
    policy = RetryPolicy(attempts=6, base_delay=0.1, max_delay=0.5)
    rng = random.Random(0)
    delays = [policy.delay(i, rng) for i in range(1, 6)]
    assert all(d <= 0.5 for d in delays)
    assert delays[2] > delays[0]
