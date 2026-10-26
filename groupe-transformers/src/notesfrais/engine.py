"""Moteur du workflow en 5 étapes, en deux variantes.

- `ProtectedEngine` : chaque étape est persistée (table `steps`), chaque effet externe porte une clé
  d'idempotence, la réponse du LLM est mise en cache, et un worker relancé reprend à la première
  étape non terminée. Si la notification échoue définitivement, le virement est compensé.
- `NaiveEngine` (baseline) : le même pipeline et les mêmes retries, mais sans état d'étape ni clé
  d'idempotence ; le message n'est acquitté qu'en fin de traitement (livraison at-least-once).
"""
from __future__ import annotations

import json
import os
import random
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import STEPS
from .config import RunConfig
from .db import services_db, tx, workflow_db
from .faults import CrashController, FaultInjector, PermanentError
from .journal import Journal
from .llm import (InvalidLLMOutput, ReplayLLM, SemanticKernelLLM, SimulatedLLM, cache_key,
                  llm_fault_probabilities, parse_extraction)
from .retry import RetryExhausted, RetryPolicy, call_with_retry
from .rules import apply_rules, fingerprint
from .services import EmailService, PaymentService, service_fault_probabilities

REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")


@dataclass
class Deps:
    run_dir: Path
    cfg: RunConfig
    journal: Journal
    llm: object
    payment: PaymentService
    email: EmailService
    crash: CrashController
    rng: random.Random
    policy: RetryPolicy


def validate_payload(payload: dict) -> list[str]:
    errors = []
    if not REQUEST_ID_RE.match(str(payload.get("request_id") or "")):
        errors.append("request_id manquant ou invalide")
    if not str(payload.get("texte") or "").strip():
        errors.append("texte vide")
    elif len(payload["texte"]) > 2000:
        errors.append("texte trop long")
    if not payload.get("employe"):
        errors.append("employé manquant")
    if "@" not in str(payload.get("email") or ""):
        errors.append("e-mail manquant")
    return errors


class BaseEngine:
    mode = "base"

    def __init__(self, conn: sqlite3.Connection, deps: Deps):
        self.conn = conn
        self.d = deps
        self.journal = deps.journal

    # -- outils communs -------------------------------------------------------------------------
    def _call(self, rid: str, step: str, fn: Callable):
        def on_retry(attempt: int, exc: Exception, delay: float) -> None:
            self.journal.write("retry", request_id=rid, step=step, attempt=attempt, error=str(exc),
                               delay_ms=round(delay * 1000, 1))
        return call_with_retry(fn, self.d.policy, self.d.rng, on_retry=on_retry)

    def _llm_once(self, rid: str, text: str, hint: str | None):
        def call():
            self.journal.write("llm_call", request_id=rid, step="extraction", model=self.d.llm.model,
                               real=bool(getattr(self.d.llm, "real", False)), repair=hint is not None)
            return self.d.llm.complete(text, hint, rid)
        return self._call(rid, "extraction", call)

    def _extract(self, rid: str, text: str) -> dict:
        """Appel LLM + validation par schéma ; une seule tentative de réparation si le JSON est faux."""
        raw = self._llm_once(rid, text, None)
        try:
            return parse_extraction(raw)
        except InvalidLLMOutput as exc:
            self.journal.write("llm_invalid_output", request_id=rid, step="extraction", error=str(exc))
            return parse_extraction(self._llm_once(rid, text, str(exc)))

    def _point(self, name: str, rid: str | None) -> None:
        self.d.crash.point(name, rid)

    def tick(self) -> bool:  # pragma: no cover - interface
        raise NotImplementedError


# ================================================================================ mode protégé

