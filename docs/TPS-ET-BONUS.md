# TPs dans CoursIA et bonus

Le module comprend **deux TPs**, réalisés **par groupe**. Chaque TP prend la forme d'une contribution du groupe au dépôt public [`jsboige/CoursIA`](https://github.com/jsboige/CoursIA) : votre groupe choisit un notebook autorisé, corrige ses exercices ouverts, vérifie son exécution puis propose son travail par Pull Request.

## Barème du bonus

Pour chaque TP :

| Exercices corrigés et acceptés | Bonus |
|---:|---:|
| 1 exercice | rendu de base, aucun bonus |
| 2 exercices | +0,5 point |
| 3 exercices ou plus | +1 point maximum |

Le plafond est donc de **+1 point par TP**, soit **+2 points maximum** sur l'ensemble du module. Le bonus s'ajoute après la note de soutenance et l'ajustement lié à la taille du groupe ; la note finale reste plafonnée à 20/20.

## Ce qui compte comme exercice corrigé

CoursIA distingue :

- un **exemple guidé**, dont la solution est déjà complète ;
- un **exercice ouvert**, matérialisé par une cellule à compléter (`pass`, `return None`, `TODO`, résultat manquant ou équivalent) ;
- une **correction**, qui remplace ce travail ouvert par une solution fonctionnelle, expliquée et vérifiée.

Modifier un exemple déjà résolu, recopier une solution existante ou seulement retirer un marqueur `TODO` ne constitue pas une correction. Si deux groupes proposent le même exercice, seule une contribution originale et attribuable peut être comptée.

## Déroulement d'un TP

1. Consultez la liste de notebooks annoncée pour le TP en classe.
2. Vérifiez qu'aucune PR ouverte ne corrige déjà les mêmes exercices.
3. Forkez `jsboige/CoursIA`, créez une branche dédiée et ne modifiez que le notebook choisi et, si nécessaire, ses tests ou ressources directement associées.
4. Pour chaque exercice choisi :
   - conservez l'énoncé et l'intention pédagogique ;
   - implémentez une solution lisible plutôt qu'une valeur codée en dur ;
   - ajoutez une courte explication lorsque le raisonnement n'est pas évident ;
   - vérifiez les cas nominaux et au moins un cas limite pertinent.
5. Exécutez le notebook depuis un environnement propre, dans l'ordre des cellules.
6. Ouvrez une Pull Request vers `jsboige/CoursIA:main` avec le numéro du TP, le notebook, les exercices corrigés et les vérifications effectuées.
7. Transmettez le lien de la PR selon la consigne donnée en classe. Une branche ou un fork sans PR ne peut pas être compté.

## Critères d'acceptation

Une correction compte lorsque :

- elle répond réellement à l'exercice et ne révèle pas de secret ou de donnée privée ;
- les cellules modifiées s'exécutent et leurs résultats sont cohérents ;
- elle ne dégrade ni les exemples guidés ni les autres exercices ;
- le diff reste limité au besoin du TP ;
- les remarques de review nécessaires sont traitées avant la clôture du TP.

Le dépôt CoursIA possède un outil canonique de détection des exercices, [`scripts/notebook_tools/count_exercises.py`](https://github.com/jsboige/CoursIA/blob/main/scripts/notebook_tools/count_exercises.py). Il aide à distinguer les cellules ouvertes des exemples, mais l'acceptation finale porte sur la qualité réelle de la correction et de son exécution.

## Hygiène et sécurité

Ne commitez jamais de clé API, fichier `.env`, cookie, donnée personnelle, poids de modèle, environnement virtuel ou sortie volumineuse. Utilisez les variables d'environnement et les données publiques ou synthétiques prévues par le notebook. Si un secret apparaît dans un commit, révoquez-le immédiatement et prévenez l'enseignant.
