"""Outils de test : runs in-process, sans réseau, sans latence, pannes scriptées."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from notesfrais.campaign import prepare_run
from notesfrais.config import RunConfig
from notesfrais.dataset import load_requests
from notesfrais.engine import build_engine
from notesfrais.faults import SimulatedCrash
from notesfrais.journal import read_journal
from notesfrais.metrics import effect_counts, final_statuses

REQUESTS = {r["request_id"]: r for r in load_requests()}


def quiet_config(mode: str = "protected", crash_at: list[str] | None = None, **overrides) -> RunConfig:
    """Aucune panne aléatoire, aucune latence : seules les pannes scriptées du test se produisent."""
    params = dict(mode=mode, seed=1, service_latency=(0.0, 0.0), llm_latency=(0.0, 0.0), p_service_error=0.0,
                  p_service_timeout_after=0.0, p_llm_invalid_json=0.0, p_llm_unavailable=0.0,
                  crash_at=crash_at or [], retry_base_delay=0.0, retry_max_delay=0.0)
    params.update(overrides)
    return RunConfig(**params)


class Run:
    def __init__(self, run_dir: Path, cfg: RunConfig, script: dict | None = None):
        self.dir = run_dir
        self.cfg = cfg
        self.script = script if script is not None else {}
        self.crashes = 0

    def drain(self, max_crashes: int = 50) -> "Run":
        """Fait tourner des « workers » successifs jusqu'à file vide ; un crash simulé = un redémarrage."""
        while True:
            engine = build_engine(self.dir, self.cfg, hard_crash=False, fault_script=self.script)
            try:
                while engine.tick():
                    pass
                return self
            except SimulatedCrash:
                self.crashes += 1
                assert self.crashes <= max_crashes
            finally:
                engine.conn.close()
                engine.d.payment.conn.close()

    def effects(self, rid: str) -> Counter:
        return effect_counts(self.dir).get(rid, Counter())

    def status(self, rid: str) -> str | None:
        return final_statuses(self.dir, self.cfg.mode).get(rid)

    def events(self, name: str) -> list[dict]:
        return [e for e in read_journal(self.dir) if e.get("event") == name]


@pytest.fixture
def make_run(tmp_path):
    counter = {"n": 0}

    def _make(ids: list[str] | None = None, mode: str = "protected", crash_at: list[str] | None = None,
              script: dict | None = None, deliveries: int = 1, **overrides) -> Run:
        counter["n"] += 1
        run_dir = tmp_path / f"run{counter['n']}"
        cfg = quiet_config(mode, crash_at, **overrides)
        reqs = [REQUESTS[i] for i in ids] if ids else list(REQUESTS.values())
        prepare_run(run_dir, cfg, requests=reqs, dup_rate=0.0)
        if deliveries > 1:
            from notesfrais.dataset import payload_of, submit
            submit(run_dir, [payload_of(r) for r in reqs] * (deliveries - 1))
        return Run(run_dir, cfg, script)

    return _make
