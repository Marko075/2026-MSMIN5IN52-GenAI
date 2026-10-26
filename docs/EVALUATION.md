# Modalités d'évaluation

## Taille des groupes

Le projet est conçu pour un **groupe de 3 personnes**.

| Taille du groupe | Ajustement appliqué à la note finale |
|---:|---:|
| 1 personne | +3 points |
| 2 personnes | +1 point |
| 3 personnes | aucun ajustement |
| 4 personnes | −1 point |

Un groupe de plus de quatre personnes n'est pas autorisé sans accord explicite de l'enseignant.

## Soutenance collégiale

La soutenance a lieu le **mercredi 28 octobre 2026, de 13:15 à 17:00, salle A202**. Les pairs et l'enseignant évaluent chaque projet sur les mêmes quatre critères, chacun noté de 0 à 10.

| Critère | Ce qui est évalué |
|---|---|
| Présentation | Clarté, structure, respect du temps, qualité de la démonstration et réponses aux questions |
| Théorie | Compréhension des méthodes, justification des choix, connaissance des limites et des travaux cités |
| Technique | Fonctionnement, architecture, qualité du code, tests, mesures et reproductibilité |
| Organisation | Répartition du travail, historique Git, documentation, gestion des risques et progression |

Pour un jury donné, la **note de base sur 20** est :

```text
(présentation + théorie + technique + organisation) / 2
```

La moyenne des évaluations des pairs forme 50 % de la note de soutenance et l'évaluation de l'enseignant forme les 50 % restants. Les évaluations manifestement incomplètes ou non argumentées peuvent être écartées.

## Bonus des TPs

Le module comprend deux [TPs réalisés par contribution à CoursIA](TPS-ET-BONUS.md). Pour chaque TP, le premier exercice corrigé constitue le rendu de base ; le deuxième et le troisième exercice acceptés valent chacun +0,5 point. Le bonus est plafonné à +1 point par TP, soit **+2 points maximum** sur le module.

La chaîne de calcul est :

```text
note_soutenance = 50 % moyenne des pairs + 50 % évaluation de l'enseignant
note_avant_bonus = note_soutenance + ajustement de taille du groupe
note_finale = min(20, note_avant_bonus + bonus des deux TPs)
```

Le bonus de TP est acquis par groupe et dépend des contributions acceptées et attribuables au groupe. La note finale reste comprise entre 0 et 20.

## Attendus transverses

La difficulté affichée dans le catalogue indique l'ampleur technique du sujet, mais ne remplace pas les critères ci-dessus. Une excellente réalisation d'un sujet 2/5 peut obtenir une excellente note. Sont particulièrement valorisés :

- un MVP réellement fonctionnel ;
- des résultats mesurés plutôt que des impressions ;
- la comparaison à une baseline simple ;
- une analyse honnête des échecs et limites ;
- des tests reproductibles ;
- une contribution visible de chaque membre.

## Remise

La Pull Request finale doit être ouverte au plus tard le **lundi 26 octobre 2026 à 23:59**, soit deux jours avant la soutenance. Les slides et d'éventuelles corrections peuvent suivre dans une PR complémentaire, à envoyer assez tôt pour être intégrée avant la soutenance.
