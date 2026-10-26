"""Workflow résilient et idempotent de traitement de notes de frais (sujet B5)."""

STEPS = ["reception", "extraction", "controle", "virement", "notification"]
TERMINAL_STATUSES = {"DONE", "REJECTED", "COMPENSATED"}
