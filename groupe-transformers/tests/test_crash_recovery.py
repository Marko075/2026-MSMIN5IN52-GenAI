"""Crash avant/après chaque effet : après reprise, exactement un effet de chaque type."""
import pytest

APPROVED = "R001"        # note nominale : 1 virement + 1 e-mail
COMPENSATED = "R037"     # adresse invalide : 1 virement + 1 remboursement, 0 e-mail

MAIN_POINTS = [
    "reception.before", "reception.after_commit",
    "extraction.before_effect", "extraction.after_effect", "extraction.after_commit",
    "controle.after_commit",
    "virement.before_effect", "virement.after_effect", "virement.after_commit",
    "notification.before_effect", "notification.after_effect", "notification.after_commit",
]


@pytest.mark.parametrize("point", MAIN_POINTS)
def test_protected_crash_gives_exactly_one_effect(make_run, point):
    run = make_run([APPROVED], crash_at=[point]).drain()
    assert run.crashes == 1
    assert run.status(APPROVED) == "DONE"
    effects = run.effects(APPROVED)
    assert effects["payment"] == 1
    assert effects["email"] == 1


@pytest.mark.parametrize("point", ["compensation.before_effect", "compensation.after_effect",
                                   "virement.after_effect", "notification.before_effect"])
def test_compensation_survives_crash(make_run, point):
    run = make_run([COMPENSATED], crash_at=[point]).drain()
    assert run.crashes == 1
    assert run.status(COMPENSATED) == "COMPENSATED"
    effects = run.effects(COMPENSATED)
    assert (effects["payment"], effects["refund"], effects["email"]) == (1, 1, 0)


def test_several_crashes_in_one_request(make_run):
    points = ["extraction.after_effect", "virement.after_effect", "notification.after_effect"]
    run = make_run([APPROVED], crash_at=points).drain()
    assert run.crashes == 3
    assert run.effects(APPROVED)["payment"] == 1
    assert run.effects(APPROVED)["email"] == 1


def test_resume_is_logged(make_run):
    run = make_run([APPROVED], crash_at=["virement.after_effect"]).drain()
    resumed = run.events("request_resumed")
    assert resumed and "controle" in resumed[0]["steps_done"]
    assert run.events("idempotent_replay"), "le 2e appel au paiement doit être rejoué, pas ré-exécuté"


@pytest.mark.parametrize("point,kind", [("virement.after_effect", "payment"),
                                        ("notification.after_effect", "email")])
def test_naive_baseline_duplicates_effect(make_run, point, kind):
    """Baseline : le même crash produit un effet en double sans persistance ni clé d'idempotence."""
    run = make_run([APPROVED], mode="naive", crash_at=[point]).drain()
    assert run.crashes == 1
    assert run.effects(APPROVED)[kind] == 2


def test_llm_cache_avoids_second_call(make_run):
    run = make_run([APPROVED], crash_at=["extraction.after_effect"]).drain()
    assert len(run.events("llm_call")) == 1
    assert len(run.events("llm_cache_hit")) == 1


def test_naive_recalls_llm_after_crash(make_run):
    run = make_run([APPROVED], mode="naive", crash_at=["extraction.after_effect"]).drain()
    assert len(run.events("llm_call")) == 2
