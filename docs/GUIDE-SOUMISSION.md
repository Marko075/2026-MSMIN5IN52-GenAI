# Guide de réalisation et de soumission

## 1. Réserver un sujet

Choisissez un sujet du [catalogue](CATALOGUE.md) ou soumettez une proposition libre avant de commencer, puis inscrivez le groupe et ses vœux dans le classeur d'inscription du cours (lien transmis par l'enseignant) : c'est lui qui fait foi pour l'attribution. Deux groupes ne peuvent pas traiter le même sujet. Une proposition libre doit respecter les mêmes exigences de faisabilité, de mesure et de différenciation que le catalogue.

## 2. Préparer le fork

1. Forkez `jsboigeEPF/2026-MSMIN5IN52-GenAI`.
2. Clonez votre fork.
3. Ajoutez le dépôt du cours comme remote `upstream` : `https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI.git`.
4. Créez une branche de travail.
5. Créez **un seul** dossier `groupe-<nom-court>` à la racine à partir de [`template-groupe/`](../template-groupe/).

Ne renommez, ne déplacez et ne supprimez aucun fichier appartenant au dépôt ou à un autre groupe. Avant d'ouvrir la PR, vérifiez que le diff ne contient que votre dossier.

## 3. Travailler progressivement

- Commitez régulièrement avec des messages décrivant le changement.
- Ouvrez une PR brouillon ou publiez un point d'étape assez tôt pour rendre la progression visible.
- Répartissez les tâches et relisez le code des autres membres.
- Quand le sujet s'y prête, comparez à une approche plus simple pour montrer l'apport du système GenAI.
- Testez les modes d'échec : réponse invalide, indisponibilité d'une API, entrée vide, timeout, absence de GPU ou dépassement de budget.
- Utilisez des données publiques, synthétiques ou dûment autorisées.

Si le groupe reste bloqué après avoir isolé le problème et documenté ses essais, ouvrez une [demande d'accompagnement](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/issues/new?template=demande-accompagnement.yml) avec une reproduction minimale et un lien vers la branche ou la PR. N'attendez pas la dernière semaine pour signaler un blocage.

Les deux TPs et leurs contributions au dépôt CoursIA suivent un flux séparé, décrit dans [TPs dans CoursIA et bonus](TPS-ET-BONUS.md).

## 4. Contenu obligatoire du dossier

```text
groupe-<nom-court>/
├── README.md
├── .env.example
├── .gitignore
├── src/                 # ou application équivalente
├── tests/               # si pertinent
├── notebooks/           # si pertinent
└── slides/              # PDF recommandé
```

Le README du groupe doit présenter : membres, sujet, problématique, architecture, installation, exécution, tests, résultats, limites, répartition du travail, licences et références.

Le projet contient également :

- le code source ;
- une UI/démo fonctionnelle **ou** un notebook qui montre le système en action (par exemple une conversation agentique commentée) ;
- des tests et leur résultat quand le sujet s'y prête : c'est un plus, pas une obligation ;
- les slides de soutenance, qui peuvent arriver dans une PR complémentaire avant la soutenance ;
- un `.env.example` ne contenant que les noms des variables.

## 5. Secrets, données et fichiers lourds

Ne commitez jamais :

- clé API, token, mot de passe, cookie ou fichier `.env` réel ;
- donnée personnelle ou confidentielle ;
- poids de modèle, environnement virtuel, `node_modules`, cache ou archive de build ;
- contenu dont la licence interdit la redistribution.

Si un secret a été commité, révoquez-le immédiatement puis prévenez l'enseignant. Le supprimer dans un commit ultérieur ne le retire pas de l'historique Git.

## 6. Ouvrir la Pull Request

1. Synchronisez votre branche avec `upstream/main` sans réécrire l'historique partagé.
2. Inspectez la liste des fichiers modifiés.
3. Poussez votre branche vers votre fork.
4. Ouvrez une PR vers `jsboigeEPF/2026-MSMIN5IN52-GenAI:main`.
5. Remplissez toute la checklist du modèle de PR.

La PR publique identifie les membres uniquement par leurs comptes GitHub (`@pseudo`) ; n'indiquez ni nom civil, ni adresse e-mail, ni numéro étudiant.

La PR est obligatoire : un lien vers un dépôt externe, un fichier envoyé séparément ou un push direct ne constitue pas une remise.

**Date limite : lundi 26 octobre 2026 à 23:59.**

La PR n'a pas besoin d'être parfaite à cette date : elle se met à jour à chaque push. Les slides et d'éventuelles corrections peuvent suivre dans une PR complémentaire ; envoyez-la assez tôt pour qu'elle puisse être intégrée avant la soutenance.

## 7. Préparer la soutenance

La démonstration doit pouvoir repartir depuis un environnement propre. Préparez un plan B enregistré ou mocké si une API externe, le réseau ou un GPU peut manquer. Chaque membre doit être capable d'expliquer l'architecture, les choix, les mesures et les limites.
