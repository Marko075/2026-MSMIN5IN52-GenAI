"""Étape 3 : règles de contrôle simulées (plafonds, dates, conversion de devises)."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta

from .config import REFERENCE_DATE

# Plafonds par catégorie, en euros (politique de frais fictive).
CEILINGS_EUR = {"repas": 40.0, "transport": 250.0, "hebergement": 180.0, "materiel": 400.0, "autre": 100.0}
# Taux de change fixes et fictifs : le contrôle doit être déterministe.
FX_TO_EUR = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17, "CHF": 1.05}
MAX_AGE_DAYS = 90


def amount_eur(expense: dict) -> float:
    return round(float(expense["montant"]) * FX_TO_EUR[expense["devise"]], 2)


def fingerprint(employee: str, expense: dict) -> str:
    """Empreinte métier : deux demandes différentes pour la même dépense ont la même empreinte."""
    key = f"{employee}|{float(expense['montant']):.2f}|{expense['devise']}|{expense['date']}|{expense['categorie']}"
    return hashlib.sha256(key.encode()).hexdigest()[:24]


def apply_rules(expense: dict, reference: date = REFERENCE_DATE) -> dict:
    reasons: list[str] = []
    eur = amount_eur(expense)
    ceiling = CEILINGS_EUR[expense["categorie"]]
    if eur > ceiling:
        reasons.append(f"plafond {expense['categorie']} dépassé ({eur:.2f} € > {ceiling:.0f} €)")
    spent = date.fromisoformat(str(expense["date"]))
    if spent > reference:
        reasons.append(f"date future ({spent.isoformat()})")
    elif spent < reference - timedelta(days=MAX_AGE_DAYS):
        reasons.append(f"dépense de plus de {MAX_AGE_DAYS} jours ({spent.isoformat()})")
    return {"decision": "REJECTED" if reasons else "APPROVED", "reasons": reasons, "amount_eur": eur}
