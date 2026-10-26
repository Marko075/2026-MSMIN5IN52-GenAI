# Projets 2026 — IA générative et chatbots

Dépôt de projets du cours **MSMIN5IN52 — IA générative et chatbots**, groupe **TD MIN1**, EPF, année 2026-2027.

## Calendrier

| Étape | Date |
|---|---|
| Première séance | Mercredi 16 septembre 2026, 08:30–12:15 |
| Dépôt de la Pull Request finale | **Lundi 26 octobre 2026 à 23:59** |
| Soutenance et démonstration | **Mercredi 28 octobre 2026, de 13:15 à 17:00, salle A202** |

Le cours comporte six séances. Le projet est réalisé progressivement et doit rester démontrable tout au long du module.

## Démarrage rapide

1. Constituez un groupe — **3 personnes est le format standard**.
2. Choisissez un sujet dans le [catalogue 2026](docs/CATALOGUE.md), puis inscrivez le groupe et ses vœux dans le **classeur d'inscription** du cours (lien transmis par l'enseignant). Un sujet n'est attribué qu'à un groupe ; le classeur fait foi.
3. Forkez ce dépôt sur le compte d'un membre du groupe.
4. Créez un dossier unique à la racine, nommé `groupe-<nom-court>`.
5. Copiez le contenu de [`template-groupe/`](template-groupe/) dans ce dossier.
6. Travaillez par commits réguliers sans modifier les fichiers des autres groupes.
7. Si le groupe est bloqué, ouvrez tôt une [demande d'accompagnement](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/issues/new?template=demande-accompagnement.yml).
8. Ouvrez une Pull Request vers ce dépôt avant la date limite.

Les sujets libres sont possibles, mais doivent être proposés avec le [formulaire dédié](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/issues/new?template=proposition-sujet.yml) et validés avant développement.

## Deux circuits de contribution distincts

- **Projet fil rouge** : le groupe développe son démonstrateur dans son fork de **ce dépôt**, puis ouvre une PR vers [`jsboigeEPF/2026-MSMIN5IN52-GenAI:main`](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/pulls). Cette PR collective porte le projet évalué en soutenance.
- **TPs par groupe** : le groupe corrige des exercices dans un notebook du dépôt [`jsboige/CoursIA`](https://github.com/jsboige/CoursIA), puis ouvre une PR distincte vers `jsboige/CoursIA:main`. Ces contributions ne vont ni dans le dossier du groupe ni dans la PR du projet ; leur barème est décrit dans [TPs dans CoursIA et bonus](docs/TPS-ET-BONUS.md).

## Documents de référence

- [Catalogue des sujets 2026](docs/CATALOGUE.md)
- [Guide de réalisation et de soumission](docs/GUIDE-SOUMISSION.md)
- [Modalités d'évaluation](docs/EVALUATION.md)
- [TPs dans CoursIA et bonus](docs/TPS-ET-BONUS.md)
- [Sujets réalisés lors des promotions précédentes](docs/HISTORIQUE-SUJETS.md)
- [Gabarit de dossier de groupe](template-groupe/README.md)

## Catégories du catalogue

| Code | Catégorie |
|---|---|
| A | Texte structuré, RAG et mémoire sémantique |
| B | Agents, orchestration et MCP |
| C | Génération et édition d'images |
| D | Audio et voix |
| E | Vidéo et médias composés |
| F | Plateformes conversationnelles et mise en production |
| G | Ingénierie logicielle assistée par IA |
| H | Évaluation, sécurité et fiabilité |
| I | Adaptation de modèles et inférence locale |
| J | Données, science et aide à la décision |
| K | IA responsable, gouvernance et sobriété |
| L | Applications sectorielles évaluables |

## Livrables attendus

Chaque groupe fournit au minimum :

- le code source et des instructions reproductibles ;
- un `README.md` complet ;
- une interface/démonstration fonctionnelle **ou** un notebook explicatif qui montre le système en action ;
- des tests quand le sujet s'y prête (un plus, pas une obligation) ;
- les slides de soutenance (elles peuvent suivre dans une PR complémentaire) ;
- un fichier `.env.example` sans valeur secrète ;
- un historique Git montrant la participation des membres.

Les données volumineuses, poids de modèles, environnements virtuels, fichiers `.env` et clés API ne doivent jamais être commités.

## Ressources du cours

Les fiches renvoient aux notebooks du dépôt public [CoursIA](https://github.com/jsboige/CoursIA/tree/main/MyIA.AI.Notebooks/GenAI). Ils servent de points de départ : un projet attendu ne se limite pas à recopier un notebook, mais construit un démonstrateur, mesure ses résultats et documente ses choix.

## Licence

Le contenu pédagogique de ce dépôt est distribué sous [licence MIT](LICENSE). Chaque groupe reste responsable des licences des modèles, données, bibliothèques et médias qu'il utilise.