class ProtectedEngine(BaseEngine):
    mode = "protected"

    def __init__(self, conn, deps):
        super().__init__(conn, deps)
        self._seen: set[str] = set()

    # -- accès à l'état ------------------------------------------------------------------------
    def _request(self, rid: str) -> sqlite3.Row:
        return self.conn.execute("SELECT * FROM requests WHERE request_id=?", (rid,)).fetchone()

    def _step(self, rid: str, step: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM steps WHERE request_id=? AND step=?", (rid, step)).fetchone()

    def _output(self, rid: str, step: str):
        row = self._step(rid, step)
        return json.loads(row["output"]) if row is not None and row["output"] else None

    def _put_step(self, rid: str, step: str, status: str, output=None, error: str | None = None) -> None:
        now = time.time()
        self.conn.execute(
            "INSERT INTO steps(request_id, step, status, output, error, attempts, started_at, finished_at)"
            " VALUES (?,?,?,?,?,0,?,?) ON CONFLICT(request_id, step) DO UPDATE SET status=excluded.status,"
            " output=COALESCE(excluded.output, steps.output), error=excluded.error, finished_at=excluded.finished_at",
            (rid, step, status, None if output is None else json.dumps(output, ensure_ascii=False), error, now, now))

    def _set_status(self, rid: str, status: str, reason: str | None = None) -> None:
        self.conn.execute("UPDATE requests SET status=?, reason=COALESCE(?, reason), updated_at=? WHERE request_id=?",
                          (status, reason, time.time(), rid))

    def _begin(self, rid: str, step: str) -> float:
        now = time.time()
        with tx(self.conn):
            self.conn.execute(
                "INSERT INTO steps(request_id, step, status, attempts, started_at) VALUES (?,?,'RUNNING',1,?)"
                " ON CONFLICT(request_id, step) DO UPDATE SET status='RUNNING', attempts=steps.attempts+1,"
                " started_at=excluded.started_at", (rid, step, now))
        attempts = self._step(rid, step)["attempts"]
        self.journal.write("step_start", request_id=rid, step=step, attempt=attempts)
        return now

    def _done(self, rid: str, step: str, t0: float, output=None, then: Callable[[], None] | None = None,
              **extra) -> None:
        with tx(self.conn):
            self._put_step(rid, step, "DONE", output)
            if then is not None:
                then()
        self.journal.write("step_done", request_id=rid, step=step, duration_ms=(time.time() - t0) * 1000, **extra)

    def _final(self, rid: str, status: str, reason: str | None = None) -> None:
        self.journal.write("request_final", request_id=rid, status=status, reason=reason)

    # -- boucle ----------------------------------------------------------------------------------
    def tick(self) -> bool:
        row = self.conn.execute("SELECT request_id FROM requests WHERE status IN ('RUNNING','COMPENSATING')"
                                " ORDER BY created_at LIMIT 1").fetchone()
        if row is not None:
            self.run_request(row["request_id"])
            return True
        msg = self.conn.execute("SELECT * FROM inbox WHERE acked_at IS NULL ORDER BY msg_id LIMIT 1").fetchone()
        if msg is None:
            return False
        rid = self.receive(msg)
        if rid is not None:
            self.run_request(rid)
        return True

    # -- étape 1 : réception et dédoublonnage ----------------------------------------------------
    def receive(self, msg: sqlite3.Row) -> str | None:
        t0 = time.time()
        payload = json.loads(msg["payload"])
        rid = str(payload.get("request_id") or f"MSG{msg['msg_id']}")
        self._point("reception.before", rid)
        errors = validate_payload(payload)
        with tx(self.conn):
            exists = self.conn.execute("SELECT 1 FROM requests WHERE request_id=?", (rid,)).fetchone()
            if exists:
                outcome = "duplicate_ignored"
            else:
                outcome = "rejected" if errors else "accepted"
                now = time.time()
                self.conn.execute(
                    "INSERT INTO requests(request_id, payload, status, reason, created_at, updated_at)"
                    " VALUES (?,?,?,?,?,?)",
                    (rid, msg["payload"], "REJECTED" if errors else "RUNNING", "; ".join(errors) or None, now, now))
                self._put_step(rid, "reception", "FAILED" if errors else "DONE",
                               {"errors": errors}, "; ".join(errors) or None)
            self.conn.execute("UPDATE inbox SET acked_at=?, outcome=? WHERE msg_id=?",
                              (time.time(), outcome, msg["msg_id"]))
        if outcome == "duplicate_ignored":
            self.journal.write("duplicate_ignored", request_id=rid, step="reception", msg_id=msg["msg_id"])
            return None
        self.journal.write("request_start", request_id=rid)
        if errors:
            self.journal.write("step_failed", request_id=rid, step="reception", error="; ".join(errors))
            self._final(rid, "REJECTED", "; ".join(errors))
            return None
        self.journal.write("step_done", request_id=rid, step="reception", duration_ms=(time.time() - t0) * 1000)
        self._point("reception.after_commit", rid)
        return rid

    # -- orchestration d'une demande -------------------------------------------------------------
    def run_request(self, rid: str) -> None:
        if rid not in self._seen:
            self._seen.add(rid)
            done = [r["step"] for r in self.conn.execute(
                "SELECT step FROM steps WHERE request_id=? AND status IN ('DONE','SKIPPED','FAILED')", (rid,))]
            if done != ["reception"] or self.conn.execute(
                    "SELECT 1 FROM steps WHERE request_id=? AND status='RUNNING'", (rid,)).fetchone():
                self.journal.write("request_resumed", request_id=rid, steps_done=done)
        if self._request(rid)["status"] == "RUNNING":
            for step in STEPS[1:]:
                row = self._step(rid, step)
                if row is not None and row["status"] in ("DONE", "SKIPPED", "FAILED"):
                    continue
                if getattr(self, f"_do_{step}")(rid) == "suspend":
                    return
                if self._request(rid)["status"] != "RUNNING":
                    break
        if self._request(rid)["status"] == "COMPENSATING":
            self._do_compensation(rid)

    def _suspend(self, rid: str, step: str, error: str) -> str:
        with tx(self.conn):
            self._put_step(rid, step, "PENDING", error=error)
            self._set_status(rid, "SUSPENDED", f"{step} : {error}")
        self.journal.write("request_suspended", request_id=rid, step=step, error=error)
        return "suspend"

    # -- étape 2 : extraction LLM (avec cache) ---------------------------------------------------
    def _do_extraction(self, rid: str):
        t0 = self._begin(rid, "extraction")
        text = json.loads(self._request(rid)["payload"])["texte"]
        key = cache_key(self.d.llm.model, text)
        cached = self.conn.execute("SELECT response FROM llm_cache WHERE cache_key=?", (key,)).fetchone()
        if cached is not None:
            expense = json.loads(cached["response"])
            self.journal.write("llm_cache_hit", request_id=rid, step="extraction")
        else:
            self._point("extraction.before_effect", rid)
            try:
                expense = self._extract(rid, text)
            except InvalidLLMOutput as exc:
                with tx(self.conn):
                    self._put_step(rid, "extraction", "FAILED", error=str(exc))
                    self._put_step(rid, "controle", "SKIPPED")
                    self._put_step(rid, "virement", "SKIPPED")
                    self._set_status(rid, "RUNNING", f"extraction invalide : {exc}")
                self.journal.write("step_failed", request_id=rid, step="extraction", error=str(exc))
                return None
            except (RetryExhausted, PermanentError) as exc:
                return self._suspend(rid, "extraction", f"LLM indisponible : {exc}")
            with tx(self.conn):
                self.conn.execute("INSERT OR REPLACE INTO llm_cache(cache_key, model, response, created_at)"
                                  " VALUES (?,?,?,?)", (key, self.d.llm.model, json.dumps(expense), time.time()))
        self._point("extraction.after_effect", rid)
        self._done(rid, "extraction", t0, expense)
        self._point("extraction.after_commit", rid)
        return None

    # -- étape 3 : contrôle ---------------------------------------------------------------------
    def _do_controle(self, rid: str):
        t0 = self._begin(rid, "controle")
        expense = self._output(rid, "extraction")
        employee = json.loads(self._request(rid)["payload"])["employe"]
        result = apply_rules(expense)
        fp = fingerprint(employee, expense)

        def persist():
            if result["decision"] == "APPROVED":
                other = self.conn.execute("SELECT request_id FROM fingerprints WHERE fingerprint=?", (fp,)).fetchone()
                if other is not None and other["request_id"] != rid:
                    result["decision"] = "REJECTED"
                    result["reasons"].append(f"doublon métier de {other['request_id']}")
                elif other is None:
                    self.conn.execute("INSERT INTO fingerprints(fingerprint, request_id) VALUES (?,?)", (fp, rid))
            self._put_step(rid, "controle", "DONE", result)
            if result["decision"] == "REJECTED":
                self._put_step(rid, "virement", "SKIPPED")
                self._set_status(rid, "RUNNING", "; ".join(result["reasons"]))

        self._done(rid, "controle", t0, None, then=persist)
        self.journal.write("decision", request_id=rid, step="controle", decision=result["decision"],
                           reasons=result["reasons"])
        self._point("controle.after_commit", rid)
        return None

    # -- étape 4 : virement (effet externe, clé d'idempotence) ----------------------------------
    def _do_virement(self, rid: str):
        t0 = self._begin(rid, "virement")
        control = self._output(rid, "controle")
        employee = json.loads(self._request(rid)["payload"])["employe"]
        key = f"{rid}:virement"
        self._point("virement.before_effect", rid)
        try:
            payment = self._call(rid, "virement",
                                 lambda: self.d.payment.charge(key, rid, control["amount_eur"], employee))
        except (RetryExhausted, PermanentError) as exc:
            # Réconciliation : grâce à la clé, on sait si le paiement a eu lieu malgré l'échec apparent.
            existing = self.d.payment.lookup(key)
            with tx(self.conn):
                self._put_step(rid, "virement", "FAILED", existing, str(exc))
                if existing:
                    self._set_status(rid, "COMPENSATING", f"virement incertain : {exc}")
                else:
                    self._set_status(rid, "FAILED", f"virement impossible : {exc}")
            self.journal.write("step_failed", request_id=rid, step="virement", error=str(exc))
            if not existing:
                self._final(rid, "FAILED", str(exc))
            return None
        self._point("virement.after_effect", rid)  # fenêtre critique : effet fait, étape non marquée
        self._done(rid, "virement", t0, payment, payment_id=payment["id"])
        self._point("virement.after_commit", rid)
        return None

    # -- étape 5 : notification (effet externe, clé d'idempotence) ------------------------------
    def _do_notification(self, rid: str):
        t0 = self._begin(rid, "notification")
        request = self._request(rid)
        payload = json.loads(request["payload"])
        approved = (self._step(rid, "virement") or {"status": None})["status"] == "DONE"
        subject = "Note de frais remboursée" if approved else "Note de frais refusée"
        key = f"{rid}:notification"
        self._point("notification.before_effect", rid)
        try:
            self._call(rid, "notification", lambda: self.d.email.send(key, rid, payload["email"], subject))
        except (RetryExhausted, PermanentError) as exc:
            with tx(self.conn):
                self._put_step(rid, "notification", "FAILED", error=str(exc))
                if approved:
                    self._set_status(rid, "COMPENSATING", f"notification impossible : {exc}")
                else:
                    self._set_status(rid, "REJECTED")
            self.journal.write("step_failed", request_id=rid, step="notification", error=str(exc))
            if not approved:
                self._final(rid, "REJECTED", request["reason"])
            return None
        self._point("notification.after_effect", rid)
        final = "DONE" if approved else "REJECTED"
        self._done(rid, "notification", t0, None, then=lambda: self._set_status(rid, final))
        self._final(rid, final, request["reason"])
        self._point("notification.after_commit", rid)
        return None

    # -- compensation : annulation du virement --------------------------------------------------
    def _do_compensation(self, rid: str):
        t0 = self._begin(rid, "compensation")
        payment = self._output(rid, "virement") or self.d.payment.lookup(f"{rid}:virement")
        self._point("compensation.before_effect", rid)
        refund = None
        if payment:
            try:
                refund = self._call(rid, "compensation", lambda: self.d.payment.refund(
                    f"{rid}:compensation", rid, payment["id"], payment["amount"]))
            except (RetryExhausted, PermanentError) as exc:
                return self._suspend(rid, "compensation", str(exc))
        self._point("compensation.after_effect", rid)
        self._done(rid, "compensation", t0, refund, then=lambda: self._set_status(rid, "COMPENSATED"))
        self._final(rid, "COMPENSATED", self._request(rid)["reason"])
        return None


# ================================================================================ mode naïf

class NaiveEngine(BaseEngine):
    mode = "naive"

    def __init__(self, conn, deps):
        super().__init__(conn, deps)
        self._fingerprints: set[str] = set()  # en mémoire : perdu à chaque crash

    def tick(self) -> bool:
        msg = self.conn.execute("SELECT * FROM inbox WHERE acked_at IS NULL ORDER BY msg_id LIMIT 1").fetchone()
        if msg is None:
            return False
        self.process(msg)
        return True

    def _ack(self, msg, rid: str, outcome: str, reason: str | None = None) -> None:
        with tx(self.conn):
            self.conn.execute("UPDATE inbox SET acked_at=?, outcome=? WHERE msg_id=?",
                              (time.time(), outcome, msg["msg_id"]))
        self.journal.write("request_final", request_id=rid, status=outcome, reason=reason)

    def _step_done(self, rid, step, t0, **extra):
        self.journal.write("step_done", request_id=rid, step=step, duration_ms=(time.time() - t0) * 1000, **extra)

    def process(self, msg) -> None:
        payload = json.loads(msg["payload"])
        rid = str(payload.get("request_id") or f"MSG{msg['msg_id']}")
        self.journal.write("request_start", request_id=rid, msg_id=msg["msg_id"])
        # 1. réception : validation seulement, aucun dédoublonnage
        t0 = time.time()
        self.journal.write("step_start", request_id=rid, step="reception")
        self._point("reception.before", rid)
        errors = validate_payload(payload)
        if errors:
            self.journal.write("step_failed", request_id=rid, step="reception", error="; ".join(errors))
            self._ack(msg, rid, "REJECTED", "; ".join(errors))
            return
        self._step_done(rid, "reception", t0)
        self._point("reception.after_commit", rid)
        # 2. extraction : pas de cache
        t0 = time.time()
        self.journal.write("step_start", request_id=rid, step="extraction")
        self._point("extraction.before_effect", rid)
        reason = None
        try:
            expense = self._extract(rid, payload["texte"])
        except InvalidLLMOutput as exc:
            expense, reason = None, f"extraction invalide : {exc}"
            self.journal.write("step_failed", request_id=rid, step="extraction", error=str(exc))
        except (RetryExhausted, PermanentError) as exc:
            self._ack(msg, rid, "FAILED", f"LLM indisponible : {exc}")
            return
        self._point("extraction.after_effect", rid)
        if expense is not None:
            self._step_done(rid, "extraction", t0)
        self._point("extraction.after_commit", rid)
        # 3. contrôle
        approved, amount = False, 0.0
        if expense is not None:
            t0 = time.time()
            self.journal.write("step_start", request_id=rid, step="controle")
            result = apply_rules(expense)
            fp = fingerprint(payload["employe"], expense)
            if result["decision"] == "APPROVED" and fp in self._fingerprints:
                result["decision"] = "REJECTED"
                result["reasons"].append("doublon métier")
            if result["decision"] == "APPROVED":
                self._fingerprints.add(fp)
            approved, amount = result["decision"] == "APPROVED", result["amount_eur"]
            reason = "; ".join(result["reasons"]) or None
            self._step_done(rid, "controle", t0, decision=result["decision"])
            self._point("controle.after_commit", rid)
        # 4. virement : sans clé d'idempotence
        payment = None
        if approved:
            t0 = time.time()
            self.journal.write("step_start", request_id=rid, step="virement")
            self._point("virement.before_effect", rid)
            try:
                payment = self._call(rid, "virement",
                                     lambda: self.d.payment.charge(None, rid, amount, payload["employe"]))
            except (RetryExhausted, PermanentError) as exc:
                self.journal.write("step_failed", request_id=rid, step="virement", error=str(exc))
                self._ack(msg, rid, "FAILED", str(exc))
                return
            self._point("virement.after_effect", rid)
            self._step_done(rid, "virement", t0, payment_id=payment["id"])
            self._point("virement.after_commit", rid)
        # 5. notification : sans clé d'idempotence
        t0 = time.time()
        self.journal.write("step_start", request_id=rid, step="notification")
        subject = "Note de frais remboursée" if approved else "Note de frais refusée"
        self._point("notification.before_effect", rid)
        try:
            self._call(rid, "notification", lambda: self.d.email.send(None, rid, payload["email"], subject))
        except (RetryExhausted, PermanentError) as exc:
            self.journal.write("step_failed", request_id=rid, step="notification", error=str(exc))
            if payment is None:
                self._ack(msg, rid, "REJECTED", reason)
                return
            self.journal.write("step_start", request_id=rid, step="compensation")
            self._point("compensation.before_effect", rid)
            try:
                self._call(rid, "compensation",
                           lambda: self.d.payment.refund(None, rid, payment["id"], payment["amount"]))
            except (RetryExhausted, PermanentError) as exc2:
                self._ack(msg, rid, "FAILED", f"compensation impossible : {exc2}")
                return
            self._point("compensation.after_effect", rid)
            self.journal.write("step_done", request_id=rid, step="compensation")
            self._ack(msg, rid, "COMPENSATED", f"notification impossible : {exc}")
            return
        self._point("notification.after_effect", rid)
        self._step_done(rid, "notification", t0)
        self._ack(msg, rid, "DONE" if approved else "REJECTED", reason)
        self._point("notification.after_commit", rid)


# ================================================================================ fabrique

def build_engine(run_dir: Path, cfg: RunConfig | None = None, hard_crash: bool = True, llm=None,
                 fault_script: dict | None = None, journal: Journal | None = None) -> BaseEngine:
    from .dataset import load_requests, truth_table

    run_dir = Path(run_dir)
    cfg = cfg or RunConfig.load(run_dir)
    # Graine différente à chaque processus en campagne (sinon chaque redémarrage rejouerait les mêmes pannes).
    rng = random.Random(cfg.seed if not hard_crash else f"{cfg.seed}-{os.getpid()}-{time.time_ns()}")
    journal = journal or Journal(run_dir, "worker", mode=cfg.mode)
    service_probs = service_fault_probabilities(cfg.p_service_error, cfg.p_service_timeout_after)
    faults = FaultInjector(rng, {"payment": service_probs, "email": service_probs,
                                 "llm": llm_fault_probabilities(cfg.p_llm_invalid_json, cfg.p_llm_unavailable)},
                           fault_script)
    sconn = services_db(run_dir)
    if llm is None:
        if cfg.llm == "real":
            llm = SemanticKernelLLM()
        elif cfg.llm == "replay":
            llm = ReplayLLM(truth_table(load_requests()), faults, rng, cfg.llm_latency)
        else:
            llm = SimulatedLLM(truth_table(load_requests()), faults, rng, cfg.llm_latency)
    deps = Deps(
        run_dir=run_dir, cfg=cfg, journal=journal, llm=llm,
        payment=PaymentService(sconn, faults, rng, cfg.service_latency, journal),
        email=EmailService(sconn, faults, rng, cfg.service_latency, journal),
        crash=CrashController(run_dir, cfg.crash_at, cfg.crash_prob, rng, hard_crash, journal),
        rng=rng,
        policy=RetryPolicy(cfg.retry_attempts, cfg.retry_base_delay, cfg.retry_max_delay),
    )
    cls = ProtectedEngine if cfg.mode == "protected" else NaiveEngine
    return cls(workflow_db(run_dir), deps)
