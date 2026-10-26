# PLAN — B5 : workflow agentique résilient et idempotent (groupe-transformers)

Échéance : PR ouverte avant le lundi 26/10/2026 à 23:59 (objectif interne : 22:30).

## Phases

- [x] **0. Mise en place**
  - [x] `.env` vérifié comme ignoré par Git (`git check-ignore`) avant tout `git add`
  - [x] remote `upstream` ajouté et fork synchronisé avec `upstream/main` (merge, sans réécriture)
  - [x] contenu de `template-groupe/` déjà présent dans `groupe-transformers/` (README, `.env.example`, `.gitignore`) ; `.env` non écrasé
  - [x] lecture de CATALOGUE (B5), GUIDE-SOUMISSION, EVALUATION, AGENTS.md, notebooks CoursIA 06-ProcessFramework et 09_Production_Patterns
- [x] **1. Moteur** : 5 étapes, persistance SQLite WAL, clés d'idempotence, services factices, CLI (LLM simulé, puis réel)
  - [x] `check-llm` : 1 appel réel OK (Semantic Kernel → OpenRouter, JSON valide)
  - [x] `real-run` : 10 demandes, 10 appels, 100 % des champs corrects, crash après l'appel LLM récupéré par le cache
- [x] **2. Pannes** : superviseur, chaos (psutil), points de crash, doublons, pannes transitoires, compensation, mode naïf
- [x] **3. Tests pytest hors ligne** : 56 tests verts (~10 s)
- [x] **4. Campagne** : 5 seeds × 2 modes ; 65 / 49 crashs ; 94 doublons (naïf) contre 0 (protégé) ; notebook + rapport HTML
- [x] **5. Démo** : tableau de bord Streamlit (direct + replay), `python -m demo` (~25 s), `replay --terminal`
- [x] **6. Finalisation** : README complet, `.env.example`, slides v1 (Markdown + PDF), vérification du diff
- [ ] **À faire par le groupe** : pseudo GitHub d'Alexandre (README, slides), section « Répartition du travail », ouverture de la PR

## Décisions (prises sans interrompre, à relire)

| # | Décision | Raison |
|---|---|---|
| D1 | Travail sur `main` du fork, **un seul commit + push à la fin** (choix du groupe) au lieu d'un commit par phase | Demande explicite du groupe ; push de sécurité si 22:30 approche |
| D2 | Commits au nom du membre, sans trailer `Co-Authored-By` ; l'assistance IA est **déclarée dans le README** | Choix du groupe ; AGENTS.md accepte l'une ou l'autre forme de déclaration |
| D3 | Modèle LLM : `qwen/qwen3.8-flash` via OpenRouter (surchargeable par `OPENROUTER_MODEL`) | Le défaut des notebooks (`gpt-5-mini`) n'est pas dans la liste des modèles ouverts au cours ; Qwen3.8 Flash y figure, supporte `response_format` JSON, ~0,15 $/M tokens |
| D4 | Python 3.14 local (projet compatible ≥ 3.11), venv dans `groupe-transformers/.venv` (ignoré) | Seule version installée sur la machine |
| D5 | Services externes simulés dans une base séparée `services.db` | Un service externe ne partage pas la transaction du workflow : c'est ce qui crée la fenêtre critique « effet fait, étape pas encore marquée » |
| D6 | Les services factices peuvent échouer **après** avoir appliqué l'effet (`timeout_after`) | Cas réel le plus dangereux : un retry sans clé d'idempotence crée un doublon même sans crash |
| D7 | Journal JSON Lines : un fichier par processus (`worker.jsonl`, `supervisor.jsonl`, `dashboard.jsonl`), fusionnés par horodatage à la lecture ; lignes tronquées ignorées | Pas de verrou de fichier portable Windows/Linux ; un kill peut tronquer la dernière ligne |
| D8 | Les métriques d'effets viennent du registre `services.db` (autorité), les temps viennent du journal | Le journal peut perdre la dernière ligne au moment d'un kill ; le registre est transactionnel |
| D9 | Clé de cache LLM = sha256(modèle, version du prompt, texte) | Après un crash, une étape déjà extraite ne rappelle jamais le LLM |
| D10 | Mode naïf : même pipeline, mêmes retries, mais pas d'état d'étape, pas de clé d'idempotence, ack du message seulement en fin de traitement (at-least-once) | Baseline réaliste d'une file de messages classique |
| D11 | Budget LLM réel : compteur persistant `results/llm_usage.jsonl`, plafond 150 appels (cible < 30) | Règle du cours (budget partagé) |
| D12 | Campagne et démo en LLM simulé déterministe ; vrai LLM sur 10 demandes (`real-run`) | Reproductible sans réseau ni clé |
| D13 | Semantic Kernel conservé (pas de bascule vers le SDK OpenAI) | Fonctionne du premier coup sous Python 3.14 (SK 1.45) ; import paresseux pour ne pas ralentir le worker simulé |
| D14 | Le chaos attend que le worker soit « prêt » avant de tirer son délai de kill | Sinon des kills plus rapides que le démarrage de Python bloqueraient toute progression |
| D15 | Mode naïf : anti-doublon métier en mémoire (perdu à chaque crash) | Implémentation naïve réaliste ; montre qu'un état en mémoire ne protège que tant que le processus vit |
| D16 | Si les retries du virement sont épuisés : réconciliation par la clé, puis compensation si le paiement existe | Évite un paiement orphelin quand le dernier essai a réussi côté service |
| D17 | Instantanés (`snapshots.jsonl`) enregistrés pendant chaque run et rejoués par `replay` | Le replay (plan B) réutilise exactement le rendu du tableau de bord, sans rien exécuter |
| D18 | Enregistreur d'instantanés tolérant aux erreurs, lectures sans écriture de schéma | Lors d'une démo, l'enregistrement s'est arrêté à mi-parcours (cause non reproduite) ; on journalise l'erreur et on continue |
| D19 | Slides PDF générées depuis le Markdown par matplotlib (`slides/build_pdf.py`) | Pas de Marp/pandoc installé ; le Markdown reste la source |
