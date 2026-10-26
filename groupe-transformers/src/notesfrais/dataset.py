"""Jeu de 40 demandes synthétiques et construction des messages (avec doublons de livraison)."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from .config import DATA_DIR
from .db import tx, workflow_db
from .llm import text_key


def load_requests(path: Path = DATA_DIR / "requests.json") -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def truth_table(requests: list[dict]) -> dict[str, dict]:
    """Vérité terrain indexée par texte : c'est ce que « répond » le LLM simulé."""
    return {text_key(r["texte"]): r["attendu"] for r in requests if r.get("attendu")}


def payload_of(req: dict) -> dict:
    return {k: req[k] for k in ("request_id", "employe", "email", "texte")}


def build_messages(requests: list[dict], seed: int, dup_rate: float = 0.15) -> list[dict]:
    """Ordre mélangé + une partie des demandes livrée deux fois (même request_id)."""
    rng = random.Random(seed)
    messages = [payload_of(r) for r in requests]
    rng.shuffle(messages)
    for req in rng.sample(requests, k=round(len(requests) * dup_rate)):
        messages.insert(rng.randint(len(messages) // 3, len(messages)), payload_of(req))
    return messages


def submit(run_dir: Path, messages: list[dict]) -> int:
    conn = workflow_db(run_dir)
    with tx(conn):
        for msg in messages:
            conn.execute("INSERT INTO inbox(request_id, payload, received_at) VALUES (?,?,?)",
                         (msg.get("request_id"), json.dumps(msg, ensure_ascii=False), time.time()))
    conn.close()
    return len(messages)
