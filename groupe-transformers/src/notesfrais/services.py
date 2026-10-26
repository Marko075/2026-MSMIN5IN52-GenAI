"""Services externes factices : paiement (style Stripe) et e-mail, avec clés d'idempotence.

Ils écrivent dans `services.db`, une base distincte de celle du workflow : comme un vrai service
distant, leur effet ne participe pas à la transaction du worker. Chaque effet est inscrit dans le
registre `effects`, ce qui permet de compter les doublons.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import time

from .db import tx
from .faults import FaultInjector, PermanentError, TransientError


class ServiceTimeout(TransientError):
    pass


class ServiceUnavailable(TransientError):
    pass


class IdempotencyConflict(PermanentError):
    """Même clé, paramètres différents : comme Stripe, on refuse."""


def _request_hash(params: dict) -> str:
    return hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()


class _FakeService:
    name = "service"

    def __init__(self, conn: sqlite3.Connection, faults: FaultInjector, rng: random.Random,
                 latency: tuple[float, float] = (0.0, 0.0), journal=None):
        self.conn = conn
        self.faults = faults
        self.rng = rng
        self.latency = latency
        self.journal = journal

    def _sleep(self) -> None:
        low, high = self.latency
        if high > 0:
            time.sleep(self.rng.uniform(low, high))

    def _log(self, event: str, **fields) -> None:
        if self.journal is not None:
            self.journal.write(event, service=self.name, **fields)

    def _apply(self, kind: str, request_id: str, idem_key: str | None, params: dict,
               make_response) -> dict:
        """Applique un effet. Avec une clé déjà vue : renvoie la réponse enregistrée, sans nouvel effet."""
        fault = self.faults.draw(self.name)
        self._sleep()
        if fault == "error_500":
            self._log("fault_injected", request_id=request_id, fault=fault)
            raise ServiceUnavailable(f"{self.name}: HTTP 500")
        req_hash = _request_hash(params)
        with tx(self.conn):
            if idem_key is not None:
                row = self.conn.execute(
                    "SELECT request_hash, response FROM idempotency_keys WHERE service=? AND idem_key=?",
                    (self.name, idem_key)).fetchone()
                if row is not None:
                    if row["request_hash"] != req_hash:
                        raise IdempotencyConflict(f"clé {idem_key} réutilisée avec d'autres paramètres")
                    replayed = True
                    response = json.loads(row["response"])
                else:
                    replayed = False
            else:
                replayed = False
            if not replayed:
                cur = self.conn.execute(
                    "INSERT INTO effects(service, kind, request_id, idem_key, amount, ref, created_at, pid)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (self.name, kind, request_id, idem_key, params.get("amount"), params.get("ref"),
                     time.time(), os.getpid()))
                response = make_response(cur.lastrowid)
                if idem_key is not None:
                    self.conn.execute(
                        "INSERT INTO idempotency_keys(service, idem_key, request_hash, response, created_at)"
                        " VALUES (?,?,?,?,?)",
                        (self.name, idem_key, req_hash, json.dumps(response), time.time()))
        if replayed:
            self._log("idempotent_replay", request_id=request_id, kind=kind, idem_key=idem_key)
        else:
            self._log("effect_applied", request_id=request_id, kind=kind, idem_key=idem_key,
                      effect_id=response.get("id"))
        # Latence de la réponse : un kill ici tombe dans la fenêtre critique (effet fait, réponse perdue).
        self._sleep()
        if fault == "timeout_after":
            self._log("fault_injected", request_id=request_id, fault=fault)
            raise ServiceTimeout(f"{self.name}: timeout après application de l'effet")
        return response


class PaymentService(_FakeService):
    name = "payment"

    def charge(self, idem_key: str | None, request_id: str, amount: float, beneficiary: str) -> dict:
        params = {"op": "charge", "request_id": request_id, "amount": round(amount, 2), "ref": beneficiary}
        return self._apply("payment", request_id, idem_key, params,
                           lambda eid: {"id": f"pay_{eid}", "status": "succeeded", "amount": round(amount, 2)})

    def refund(self, idem_key: str | None, request_id: str, payment_id: str, amount: float) -> dict:
        params = {"op": "refund", "request_id": request_id, "amount": round(amount, 2), "ref": payment_id}
        return self._apply("refund", request_id, idem_key, params,
                           lambda eid: {"id": f"ref_{eid}", "status": "refunded", "payment_id": payment_id})

    def lookup(self, idem_key: str) -> dict | None:
        """Réconciliation : retrouve un paiement par sa clé (utile si les retries ont été épuisés)."""
        row = self.conn.execute("SELECT response FROM idempotency_keys WHERE service=? AND idem_key=?",
                                (self.name, idem_key)).fetchone()
        return json.loads(row["response"]) if row else None


class EmailService(_FakeService):
    name = "email"

    def send(self, idem_key: str | None, request_id: str, to: str, subject: str) -> dict:
        domain = to.rsplit("@", 1)[-1] if "@" in to else ""
        if not domain or domain.endswith(".invalid"):
            # Erreur définitive (boîte inexistante) : aucun effet, inutile de réessayer.
            self._log("permanent_error", request_id=request_id, error="adresse invalide")
            raise PermanentError(f"adresse e-mail invalide pour {request_id}")
        params = {"op": "send", "request_id": request_id, "ref": to, "subject": subject}
        return self._apply("email", request_id, idem_key, params,
                           lambda eid: {"id": f"msg_{eid}", "status": "sent"})


def service_fault_probabilities(p_error: float, p_timeout_after: float) -> list[tuple[str, float]]:
    return [("error_500", p_error), ("timeout_after", p_timeout_after)]
