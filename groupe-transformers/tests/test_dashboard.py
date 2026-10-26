"""Le tableau de bord s'affiche sans exception."""
import sys
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

APP = str(Path(__file__).resolve().parents[1] / "src" / "notesfrais" / "dashboard.py")


def test_dashboard_live_page(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dashboard"])
    at = st_testing.AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("Lancer la campagne" in b.label for b in at.sidebar.button)
