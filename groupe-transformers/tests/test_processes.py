"""Vrais processus : crash par os._exit et kill psutil, relance par le superviseur."""
from notesfrais.campaign import prepare_run, run_one
from notesfrais.chaos import ChaosMonkey
from notesfrais.dataset import load_requests
from notesfrais.journal import Journal
from notesfrais.metrics import compute_metrics
from notesfrais.supervisor import Supervisor

from .conftest import quiet_config

SUBSET = [r for r in load_requests() if r["request_id"] in {"R001", "R002", "R037"}]


def test_real_process_crash_in_critical_window(tmp_path):
    cfg = quiet_config(crash_at=["virement.after_effect", "notification.after_effect"])
    prepare_run(tmp_path, cfg, requests=SUBSET, dup_rate=0.0)
    result = Supervisor(tmp_path).run(timeout=120)
    assert result["status"] == "finished"
    assert result["restarts"] == 2
    m = compute_metrics(tmp_path, "protected")
    assert m["completion_rate"] == 1.0
    assert m["duplicate_effects"] == 0
    assert m["inconsistent_requests"] == 0


def test_chaos_kills_protected_run(tmp_path):
    cfg = quiet_config(service_latency=(0.01, 0.03), llm_latency=(0.01, 0.03))
    m = run_one(tmp_path / "run", cfg, n_requests=12, kill_interval=(0.2, 0.6), timeout=180)
    assert m["supervisor"]["status"] == "finished"
    assert m["crashes"] >= 1
    assert m["completion_rate"] == 1.0
    assert m["duplicate_effects"] == 0
    assert m["recovery_s"]["n"] >= 1
