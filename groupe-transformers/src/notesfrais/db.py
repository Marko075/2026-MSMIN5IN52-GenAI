"""Accès SQLite en mode WAL : base du workflow et base des services externes simulés."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

WORKFLOW_SCHEMA = """
CREATE TABLE IF NOT EXISTS inbox (
    msg_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  TEXT,
    payload     TEXT NOT NULL,
    received_at REAL NOT NULL,
    acked_at    REAL,
    outcome     TEXT
);
CREATE TABLE IF NOT EXISTS requests (
    request_id   TEXT PRIMARY KEY,
    payload      TEXT NOT NULL,
    status       TEXT NOT NULL,
    reason       TEXT,
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS steps (
    request_id  TEXT NOT NULL,
    step        TEXT NOT NULL,
    status      TEXT NOT NULL,
    output      TEXT,
    error       TEXT,
    attempts    INTEGER NOT NULL DEFAULT 0,
    started_at  REAL,
    finished_at REAL,
    PRIMARY KEY (request_id, step)
);
CREATE TABLE IF NOT EXISTS llm_cache (
    cache_key  TEXT PRIMARY KEY,
    model      TEXT NOT NULL,
    response   TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS fingerprints (
    fingerprint TEXT PRIMARY KEY,
    request_id  TEXT NOT NULL
);
"""

SERVICES_SCHEMA = """
CREATE TABLE IF NOT EXISTS idempotency_keys (
    service      TEXT NOT NULL,
    idem_key     TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    response     TEXT NOT NULL,
    created_at   REAL NOT NULL,
    PRIMARY KEY (service, idem_key)
);
CREATE TABLE IF NOT EXISTS effects (
    effect_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    service    TEXT NOT NULL,
    kind       TEXT NOT NULL,
    request_id TEXT NOT NULL,
    idem_key   TEXT,
    amount     REAL,
    ref        TEXT,
    created_at REAL NOT NULL,
    pid        INTEGER
);
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=30, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    # NORMAL en WAL : une transaction validée survit à un kill du processus (seule une coupure
    # de courant peut perdre les dernières transactions), et les commits restent rapides.
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


@contextmanager
def tx(conn: sqlite3.Connection):
    """Transaction explicite. Toute exception, y compris un crash simulé, annule la transaction."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def workflow_db(run_dir: Path) -> sqlite3.Connection:
    conn = connect(run_dir / "workflow.db")
    conn.executescript(WORKFLOW_SCHEMA)
    return conn


def services_db(run_dir: Path) -> sqlite3.Connection:
    conn = connect(run_dir / "services.db")
    conn.executescript(SERVICES_SCHEMA)
    return conn


def init_run_dbs(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    workflow_db(run_dir).close()
    services_db(run_dir).close()
