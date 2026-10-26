"""Génère data/requests.json : 40 notes de frais synthétiques (aucune donnée réelle)."""
import json
from pathlib import Path

# (id, employé, texte, montant, devise, catégorie, date, motif, scénario)
ROWS = [
    ("R001", "E01", "Déjeuner avec un client au restaurant le 12/10/2026 : 34,50 € TTC.", 34.50, "EUR", "repas", "2026-10-12", "Déjeuner client", "nominal"),
    ("R002", "E02", "Billet de train Paris-Lyon aller-retour pour le salon Industrie, payé 118 € le 5 octobre 2026.", 118, "EUR", "transport", "2026-10-05", "Train Paris-Lyon pour le salon Industrie", "nominal"),
    ("R003", "E03", "Nuit d'hôtel à Lille le 28/09/2026 pour l'audit fournisseur, facture de 96,00 euros.", 96, "EUR", "hebergement", "2026-09-28", "Hôtel à Lille pour l'audit fournisseur", "nominal"),
    ("R004", "E04", "Achat d'un clavier et d'une souris pour le poste de travail, 79,90 € le 2026-10-01.", 79.90, "EUR", "materiel", "2026-10-01", "Clavier et souris", "nominal"),
    ("R005", "E05", "Taxi from JFK airport to the office on 2026-09-15, 62.40 USD.", 62.40, "USD", "transport", "2026-09-15", "Taxi aéroport JFK - bureau", "nominal"),
    ("R006", "E06", "Repas d'équipe pour la fin du sprint, 38 € le 16 octobre 2026.", 38, "EUR", "repas", "2026-10-16", "Repas d'équipe fin de sprint", "nominal"),
    ("R007", "E07", "Plein d'essence pour la visite chantier à Rouen le 03/10/2026 : 71,25 €.", 71.25, "EUR", "transport", "2026-10-03", "Essence visite chantier Rouen", "nominal"),
    ("R008", "E08", "Hotel in London on 22/09/2026 for the partner workshop: 150 GBP.", 150, "GBP", "hebergement", "2026-09-22", "Hôtel à Londres pour l'atelier partenaire", "nominal"),
    ("R009", "E09", "Frais d'inscription à la conférence DevDays du 08/10/2026, 85 €.", 85, "EUR", "autre", "2026-10-08", "Inscription conférence DevDays", "nominal"),
    ("R010", "E10", "Dîner à Genève avec le partenaire le 30.09.2026, montant 36 CHF.", 36, "CHF", "repas", "2026-09-30", "Dîner partenaire à Genève", "nominal"),
    ("R011", "E11", "Ticket de parking aéroport du 14/10/2026, 24 €.", 24, "EUR", "transport", "2026-10-14", "Parking aéroport", "nominal"),
    ("R012", "E12", "Câble HDMI et adaptateur USB-C achetés le 9 octobre 2026 pour la salle de réunion : 32,99 €.", 32.99, "EUR", "materiel", "2026-10-09", "Câble HDMI et adaptateur USB-C", "nominal"),
    ("R013", "E01", "Vol Paris-Toulouse le 21/09/2026 pour la réunion projet, 189 €.", 189, "EUR", "transport", "2026-09-21", "Vol Paris-Toulouse réunion projet", "nominal"),
    ("R014", "E02", "Petit-déjeuner de travail le 19/10/2026, 18,60 €.", 18.60, "EUR", "repas", "2026-10-19", "Petit-déjeuner de travail", "nominal"),
    ("R015", "E03", "Abonnement mensuel à un outil de visioconférence, 29 € prélevés le 01/10/2026.", 29, "EUR", "autre", "2026-10-01", "Abonnement visioconférence", "nominal"),
    ("R016", "E04", "Deux nuits d'hôtel à Nantes, départ le 07/10/2026, total 172 €.", 172, "EUR", "hebergement", "2026-10-07", "Deux nuits d'hôtel à Nantes", "nominal"),
    ("R017", "E05", "Business lunch in Boston on 2026-09-16, 41.80 USD.", 41.80, "USD", "repas", "2026-09-16", "Déjeuner d'affaires à Boston", "nominal"),
    ("R018", "E06", "Forfait Navigo hebdomadaire du 13/10/2026 : 30,75 €.", 30.75, "EUR", "transport", "2026-10-13", "Navigo hebdomadaire", "nominal"),
    ("R019", "E07", "Casque audio pour les appels clients acheté le 25/09/2026 : 129 €.", 129, "EUR", "materiel", "2026-09-25", "Casque audio", "nominal"),
    ("R020", "E08", "Déjeuner pendant la formation le 06/10/2026, 22,40 €.", 22.40, "EUR", "repas", "2026-10-06", "Déjeuner formation", "nominal"),
    ("R021", "E09", "Location de voiture pour le déplacement à Bordeaux, 2 jours, 146 € le 29/09/2026.", 146, "EUR", "transport", "2026-09-29", "Location de voiture Bordeaux", "nominal"),
    ("R022", "E10", "Achat de livres techniques pour l'équipe le 11/10/2026, 64,30 €.", 64.30, "EUR", "autre", "2026-10-11", "Livres techniques", "nominal"),
    ("R023", "E11", "Nuit à l'hôtel près de la gare de Strasbourg le 15/10/2026, 89 €.", 89, "EUR", "hebergement", "2026-10-15", "Hôtel à Strasbourg", "nominal"),
    ("R024", "E12", "Repas pris sur la route lors du déplacement du 17/10/2026, 15,90 €.", 15.90, "EUR", "repas", "2026-10-17", "Repas en déplacement", "nominal"),
    ("R025", "E01", "Disque SSD externe de 1 To pour les sauvegardes, 99 € le 04/10/2026.", 99, "EUR", "materiel", "2026-10-04", "Disque SSD externe", "nominal"),
    ("R026", "E02", "Tickets de métro et de bus à Bruxelles pendant la mission du 24/09/2026, 18 €.", 18, "EUR", "transport", "2026-09-24", "Transports en commun à Bruxelles", "nominal"),
    ("R027", "E03", "Dîner client le 10/10/2026 au restaurant, 39,00 €.", 39, "EUR", "repas", "2026-10-10", "Dîner client", "nominal"),
    ("R028", "E04", "Péage autoroute A13 aller-retour le 02/10/2026, 27,60 €.", 27.60, "EUR", "transport", "2026-10-02", "Péage A13", "nominal"),
    ("R029", "E05", "Dîner de gala avec trois clients le 09/10/2026, addition de 212 €.", 212, "EUR", "repas", "2026-10-09", "Dîner de gala clients", "plafond"),
    ("R030", "E06", "Achat d'un ordinateur portable le 18/09/2026 pour un nouvel arrivant : 1249 €.", 1249, "EUR", "materiel", "2026-09-18", "Ordinateur portable", "plafond"),
    ("R031", "E07", "Suite à l'hôtel à Cannes le 26/09/2026 pendant le salon, 420 €.", 420, "EUR", "hebergement", "2026-09-26", "Hôtel à Cannes pendant le salon", "plafond"),
    ("R032", "E08", "Business class flight New York - Paris on 2026-10-02, 2350.00 USD.", 2350, "USD", "transport", "2026-10-02", "Vol New York - Paris en classe affaires", "plafond"),
    ("R033", "E09", "Billet de train réservé pour le séminaire du 15/11/2026, 74 €.", 74, "EUR", "transport", "2026-11-15", "Train pour le séminaire", "date_future"),
    ("R034", "E10", "Déjeuner d'équipe du 12/05/2026 oublié dans la note précédente, 27 €.", 27, "EUR", "repas", "2026-05-12", "Déjeuner d'équipe", "date_ancienne"),
    ("R035", "E02", "Train Paris-Lyon A/R pour le salon Industrie le 05/10/2026, 118,00 €.", 118, "EUR", "transport", "2026-10-05", "Train Paris-Lyon salon Industrie", "doublon_metier"),
    ("R036", "E11", "Parking de l'aéroport, 24 euros, le 14 octobre 2026.", 24, "EUR", "transport", "2026-10-14", "Parking aéroport", "doublon_metier"),
    ("R037", "E13", "Déjeuner avec un prospect le 08/10/2026, 31,20 €.", 31.20, "EUR", "repas", "2026-10-08", "Déjeuner prospect", "email_invalide"),
    ("R038", "E14", "Billet de train Lyon-Grenoble du 13/10/2026, 23 €.", 23, "EUR", "transport", "2026-10-13", "Train Lyon-Grenoble", "email_invalide"),
    ("R039", "E15", "Fournitures de bureau (carnets, stylos) achetées le 30/09/2026, 21,45 €.", 21.45, "EUR", "materiel", "2026-09-30", "Fournitures de bureau", "email_invalide"),
    ("R040", "E12", "   ", None, None, None, None, None, "vide"),
]

# Domaine réservé « .invalid » (RFC 2606) : le service e-mail factice le refuse définitivement.
INVALID = {"E13": "e13@compta.invalid", "E14": "e14@rh.invalid", "E15": "e15@ventes.invalid"}

out = []
for rid, emp, text, amount, cur, cat, day, motif, scenario in ROWS:
    out.append({
        "request_id": rid,
        "employe": emp,
        "email": INVALID.get(emp, f"{emp.lower()}@example.com"),
        "texte": text,
        "scenario": scenario,
        "attendu": None if amount is None else
        {"montant": amount, "devise": cur, "categorie": cat, "date": day, "motif": motif},
    })

Path(__file__).with_name("requests.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "demandes écrites")
