# AGENTS.md — charte de l'agent étudiant

Ce dépôt est celui de vos projets. Si vous travaillez avec un agent de code (Claude Code, Cursor, Copilot, Codex…), **cette page fait autorité** : elle dit ce que votre agent doit faire ici, et ce qu'il ne doit pas y chercher.

## Votre périmètre

- **Un seul dossier : celui de votre groupe**, `groupe-<nom-court>` à la racine de votre fork, initialisé depuis [`template-groupe/`](template-groupe/). N'éditez rien en dehors — ni le dossier d'un autre groupe, ni `docs/`, ni `.github/`.
- **Vous travaillez sur un fork**, et vous livrez par **Pull Request** vers ce dépôt.
- **Commits réguliers et petits.** L'historique Git fait partie du livrable : il doit montrer la participation de chaque membre.

## Ce que votre agent ne doit pas chercher

Si vous pointez votre agent sur un clone de **CoursIA** (le dépôt de cours), il y lira un harnais écrit pour une flotte d'agents automatisés. **Rien de cela ne vous concerne.**

Il n'y a ici **aucun** dashboard à lire, **aucune** « lane » à réclamer, **aucun** heartbeat ni inbox de cluster, **aucun** `[CLAIMED]` à poser, **aucun** tag `Grain:` à écrire, **aucun** rapport de début ou de fin de session à publier. Ces objets n'existent pas pour vous. Leur absence n'est pas un blocage : votre agent termine sa session quand le travail est fait.

## Non négociable

| Règle | Pourquoi |
|---|---|
| **Aucun secret dans un commit** — clé d'API, token, mot de passe, URL contenant des identifiants. Les valeurs vivent dans un `.env` **non commité** ; seul `.env.example`, sans valeur, est livré. | Le dépôt est public et l'historique Git est définitif. Un secret poussé est un secret à **révoquer**, pas à supprimer : un `git revert` ne l'efface pas. |
| **Aucune donnée personnelle** de tiers — nom, e-mail, photo, enregistrement de voix — sans accord écrit de la personne. | Même permanence de l'historique, plus le RGPD. Anonymisez vos jeux de test. |
| **Déclarez la contribution de l'agent** : `Co-Authored-By:` dans le commit, ou une phrase dans le README du groupe. | Une contribution d'agent **déclarée n'enlève aucun point** — l'assistance par IA est le sujet même du cours. La masquer est de la fraude. |
| **Ce que vous rendez doit s'exécuter.** Pas de `raise NotImplementedError` laissé dans le chemin nominal, pas de test désactivé ou supprimé pour faire passer la CI. | Un livrable qui ne tourne pas n'est pas évaluable. Un test supprimé pour verdir la CI se voit dans le diff. |

## Bien se servir d'un agent (c'est noté)

- **Lisez ce que l'agent produit avant de le committer.** Vous serez interrogés dessus en soutenance ; « c'est l'agent qui l'a écrit » n'est pas une réponse recevable.
- **Faites-lui expliquer ses choix**, pas seulement produire du code. Un désaccord argumenté avec votre agent vaut mieux qu'une acceptation silencieuse — et se raconte très bien à l'oral.
- **Vérifiez ses affirmations.** Un agent qui annonce « les tests passent » sans avoir lancé les tests est le défaut le plus courant. Demandez la sortie de commande.
- **Ne le laissez pas réécrire ce qu'il ne comprend pas.** S'il propose de supprimer du code existant pour « simplifier », demandez d'abord pourquoi ce code existait.

## Aide

- Sujet libre hors catalogue → [formulaire de proposition de sujet](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/issues/new?template=proposition-sujet.yml), à faire valider **avant** de développer.
- Choix du sujet, livrables, barème → [`docs/CATALOGUE.md`](docs/CATALOGUE.md), [`docs/GUIDE-SOUMISSION.md`](docs/GUIDE-SOUMISSION.md), [`docs/EVALUATION.md`](docs/EVALUATION.md).
- Blocage technique persistant → ouvrez une issue sur ce dépôt en décrivant ce que vous avez déjà tenté.
