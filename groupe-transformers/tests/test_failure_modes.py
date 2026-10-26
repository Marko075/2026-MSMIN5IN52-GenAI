"""Modes d'échec : doublons de livraison, pannes transitoires, entrée vide, JSON invalide, API indisponible."""
import pytest

from notesfrais.metrics import compute_metrics
from notesfrais.worker import resume_suspended

APPROVED = "R001"


def test_full_dataset_nominal(make_run):
    run = make_run().drain()
    m = compute_metrics(run.dir, "protected")
    assert m["statuses"] == {"DONE": 28, "REJECTED": 9, "COMPENSATED": 3}
    assert m["duplicate_effects"] == 0
    assert m["inconsistent_requests"] == 0


def test_duplicate_delivery_protected(make_run):
    run = make_run([APPROVED], deliveries=2).drain()
    assert run.effects(APPROVED)["payment"] == 1
    assert len(run.events("duplicate_ignored")) == 1


def test_duplicate_delivery_naive(make_run):
    # Même processus : l'anti-doublon en mémoire évite le 2e virement, mais 2 e-mails contradictoires partent.
    run = make_run([APPROVED], mode="naive", deliveries=2).drain()
    assert run.effects(APPROVED)["payment"] == 1
    assert run.effects(APPROVED)["email"] == 2
    # Un redémarrage entre les deux livraisons efface cette mémoire : double virement.
    run = make_run([APPROVED], mode="naive", deliveries=2, crash_at=["notification.after_commit"]).drain()
    assert run.effects(APPROVED)["payment"] == 2


def test_semantic_duplicate_rejected(make_run):
    run = make_run(["R002", "R035"]).drain()
    statuses = {run.status("R002"), run.status("R035")}
    assert statuses == {"DONE", "REJECTED"}
    assert run.effects("R002")["payment"] + run.effects("R035")["payment"] == 1


def test_transient_500_is_retried(make_run):
    run = make_run([APPROVED], script={"payment": ["error_500", "error_500"]}).drain()
    assert run.status(APPROVED) == "DONE"
    assert run.effects(APPROVED)["payment"] == 1
    assert len([e for e in run.events("retry") if e["step"] == "virement"]) == 2


def test_timeout_after_effect_protected(make_run):
    """Le service a payé mais la réponse est perdue : le retry avec la même clé ne repaie pas."""
    run = make_run([APPROVED], script={"payment": ["timeout_after"]}).drain()
    assert run.effects(APPROVED)["payment"] == 1
    assert run.events("idempotent_replay")


def test_timeout_after_effect_naive(make_run):
    run = make_run([APPROVED], mode="naive", script={"payment": ["timeout_after"]}).drain()
    assert run.effects(APPROVED)["payment"] == 2


def test_payment_retries_exhausted_reconciles(make_run):
    """Retries épuisés alors que le paiement a eu lieu : la clé permet de le retrouver et de le compenser."""
    run = make_run([APPROVED], script={"payment": ["timeout_after"] * 5}).drain()
    assert run.status(APPROVED) == "COMPENSATED"
    effects = run.effects(APPROVED)
    assert effects["payment"] - effects["refund"] == 0


def test_payment_unavailable_fails_cleanly(make_run):
    run = make_run([APPROVED], script={"payment": ["error_500"] * 5}).drain()
    assert run.status(APPROVED) == "FAILED"
    assert run.effects(APPROVED)["payment"] == 0


def test_compensation_path(make_run):
    run = make_run(["R037"]).drain()
    assert run.status("R037") == "COMPENSATED"
    effects = run.effects("R037")
    assert (effects["payment"], effects["refund"], effects["email"]) == (1, 1, 0)


def test_empty_input_rejected_without_llm_call(make_run):
    run = make_run(["R040"]).drain()
    assert run.status("R040") == "REJECTED"
    assert run.events("llm_call") == []
    assert sum(run.effects("R040").values()) == 0


def test_invalid_json_repaired(make_run):
    run = make_run([APPROVED], script={"llm": ["invalid_json"]}).drain()
    assert run.status(APPROVED) == "DONE"
    assert len(run.events("llm_call")) == 2
    assert run.events("llm_invalid_output")


def test_invalid_json_twice_rejects_without_payment(make_run):
    run = make_run([APPROVED], script={"llm": ["invalid_json", "invalid_json"]}).drain()
    assert run.status(APPROVED) == "REJECTED"
    effects = run.effects(APPROVED)
    assert effects["payment"] == 0
    assert effects["email"] == 1  # avis de refus


def test_llm_unavailable_suspends_then_resumes(make_run):
    run = make_run([APPROVED], script={"llm": ["unavailable"] * 5}).drain()
    assert run.status(APPROVED) == "SUSPENDED"
    assert sum(run.effects(APPROVED).values()) == 0
    assert resume_suspended(run.dir) == 1
    run.drain()
    assert run.status(APPROVED) == "DONE"
    assert run.effects(APPROVED)["payment"] == 1


@pytest.mark.parametrize("mode", ["protected", "naive"])
def test_rules_rejections(make_run, mode):
    run = make_run(["R029", "R033", "R034"], mode=mode).drain()
    for rid in ("R029", "R033", "R034"):
        assert run.status(rid) == "REJECTED"
        assert run.effects(rid)["payment"] == 0
