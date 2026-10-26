"""Le tableau de bord s'affiche sans exception, en direct comme en replay."""
import sys
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

from notesfrais.config import RESULTS_DIR  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "src" / "notesfrais" / "dashboard.py")


def test_dashboard_live_page(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dashboard"])
    at = st_testing.AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("Lancer la campagne" in b.label for b in at.sidebar.button)


@pytest.mark.skipif(not list((RESULTS_DIR / "recordings").glob("*.snapshots.jsonl")),
                    reason="aucun enregistrement de campagne")
def test_dashboard_replay_page(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dashboard", "--replay"])
    at = st_testing.AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("Rejouer" in b.label for b in at.sidebar.button)
