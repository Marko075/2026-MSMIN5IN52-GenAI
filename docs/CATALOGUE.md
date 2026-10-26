# Catalogue des sujets 2026

Ce catalogue est l'offre officielle **2026-2027** du module : **48 sujets actifs** répartis en douze axes. Un sujet attribué à un groupe dans le classeur d'inscription du cours devient indisponible aux autres groupes ; un sujet libre validé y entre par le formulaire de proposition. Chaque sujet définit un MVP réalisable en six semaines, un protocole d'évaluation et un plan de repli. Les notebooks liés sont des ressources de démarrage : le livrable doit aller au-delà de leur reproduction.

Consultez également les [sujets historiques exclus](HISTORIQUE-SUJETS.md), le [guide de soumission](GUIDE-SOUMISSION.md) et les [modalités d'évaluation](EVALUATION.md).

## Index

| Catégorie | Sujets |
|---|---|
| A — Texte structuré, RAG et mémoire | [A1](#a1--rag-hybride-avec-reranking-et-citations) · [A2](#a2--mémoire-persistante-multi-sessions) · [A3](#a3--contrats-json-sous-stress) · [A4](#a4--mémoire-multimodale-évaluable) · [A5](#a5--long-contexte-contre-rag-sous-ablation) |
| B — Agents, orchestration et MCP | [B1](#b1--processus-agentique-avec-validation-humaine) · [B2](#b2--serveur-mcp-métier-audité) · [B3](#b3--orchestrateur-agentique-sous-budget) · [B4](#b4--générateur-auto-validant-de-notebooks) · [B5](#b5--workflow-agentique-résilient-et-idempotent) |
| C — Images | [C1](#c1--benchmark-dévaluation-dédition-dimages) · [C2](#c2--fabrique-de-schémas-pédagogiques-cohérents) · [C3](#c3--édition-contrôlée-par-masques-et-structure) · [C4](#c4--cohérence-dune-série-visuelle) |
| D — Audio et voix | [D1](#d1--agent-vocal-temps-réel-sous-contrainte-de-latence) · [D2](#d2--doublage-multi-locuteurs-mesuré) · [D3](#d3--séparation-et-restauration-de-sources-audio) · [D4](#d4--synthèse-vocale-expressive-et-prosodie) |
| E — Vidéo | [E1](#e1--micro-capsules-vidéo-pédagogiques) · [E2](#e2--benchmark-de-compréhension-temporelle-vidéo) · [E3](#e3--pipeline-audiovisuel-synchronisé) · [E4](#e4--restauration-et-upscaling-vidéo) |
| F — Plateformes et production | [F1](#f1--qa-e2e-dopen-webui) · [F2](#f2--rag-wordpress-isolé-et-mesuré) · [F3](#f3--application-genai-observable-avec-net-aspire) · [F4](#f4--routeur-multi-fournisseurs-avec-failover) |
| G — Ingénierie assistée | [G1](#g1--banc-dessai-dagents-de-codage) · [G2](#g2--garde-fous-roslyn-pour-code-généré) · [G3](#g3--pair-programming-ia-en-étude-contrôlée) · [G4](#g4--migration-de-code-par-tests-différentiels) |
| H — Évaluation, sécurité et fiabilité | [H1](#h1--laboratoire-red-team-dinjection-de-prompt) · [H2](#h2--harness-dévaluation-dagents) · [H3](#h3--observatoire-du-reward-hacking) · [H4](#h4--provenance-et-détection-de-contenus-synthétiques) · [H5](#h5--constitution-ia-et-coût-des-refus) |
| I — Adaptation et inférence | [I1](#i1--qlora-sans-contamination-de-lévaluation) · [I2](#i2--inférence-locale-net-face-aux-api-cloud) · [I3](#i3--frontière-coût-précision-du-test-time-compute) · [I4](#i4--fusion-et-routage-de-modèles-spécialisés) |
| J — Données, science et décision | [J1](#j1--assistant-de-preuves-scientifiques) · [J2](#j2--analyste-multimodal-de-données) · [J3](#j3--expériences-reproductibles-auto-validées) |
| K — IA responsable, gouvernance et sobriété | [K1](#k1--confidentialité-des-données-synthétiques) · [K2](#k2--traçabilité-et-licences-des-générations) · [K3](#k3--sobriété--coût-énergie-et-tokens) |
| L — Applications sectorielles évaluables | [L1](#l1--assistant-médical-borné-avec-abstention) · [L2](#l2--analyse-financière-sourcée-et-auditable) · [L3](#l3--tuteur-adaptatif-avec-mesure-dapprentissage) |

## Lire une fiche

- **Difficulté** : ampleur technique indicative, de 2/5 à 5/5.
- **MVP** : périmètre minimal attendu à la démonstration.
- **Réussite** : résultat mesurable, pas seulement une démonstration choisie.
- **Plan B** : solution permettant de démontrer le travail malgré une API ou un GPU indisponible.
- **Budget** : lorsqu'une API ou une ressource payante est utile, la fiche fixe un ordre de grandeur à confirmer par le groupe avant les campagnes d'essais.

---

## A — Texte structuré, RAG et mémoire sémantique

### A1 — RAG hybride avec reranking et citations

**Difficulté : 3/5** · Mots-clés : `rag`, `hybrid-search`, `reranking`, `citations`

Construire une recherche combinant lexical et vectoriel, puis reranker les passages avant génération. Le cœur du projet est la mesure du retrieval et de la fidélité des citations, non un chatbot documentaire générique.

- **MVP** : ingestion d'un corpus public, trois variantes de retrieval et réponse avec citations traçables.
- **Réussite** : jeu d'au moins 40 questions, Recall@k/MRR, exactitude des citations et comparaison à une baseline vectorielle simple.
- **Extensions** : HyDE, reranker neuronal, analyse par type de question.
- **Faisabilité** : Python + Qdrant ; Docker utile, GPU non requis ; budget API cible inférieur à 10 €. Plan B : modèle local ou réponses extractives.

**CoursIA** : [Retrieval avancé](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/02-Retrieval-Avance.ipynb) · [Kernel Memory Hybrid Search](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/08-KernelMemory-Hybrid-Search.ipynb) · [RAG moderne](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/05_RAG_Modern.ipynb)

**Références** : [Qdrant — Hybrid Queries](https://qdrant.tech/documentation/concepts/hybrid-queries/) · [BEIR](https://arxiv.org/abs/2104.08663) · [RAGAS](https://docs.ragas.io/)

### A2 — Mémoire persistante multi-sessions

**Difficulté : 3/5** · Mots-clés : `memory`, `sessions`, `privacy`, `evaluation`

Concevoir une mémoire explicite qui décide quoi conserver, retrouver, mettre à jour ou oublier entre plusieurs sessions. Contrairement à l'ancien majordome, le domaine importe peu : le verrou est la politique de mémoire et sa mesure.

- **MVP** : journal d'événements, mémoire sémantique persistante, mise à jour des faits contradictoires et commande d'oubli.
- **Réussite** : scénarios multi-sessions reproductibles mesurant rappel utile, faux souvenirs, fraîcheur et suppression effective.
- **Extensions** : mémoire épisodique/sémantique séparée, chiffrement, expiration automatique.
- **Faisabilité** : base locale ou Qdrant ; GPU non requis ; données synthétiques obligatoires ; budget cible inférieur à 5 €. Plan B : embeddings locaux.

**CoursIA** : [Persistent Memory](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/14_Persistent_Memory.ipynb) · [Hands-On Grounding](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/01-Hands-On-Grounding.ipynb) · [Stockage vectoriel](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/05-Stockage-Vectoriel.ipynb)

**Références** : [MemGPT](https://arxiv.org/abs/2310.08560) · [Qdrant — Payload](https://qdrant.tech/documentation/concepts/payload/) · [OWASP — LLM02 Insecure Output Handling](https://genai.owasp.org/llmrisk/llm02-insecure-output-handling/)

### A3 — Contrats JSON sous stress

**Difficulté : 2/5** · Mots-clés : `structured-output`, `json-schema`, `property-testing`, `recovery`

Créer un banc de tests de sorties structurées : schémas imbriqués, contraintes croisées, réponses partielles et reprise après échec. Ce sujet porte sur la conformité et la robustesse, pas sur l'extraction ou la génération de documents métier déjà réalisées.

- **MVP** : cinq schémas de difficulté croissante, validateur, stratégie de retry et rapport d'erreurs.
- **Réussite** : au moins 200 générations, taux de conformité au premier essai/après retry, coût et latence par schéma.
- **Extensions** : property-based testing, comparaison de fournisseurs, génération de contre-exemples.
- **Faisabilité** : API texte uniquement ; budget cible inférieur à 8 €. Plan B : petit modèle local compatible JSON.

**CoursIA** : [Structured Outputs](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/03_Structured_Outputs.ipynb) · [Production Patterns](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb) · [Évaluation de texte](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/22_Evaluating_Generated_Text.ipynb)

**Références** : [JSON Schema](https://json-schema.org/specification) · [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) · [Hypothesis](https://hypothesis.readthedocs.io/)

### A4 — Mémoire multimodale évaluable

**Difficulté : 4/5** · Mots-clés : `multimodal`, `kernel-memory`, `retrieval`, `grounding`

Indexer un corpus mêlant texte et images, puis répondre à des questions dont certaines exigent les deux modalités. Le projet doit isoler l'apport du retrieval multimodal.

- **MVP** : ingestion multimodale, recherche, réponses sourcées et interface minimale.
- **Réussite** : jeu annoté d'au moins 30 questions unimodales/multimodales, ablations texte seul/image seule/fusion.
- **Extensions** : OCR, tableaux, late fusion, cache d'embeddings.
- **Faisabilité** : Qdrant ou Kernel Memory ; API vision possible ; budget cible inférieur à 15 €. Plan B : embeddings et légendes pré-calculés.

**CoursIA** : [Kernel Memory Multimodal](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/09-KernelMemory-Multimodal.ipynb) · [Kernel Memory In Process](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/06-KernelMemory-InProcess.ipynb) · [Semantic Kernel Multimodal](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/07-SemanticKernel-MultiModal.ipynb)

**Références** : [Microsoft Kernel Memory](https://github.com/microsoft/kernel-memory) · [CLIP](https://arxiv.org/abs/2103.00020) · [Qdrant — Multivectors](https://qdrant.tech/documentation/concepts/vectors/#multivectors)

### A5 — Long contexte contre RAG sous ablation

**Difficulté : 3/5** · Mots-clés : `long-context`, `rag`, `ablation`, `grounding`

Comparer sur un même corpus l'injection du document complet, un RAG simple et un RAG reranké. Le verrou technique est d'isoler l'effet du contexte disponible sans confondre qualité, coût et latence.

- **MVP** : corpus public, 50 questions, trois stratégies et journal des passages réellement fournis au modèle.
- **Réussite** : exactitude, fidélité des citations, coût, latence et performance selon la position de l'information.
- **Extensions** : compression de contexte, cache, questions multi-documents.
- **Faisabilité** : API texte ou modèle local ; budget cible inférieur à 12 €. Plan B : réponses mises en cache et corpus réduit.

**CoursIA** : [Long Context Strategies](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/10c_Long_Context_Strategies.ipynb) · [RAG moderne](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/05_RAG_Modern.ipynb)

**Références** : [Lost in the Middle](https://arxiv.org/abs/2307.03172) · [RAG](https://arxiv.org/abs/2005.11401) · [LongBench](https://arxiv.org/abs/2308.14508)

---

## B — Agents, orchestration et MCP

### B1 — Processus agentique avec validation humaine

**Difficulté : 3/5** · Mots-clés : `process-framework`, `human-in-loop`, `state-machine`, `tracing`

Implémenter un processus long composé d'étapes, d'états persistés, d'une validation humaine et d'une reprise après interruption. Il se distingue des anciens chats multi-agents par son graphe de processus observable.

- **MVP** : processus à cinq étapes, point d'approbation, reprise et journal d'exécution.
- **Réussite** : scénarios nominal, refus, timeout et reprise ; taux de complétion et temps par étape.
- **Extensions** : compensation d'une action, parallélisme, tableau de bord.
- **Faisabilité** : Semantic Kernel Python ou .NET ; GPU non requis ; budget cible inférieur à 10 €. Plan B : outils entièrement simulés.

**CoursIA** : [Process Framework](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/06-SemanticKernel-ProcessFramework.ipynb) · [Agents Semantic Kernel](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/03-SemanticKernel-Agents.ipynb) · [Filtres et observabilité](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/04-SemanticKernel-Filters-Observability.ipynb)

**Références** : [Semantic Kernel — Process Framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/process-framework) · [OpenTelemetry](https://opentelemetry.io/docs/) · [Human-in-the-loop ML](https://arxiv.org/abs/2108.00941)

### B2 — Serveur MCP métier audité

**Difficulté : 3/5** · Mots-clés : `mcp`, `tool-server`, `authorization`, `audit`

Créer un serveur MCP sur un petit jeu de données public, un client de démonstration et un audit des frontières d'autorité. Chaque outil doit déclarer un contrat précis et limiter ses effets.

- **MVP** : trois ressources, trois outils dont une action réversible, validation des entrées et journal d'audit.
- **Réussite** : tests des contrats, appels non autorisés, entrées hostiles, consentement et erreurs de transport.
- **Extensions** : OAuth, prompts MCP, intégration Open WebUI.
- **Faisabilité** : SDK MCP Python/TypeScript/C# ; aucun GPU ; API facultative ; budget cible inférieur à 5 €. Plan B : client de test déterministe.

**CoursIA** : [Semantic Kernel MCP](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/08-SemanticKernel-MCP.ipynb) · [Auditer un serveur MCP](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/AI-Engine-WordPress/03-Functional/03-4-MCP-Server/auditer-un-serveur-mcp.ipynb) · [Consentement OAuth MCP](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/AI-Engine-WordPress/03-Functional/03-4-MCP-Server/autour-du-consent-oauth-du-serveur-mcp.ipynb)

**Références** : [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18) · [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [OWASP — Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)

### B3 — Orchestrateur agentique sous budget

**Difficulté : 4/5** · Mots-clés : `agents`, `routing`, `budget`, `guardrails`

Construire un orchestrateur qui choisit dynamiquement modèle, outil et profondeur de raisonnement tout en respectant un plafond de coût et de tours.

- **MVP** : routeur, deux agents spécialisés, trois outils, budget dur et arrêt sûr.
- **Réussite** : suite de 30 tâches ; qualité, coût, latence, tours et violations du budget comparés à une stratégie fixe.
- **Extensions** : cache, modèle local, politique apprise.
- **Faisabilité** : API texte ; budget expérimental plafonné à 15 €. Plan B : replay de réponses et faux outils.

**CoursIA** : [Agentic Orchestration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/13_Agentic_Orchestration.ipynb) · [Reasoning Models](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/08_Reasoning_Models.ipynb) · [Function Calling](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/04_Function_Calling.ipynb)

**Références** : [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents) · [Semantic Kernel agents](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/) · [OpenAI — Function calling](https://platform.openai.com/docs/guides/function-calling)

### B4 — Générateur auto-validant de notebooks

**Difficulté : 4/5** · Mots-clés : `notebooks`, `generation`, `execution`, `validation`

Générer un notebook pédagogique à partir d'un cahier des charges, l'exécuter automatiquement, diagnostiquer ses erreurs puis produire un rapport de conformité. Le succès est l'exécution reproductible, pas la beauté d'un exemple.

- **MVP** : gabarit, génération, exécution isolée, deux boucles de correction maximum et rapport.
- **Réussite** : dix cahiers des charges ; taux d'exécution, conformité structurelle, corrections et coût.
- **Extensions** : plusieurs kernels, rubric pédagogique, sandbox renforcée.
- **Faisabilité** : Jupyter + Semantic Kernel ; exécution limitée et sans accès aux secrets ; budget cible inférieur à 8 €. Plan B : exercices Python sans réseau.

**CoursIA** : [NotebookMaker](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/10-SemanticKernel-NotebookMaker.ipynb) · [NotebookMaker batch paramétré](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/10b-SemanticKernel-NotebookMaker-batch-parameterized.ipynb) · [Code Interpreter](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/07_Code_Interpreter.ipynb)

**Références** : [Jupyter nbclient](https://nbclient.readthedocs.io/) · [nbformat](https://nbformat.readthedocs.io/) · [OWASP — Insecure Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)

### B5 — Workflow agentique résilient et idempotent

**Difficulté : 4/5** · Mots-clés : `resilience`, `idempotency`, `recovery`, `agents`

Construire un workflow outillé qui supporte doublons, interruption et reprise sans répéter ses effets. Le verrou technique est la sémantique d'exécution fiable, non le nombre d'agents.

- **MVP** : cinq étapes persistées, clés d'idempotence, reprise après crash et compensation d'une action réversible.
- **Réussite** : campagne d'au moins 40 pannes injectées mesurant complétion, effets dupliqués et temps de reprise.
- **Extensions** : files persistantes, concurrence, stratégie saga.
- **Faisabilité** : outils simulés et base locale suffisants ; aucun GPU. Plan B : replay déterministe d'événements.

**CoursIA** : [Process Framework](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/06-SemanticKernel-ProcessFramework.ipynb) · [Production Patterns](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb)

**Références** : [Microsoft — Idempotency](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) · [AWS Builders' Library — Idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) · [OpenTelemetry](https://opentelemetry.io/docs/)

---

## C — Génération et édition d'images

### C1 — Benchmark d'évaluation d'édition d'images

**Difficulté : 3/5** · Mots-clés : `image-editing`, `benchmark`, `identity`, `quality`

Comparer plusieurs moteurs sur des instructions d'édition contrôlées : modification locale, préservation de l'identité et respect du prompt.

- **MVP** : 25 images/instructions, deux moteurs, métriques automatiques et évaluation humaine aveugle.
- **Réussite** : protocole reproductible, intervalles de confiance, analyse coût–latence–qualité.
- **Extensions** : troisième moteur, métrique perceptuelle, interface de vote.
- **Faisabilité** : service ComfyUI distant ou API image ; budget cible inférieur à 15 €. Plan B : corpus de sorties pré-générées.

**CoursIA** : [Qwen Image Edit](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/01-Foundation/01-5-Qwen-Image-Edit.ipynb) · [Comparaison multi-modèles](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/03-Orchestration/03-1-Multi-Model-Comparison.ipynb) · [Stable Diffusion 3.5](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/02-Advanced/02-3-Stable-Diffusion-3-5.ipynb)

**Références** : [Qwen Image](https://github.com/QwenLM/Qwen-Image) · [CLIPScore](https://arxiv.org/abs/2104.08718) · [LPIPS](https://arxiv.org/abs/1801.03924)

### C2 — Fabrique de schémas pédagogiques cohérents

**Difficulté : 2/5** · Mots-clés : `diagrams`, `education`, `style`, `quality-control`

Produire une série de schémas pédagogiques à partir de briefs structurés, avec contrôle de lisibilité, cohérence visuelle et exactitude des légendes. Ce n'est ni une histoire illustrée ni un générateur de posts sociaux.

- **MVP** : dix concepts, gabarit de brief, génération, post-traitement et validation.
- **Réussite** : grille d'experts/utilisateurs, OCR des légendes, cohérence de palette et taux de corrections.
- **Extensions** : accessibilité daltonisme, SVG hybride, boucle de retouche.
- **Faisabilité** : API ou ComfyUI ; GPU local non requis ; budget cible inférieur à 15 €. Plan B : petit corpus pré-généré à corriger.

**CoursIA** : [Science Diagrams](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/examples/science-diagrams.ipynb) · [Educational Content Generation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/04-Applications/04-1-Educational-Content-Generation.ipynb) · [Basic Image Operations](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/01-Foundation/01-3-Basic-Image-Operations.ipynb)

**Références** : [WCAG — Images of Text](https://www.w3.org/WAI/WCAG22/Understanding/images-of-text.html) · [Tesseract OCR](https://tesseract-ocr.github.io/) · [Pillow](https://pillow.readthedocs.io/)

### C3 — Édition contrôlée par masques et structure

**Difficulté : 3/5** · Mots-clés : `inpainting`, `controlnet`, `masks`, `structure`

Éditer localement des images tout en préservant le reste de la scène. Le verrou technique est de mesurer séparément respect de la zone, de la structure et de l'instruction.

- **MVP** : 30 couples image/masque, deux méthodes d'édition et visualisation avant/après.
- **Réussite** : LPIPS hors masque, CLIPScore dans le masque et notation humaine aveugle.
- **Extensions** : ControlNet, segmentation automatique, retouches successives.
- **Faisabilité** : API ou ComfyUI ; budget cible inférieur à 15 €. Plan B : sorties pré-calculées.

**CoursIA** : [Qwen Image Edit](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/01-Foundation/01-5-Qwen-Image-Edit.ipynb) · [Workflow Orchestration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/03-Orchestration/03-2-Workflow-Orchestration.ipynb)

**Références** : [ControlNet](https://arxiv.org/abs/2302.05543) · [Diffusers — Inpainting](https://huggingface.co/docs/diffusers/using-diffusers/inpaint) · [LPIPS](https://arxiv.org/abs/1801.03924)

### C4 — Cohérence d'une série visuelle

**Difficulté : 4/5** · Mots-clés : `identity`, `consistency`, `series`, `evaluation`

Produire une série d'images où personnages, objets et style restent reconnaissables malgré des scènes variées. Le verrou technique est la cohérence inter-images, pas la qualité d'une image isolée.

- **MVP** : deux identités, dix scènes chacune, deux stratégies de conditionnement et galerie comparative.
- **Réussite** : similarité d'identité, diversité des scènes, respect du prompt et évaluation humaine randomisée.
- **Extensions** : adaptation légère, références multiples, cohérence de vêtements.
- **Faisabilité** : GPU distant ou API ; limiter les itérations. Plan B : petit corpus généré en amont.

**CoursIA** : [Creative Workflows](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/04-Applications/04-2-Creative-Workflows.ipynb) · [Multi-Model Comparison](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/03-Orchestration/03-1-Multi-Model-Comparison.ipynb)

**Références** : [DreamBooth](https://arxiv.org/abs/2208.12242) · [IP-Adapter](https://arxiv.org/abs/2308.06721) · [CLIP](https://arxiv.org/abs/2103.00020)

---

## D — Audio et voix

### D1 — Agent vocal temps réel sous contrainte de latence

**Difficulté : 4/5** · Mots-clés : `realtime`, `voice-agent`, `latency`, `barge-in`

Assembler STT, LLM et TTS en flux duplex, mesurer chaque étape et gérer l'interruption par l'utilisateur. Le sujet exclut la composition musicale.

- **MVP** : conversation vocale, streaming, interruption, traces temporelles et mode texte de secours.
- **Réussite** : p50/p95 de latence, taux d'interruptions correctement gérées, transcription et tests sur bruit contrôlé.
- **Extensions** : VAD local, plusieurs voix, routage cloud/local.
- **Faisabilité** : API temps réel ; limiter la durée des campagnes, budget cible inférieur à 15 €. Plan B : replays audio horodatés.

**CoursIA** : [Realtime Voice API](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/03-Orchestration/03-3-Realtime-Voice-API.ipynb) · [Audio Pipeline Orchestration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/03-Orchestration/03-2-Audio-Pipeline-Orchestration.ipynb) · [Whisper STT](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/01-Foundation/01-2-OpenAI-Whisper-STT.ipynb)

**Références** : [OpenAI — Realtime API](https://platform.openai.com/docs/guides/realtime) · [WebRTC](https://webrtc.org/getting-started/overview) · [Silero VAD](https://github.com/snakers4/silero-vad)

### D2 — Doublage multi-locuteurs mesuré

**Difficulté : 3/5** · Mots-clés : `dubbing`, `diarization`, `tts`, `wer`

Créer une chaîne de transcription, segmentation des locuteurs, traduction éventuelle, attribution de voix et resynchronisation. Le verrou est la qualité temporelle et vocale, non l'ambiance sonore.

- **MVP** : extrait de 3 à 5 minutes, au moins deux locuteurs, sous-titres et piste doublée.
- **Réussite** : WER, erreur de diarisation, décalage temporel et écoute à l'aveugle.
- **Extensions** : prosodie, conservation du bruit ambiant, autre langue.
- **Faisabilité** : Whisper + TTS ; utiliser des voix consenties ou synthétiques ; budget cible inférieur à 12 €. Plan B : TTS local Kokoro et extrait libre.

**CoursIA** : [Transcription Pipeline](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/04-Applications/04-2-Transcription-Pipeline.ipynb) · [TTS Voice Benchmark](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/04-Applications/04-7-TTS-Voice-Benchmark.ipynb) · [Audio Video Sync](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/04-Applications/04-4-Audio-Video-Sync.ipynb)

**Références** : [Whisper](https://github.com/openai/whisper) · [pyannote.audio](https://github.com/pyannote/pyannote-audio) · [Kokoro](https://github.com/hexgrad/kokoro)

### D3 — Séparation et restauration de sources audio

**Difficulté : 3/5** · Mots-clés : `source-separation`, `denoising`, `audio`, `benchmark`

Séparer voix, musique et bruit puis restaurer la composante utile sans introduire d'artefacts. Le verrou technique est l'évaluation objective et perceptuelle de la reconstruction.

- **MVP** : corpus de 20 mélanges contrôlés, deux pipelines et interface d'écoute aveugle.
- **Réussite** : SI-SDR, intelligibilité, temps de traitement et préférence humaine.
- **Extensions** : séparation temps réel, plusieurs locuteurs, estimation de confiance.
- **Faisabilité** : Demucs et outils locaux ; GPU facultatif. Plan B : extraits courts pré-calculés.

**CoursIA** : [Demucs Source Separation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/02-Advanced/02-4-Demucs-Source-Separation.ipynb) · [Basic Audio Operations](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/01-Foundation/01-3-Basic-Audio-Operations.ipynb)

**Références** : [Demucs](https://github.com/facebookresearch/demucs) · [MUSDB18](https://sigsep.github.io/datasets/musdb.html) · [BSS Eval](https://arxiv.org/abs/1811.02508)

### D4 — Synthèse vocale expressive et prosodie

**Difficulté : 3/5** · Mots-clés : `tts`, `prosody`, `emotion`, `evaluation`

Contrôler rythme, pauses, accentuation et émotion d'une voix synthétique sur des textes constants. Le verrou technique est de relier paramètres prosodiques et perception sans cloner une voix non consentie.

- **MVP** : 30 phrases, quatre intentions, deux systèmes et mesures acoustiques.
- **Réussite** : reconnaissance d'intention à l'aveugle, naturalité, durée et coût.
- **Extensions** : SSML, transfert de style consenti, contrôle fin.
- **Faisabilité** : voix synthétiques ou consenties uniquement ; API ou moteur local. Plan B : Kokoro local.

**CoursIA** : [Expressive TTS](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/02-Advanced/02-8-Expressive-TTS.ipynb) · [TTS Voice Benchmark](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/04-Applications/04-7-TTS-Voice-Benchmark.ipynb)

**Références** : [SSML](https://www.w3.org/TR/speech-synthesis11/) · [P.808](https://www.itu.int/rec/P-REC-P.808) · [Kokoro](https://github.com/hexgrad/kokoro)

---

## E — Vidéo et médias composés

### E1 — Micro-capsules vidéo pédagogiques

**Difficulté : 3/5** · Mots-clés : `video`, `storyboard`, `education`, `pipeline`

Produire une capsule de 60 à 90 secondes depuis un objectif pédagogique : script, storyboard, plans courts, narration et montage. Le sujet reprend le storyboard jamais livré en 2025, avec un pipeline et une évaluation explicites.

- **MVP** : trois scènes cohérentes, narration, sous-titres et générique des sources.
- **Réussite** : exactitude du contenu, cohérence inter-scènes, lisibilité et comparaison de deux stratégies de génération.
- **Extensions** : audiovisuel joint, accessibilité, traduction.
- **Faisabilité** : génération coûteuse et lente ; plafonner les scènes et le budget à 20 €. Plan B : image-to-video ou slideshow animé.

**CoursIA** : [Educational Video Generation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/04-Applications/04-1-Educational-Video-Generation.ipynb) · [Video Workflow Orchestration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/03-Orchestration/03-2-Video-Workflow-Orchestration.ipynb) · [SVD Image-to-Video](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/02-Advanced/02-4-SVD-Image-to-Video.ipynb)

**Références** : [Diffusers — text-to-video](https://huggingface.co/docs/diffusers/using-diffusers/text-img2vid) · [MoviePy](https://zulko.github.io/moviepy/) · [FFmpeg](https://ffmpeg.org/documentation.html)

### E2 — Benchmark de compréhension temporelle vidéo

**Difficulté : 3/5** · Mots-clés : `video-understanding`, `temporal-qa`, `benchmark`, `multimodal`

Comparer des modèles vision-langage sur des questions temporelles : ordre d'événements, comptage, causalité et détails fugitifs. Ce projet analyse des vidéos ; il n'en génère pas.

- **MVP** : corpus libre de 20 clips, 80 questions annotées et deux modèles.
- **Réussite** : accuracy par catégorie, stabilité aux reformulations, coût et latence.
- **Extensions** : sélection adaptative de frames, troisième modèle local.
- **Faisabilité** : API vision ou Qwen-VL ; budget cible inférieur à 12 €. Plan B : frames pré-extraites.

**CoursIA** : [GPT-5 Video Understanding](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/01-Foundation/01-2-GPT-5-Video-Understanding.ipynb) · [Qwen-VL Video Analysis](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/01-Foundation/01-3-Qwen-VL-Video-Analysis.ipynb) · [Multi-Model Video Comparison](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/03-Orchestration/03-1-Multi-Model-Video-Comparison.ipynb)

**Références** : [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) · [Video-MME](https://arxiv.org/abs/2405.21075) · [MVBench](https://arxiv.org/abs/2311.17005)

### E3 — Pipeline audiovisuel synchronisé

**Difficulté : 4/5** · Mots-clés : `audio-video`, `synchronization`, `subtitles`, `pipeline`

Assembler script, narration, plans et sous-titres en conservant leur alignement temporel. Le verrou technique est la synchronisation mesurée entre modalités, non la génération d'un clip isolé.

- **MVP** : vidéo de 90 secondes, timeline explicite, sous-titres et rapport des décalages.
- **Réussite** : erreur d'alignement audio/vidéo, couverture des sous-titres, lisibilité et temps de production.
- **Extensions** : plusieurs langues, musique adaptative, correction automatique des durées.
- **Faisabilité** : FFmpeg/MoviePy et médias courts ; GPU facultatif. Plan B : plans fixes animés.

**CoursIA** : [Audio Video Sync](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Audio/04-Applications/04-4-Audio-Video-Sync.ipynb) · [Video Workflow Orchestration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/03-Orchestration/03-2-Video-Workflow-Orchestration.ipynb)

**Références** : [FFmpeg](https://ffmpeg.org/documentation.html) · [WebVTT](https://www.w3.org/TR/webvtt1/) · [MoviePy](https://zulko.github.io/moviepy/)

### E4 — Restauration et upscaling vidéo

**Difficulté : 4/5** · Mots-clés : `upscaling`, `restoration`, `temporal-consistency`, `video`

Améliorer une vidéo dégradée tout en évitant scintillement et détails inventés. Le verrou technique est la cohérence temporelle, absente d'un benchmark image par image.

- **MVP** : 15 clips dégradés, deux méthodes, métriques par frame et mesure de stabilité temporelle.
- **Réussite** : PSNR/SSIM, métrique perceptuelle, flicker et étude humaine aveugle.
- **Extensions** : interpolation, restauration de visages, traitement en flux.
- **Faisabilité** : extraits courts et modèles pré-entraînés ; GPU partagé utile. Plan B : résolution réduite.

**CoursIA** : [Video Enhancement ESRGAN](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/01-Foundation/01-4-Video-Enhancement-ESRGAN.ipynb) · [Production Video Pipeline](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Video/04-Applications/04-4-Production-Video-Pipeline.ipynb)

**Références** : [Real-ESRGAN](https://arxiv.org/abs/2107.10833) · [BasicVSR++](https://arxiv.org/abs/2104.13371) · [VMAF](https://github.com/Netflix/vmaf)

---

## F — Plateformes conversationnelles et mise en production

### F1 — QA E2E d'Open WebUI

**Difficulté : 3/5** · Mots-clés : `open-webui`, `playwright`, `e2e`, `multi-tenant`

Étendre une suite Playwright pour couvrir un parcours RAG/outils en environnement multi-tenant, avec isolation et intégration continue.

- **MVP** : dix tests E2E, fixtures isolées, traces/screenshots d'échec et exécution CI.
- **Réussite** : scénarios nominal/erreur, absence de dépendance à l'ordre, rapport de flakiness sur dix runs.
- **Extensions** : accessibilité, charge légère, matrice de versions.
- **Faisabilité** : Docker + navigateur ; GPU inutile ; budget cible inférieur à 5 €. Plan B : réponses de modèle mockées.

**CoursIA** : [RAG Tools QA OWUI](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/Open-WebUI/Playwright-OWUI/04-rag-tools-avances/04-RAG-Tools-QA-OWUI.ipynb) · [Multi-Tenant CI QA](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/Open-WebUI/Playwright-OWUI/05-multi-tenant-ci/05-Multi-Tenant-CI-QA-OWUI.ipynb) · [Chat Streaming QA](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/Open-WebUI/Playwright-OWUI/03-chat-streaming/03-Chat-Streaming-QA-OWUI.ipynb)

**Références** : [Open WebUI docs](https://docs.openwebui.com/) · [Playwright](https://playwright.dev/docs/intro) · [GitHub Actions](https://docs.github.com/en/actions)

### F2 — RAG WordPress isolé et mesuré

**Difficulté : 3/5** · Mots-clés : `wordpress`, `rag`, `isolation`, `drift`

Déployer une instance WordPress jetable, indexer un corpus public et prouver l'isolation entre environnements de vecteurs. Le projet mesure aussi la dérive des réponses après mise à jour du corpus.

- **MVP** : deux espaces isolés, ingestion, requêtes de non-fuite et campagne avant/après mise à jour.
- **Réussite** : recall, citations, tests d'isolation et taux de réponses obsolètes.
- **Extensions** : plusieurs fournisseurs, sauvegarde/restauration, tests E2E.
- **Faisabilité** : Docker WordPress ; GPU inutile ; budget embeddings inférieur à 8 €. Plan B : corpus et embeddings locaux.

**CoursIA** : [Ingestion corpus long RAG](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/AI-Engine-WordPress/03-Functional/03-3-RAG-et-Embeddings/ingestion-corpus-long-rag.ipynb) · [Séparer les environnements de vecteurs](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/AI-Engine-WordPress/03-Functional/03-3-RAG-et-Embeddings/separer-les-environnements-de-vecteurs.ipynb) · [Mesurer la dérive d'un Copilot](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Plateformes-Conversationnelles/AI-Engine-WordPress/03-Functional/03-1-Chatbots/mesurer-la-derive-dun-copilot.ipynb)

**Références** : [WordPress REST API](https://developer.wordpress.org/rest-api/) · [AI Engine](https://meowapps.com/ai-engine/) · [Docker Compose](https://docs.docker.com/compose/)

### F3 — Application GenAI observable avec .NET Aspire

**Difficulté : 4/5** · Mots-clés : `aspire`, `observability`, `streaming`, `integration-tests`

Construire une petite application GenAI distribuée dont les appels modèle, outils et erreurs sont visibles dans des traces, métriques et logs corrélés.

- **MVP** : frontend/API, service agent, streaming, télémétrie et tests d'intégration.
- **Réussite** : retrouver automatiquement une requête de bout en bout, mesurer latence/token, détecter trois pannes injectées.
- **Extensions** : multi-provider, circuit breaker, évaluation continue.
- **Faisabilité** : .NET Aspire + conteneurs ; GPU inutile ; budget cible inférieur à 10 €. Plan B : connecteur modèle simulé.

**CoursIA** : [Aspire Observabilité](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Integrations-DotNet/Aspire/03-Aspire-Observabilite.ipynb) · [Aspire Streaming Agent](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Integrations-DotNet/Aspire/04-Aspire-Streaming-Agent.ipynb) · [Aspire Tests Integration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Integrations-DotNet/Aspire/05-Aspire-Tests-Integration.ipynb)

**Références** : [.NET Aspire](https://learn.microsoft.com/en-us/dotnet/aspire/) · [OpenTelemetry .NET](https://opentelemetry.io/docs/languages/net/) · [Polly](https://www.pollydocs.org/)

### F4 — Routeur multi-fournisseurs avec failover

**Difficulté : 3/5** · Mots-clés : `routing`, `failover`, `multi-provider`, `slo`

Router chaque requête vers un modèle selon ses capacités, son coût et son état, puis basculer proprement en cas d'échec. Le verrou technique est de respecter un SLO sans masquer les différences de comportement entre fournisseurs.

- **MVP** : trois connecteurs, health checks, règles de routage, retries bornés et traces corrélées.
- **Réussite** : 100 requêtes avec pannes injectées ; disponibilité, p95, coût et taux de bascules correctes.
- **Extensions** : circuit breaker, routage appris, cache sémantique.
- **Faisabilité** : APIs à faible volume ou connecteurs simulés ; budget inférieur à 12 €. Plan B : serveur de réponses déterministes.

**CoursIA** : [Model Merging Routing](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-05-ModelMerging-Routing-Python.ipynb) · [SemanticFleet MultiConnector](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Integrations-DotNet/Aspire/07-Aspire-SemanticFleet-MultiConnector.ipynb)

**Références** : [Azure Architecture — Circuit Breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) · [OpenTelemetry](https://opentelemetry.io/docs/) · [Polly](https://www.pollydocs.org/)

---

## G — Ingénierie logicielle assistée par IA

### G1 — Banc d'essai d'agents de codage

**Difficulté : 3/5** · Mots-clés : `coding-agents`, `benchmark`, `cost`, `reproducibility`

Comparer deux configurations d'agents de codage sur une suite fixe de tâches dans des dépôts jetables. Ce n'est pas un code reviewer : l'objet est l'efficacité du processus agentique.

- **MVP** : 12 tâches, environnement réinitialisable, tests cachés et collecte coût/tours/diffs.
- **Réussite** : au moins trois répétitions par tâche, pass@1, coût, temps, régressions et analyse statistique.
- **Extensions** : modèles multiples, qualité des commits, ablation des instructions.
- **Faisabilité** : exécutions coûteuses ; plafonner tours et budget à 20 €. Plan B : traces enregistrées complétées par quelques runs live.

**CoursIA** : [Claude CLI Agents](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claude-Code/notebooks/04-Claude-CLI-Agents.ipynb) · [Claude CLI Automatisation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claude-Code/notebooks/05-Claude-CLI-Automatisation.ipynb) · [Claude Code via Claudish](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claudish/notebooks/01-claude-code-via-claudish.ipynb)

**Références** : [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code/overview) · [SWE-bench](https://www.swebench.com/) · [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)

### G2 — Garde-fous Roslyn pour code généré

**Difficulté : 4/5** · Mots-clés : `roslyn`, `static-analysis`, `generated-code`, `verification`

Créer des analyseurs Roslyn qui interdisent des motifs dangereux ou non conformes dans du C# généré, puis mesurer leur précision sur un corpus contrôlé.

- **MVP** : quatre règles, diagnostics et code fixes, générateur de cas positifs/négatifs.
- **Réussite** : précision/rappel, zéro faux négatif sur règles critiques, tests unitaires et intégration avant compilation.
- **Extensions** : taint analysis, configuration par politique, boucle de réparation LLM.
- **Faisabilité** : .NET uniquement, API facultative, aucun GPU ; budget cible inférieur à 5 €. Plan B : corpus synthétique versionné.

**CoursIA** : [Roslyn Code Guardrails](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/analyzers/Roslyn-Code-Guardrails.ipynb) · [Aspire GardeFous Roslyn](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Integrations-DotNet/Aspire/06-Aspire-GardeFous-Roslyn.ipynb) · [CSharpRepl Live Patching](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/docs/CSharpRepl-Live-Patching.ipynb)

**Références** : [Roslyn analyzers](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/tutorials/how-to-write-csharp-analyzer-code-fix) · [Microsoft.CodeAnalysis.Testing](https://www.nuget.org/packages/Microsoft.CodeAnalysis.Analyzer.Testing/) · [CWE Top 25](https://cwe.mitre.org/top25/)

### G3 — Pair-programming IA en étude contrôlée

**Difficulté : 3/5** · Mots-clés : `pair-programming`, `experiment`, `productivity`, `quality`

Mesurer l'effet d'un assistant de code sur des tâches comparables, avec et sans assistance. Le verrou technique est un protocole contrôlé qui évite de confondre vitesse, qualité et familiarité.

- **MVP** : huit tâches appariées, participants ou runs croisés, journal du temps et tests cachés.
- **Réussite** : taux de réussite, temps, taille des diffs, défauts et charge perçue avec analyse des biais.
- **Extensions** : novices/experts, types de prompts, maintenance différée.
- **Faisabilité** : petits dépôts jetables et budget de tours borné. Plan B : traces enregistrées complétées par des runs automatisés.

**CoursIA** : [Claude CLI Bases](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claude-Code/notebooks/01-Claude-CLI-Bases.ipynb) · [Claude CLI Sessions](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claude-Code/notebooks/02-Claude-CLI-Sessions.ipynb)

**Références** : [METR — Early-2025 AI Coding Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) · [SWE-bench](https://www.swebench.com/) · [SPACE framework](https://queue.acm.org/detail.cfm?id=3454124)

### G4 — Migration de code par tests différentiels

**Difficulté : 4/5** · Mots-clés : `migration`, `differential-testing`, `transpilation`, `regression`

Migrer une petite bibliothèque entre langages ou frameworks avec un assistant, tout en prouvant l'équivalence observable. Le verrou technique est l'oracle différentiel, non la quantité de code généré.

- **MVP** : bibliothèque source, port cible, corpus d'entrées, tests différentiels et rapport des divergences.
- **Réussite** : couverture des comportements, taux d'équivalence, défauts détectés et effort de correction.
- **Extensions** : property-based testing, performances, API incompatibles.
- **Faisabilité** : projet borné à 500–1000 lignes ; aucun GPU. Plan B : fonctions pures et corpus synthétique.

**CoursIA** : [CSharpRepl Live Patching](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/docs/CSharpRepl-Live-Patching.ipynb) · [Code Interpreter](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/07_Code_Interpreter.ipynb)

**Références** : [Hypothesis](https://hypothesis.readthedocs.io/) · [Differential Testing for Software](https://dblp.org/rec/journals/dtj/McKeeman98.html) · [Microsoft — Migration guidance](https://learn.microsoft.com/en-us/dotnet/core/porting/)

---

## H — Évaluation, sécurité et fiabilité

### H1 — Laboratoire red-team d'injection de prompt

**Difficulté : 3/5** · Mots-clés : `prompt-injection`, `red-team`, `tool-use`, `mitigation`

Construire une batterie reproductible d'attaques directes et indirectes contre un agent RAG/outillé, puis comparer plusieurs défenses. Ce sujet traite de sécurité, pas d'équité ou de biais.

- **MVP** : 50 attaques classées, cible instrumentée, deux défenses et rapport automatique.
- **Réussite** : Attack Success Rate avant/après, coût en faux refus, analyse par classe d'attaque.
- **Extensions** : contenu multimodal, canary tokens, fuzzing.
- **Faisabilité** : API texte, outils simulés sans effet réel ; budget cible inférieur à 12 €. Plan B : modèle local.

**CoursIA** : [Prompt Security Red Team](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09b_Prompt_Security_RedTeam.ipynb) · [Function Calling](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/04_Function_Calling.ipynb) · [Production Patterns](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb)

**Références** : [OWASP LLM Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) · [MITRE ATLAS](https://atlas.mitre.org/) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

### H2 — Harness d'évaluation d'agents

**Difficulté : 4/5** · Mots-clés : `agent-evaluation`, `llm-as-judge`, `regression`, `calibration`

Créer une suite de scénarios et un évaluateur hybride déterministe/LLM-as-judge, puis mesurer l'accord avec une annotation humaine et les biais du juge.

- **MVP** : 30 scénarios, assertions sur outils/états, juge à rubric et rapport de régression.
- **Réussite** : accord inter-évaluateurs, sensibilité à l'ordre, stabilité, coût et détection d'une régression injectée.
- **Extensions** : juges multiples, CI, mutation testing d'agents.
- **Faisabilité** : GPU inutile ; séparer données de développement et test ; budget cible inférieur à 15 €. Plan B : juges enregistrés.

**CoursIA** : [Agent Evaluation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/13b_Agent_Evaluation.ipynb) · [Evaluating Generated Text](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/22_Evaluating_Generated_Text.ipynb) · [Semantic Kernel Observability](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/04-SemanticKernel-Filters-Observability.ipynb)

**Références** : [HELM](https://crfm.stanford.edu/helm/latest/) · [OpenAI Evals](https://github.com/openai/evals) · [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)

### H3 — Observatoire du reward hacking

**Difficulté : 5/5** · Mots-clés : `reward-hacking`, `rlvr`, `post-training`, `monitoring`

Concevoir un environnement jouet où un modèle peut optimiser un proxy imparfait, observer l'exploitation de la récompense puis tester des contre-mesures. L'objectif est une expérience scientifique bornée, non l'entraînement d'un grand modèle.

- **MVP** : tâche vérifiable, récompense vulnérable, baseline, attaque observée et deux corrections.
- **Réussite** : plusieurs seeds, courbes récompense réelle/proxy, exemples d'exploitation et reproductibilité.
- **Extensions** : reward model séparé, holdout adversarial, détection en ligne.
- **Faisabilité** : commencer avec l'environnement jouet ; GPU facultatif pour un petit modèle ; budget cible inférieur à 10 €. Plan B : politique tabulaire ou modèle minuscule.

**CoursIA** : [Reward Hacking](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/PostTraining/PT_07_rewardspy_reward_hacking.ipynb) · [RLVR](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/PostTraining/PT_05_rlvr_verifiable_rewards.ipynb) · [GRPO From Scratch](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/PostTraining/PT_08_grpo_from_scratch_toy_env.ipynb)

**Références** : [Specification gaming examples](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) · [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) · [TRL](https://huggingface.co/docs/trl/)

### H4 — Provenance et détection de contenus synthétiques

**Difficulté : 3/5** · Mots-clés : `provenance`, `watermarking`, `detection`, `c2pa`

Comparer métadonnées de provenance, watermarking et classifieurs sur des contenus transformés. Le verrou technique est la robustesse après compression, recadrage ou paraphrase, pas un détecteur présenté sur ses données d'entraînement.

- **MVP** : corpus texte/image, trois transformations, deux méthodes de détection et vérification C2PA.
- **Réussite** : précision/rappel, calibration, robustesse par transformation et taux de faux positifs.
- **Extensions** : chaîne de provenance, attaques adaptatives, interface d'inspection.
- **Faisabilité** : contenus synthétiques et publics uniquement ; GPU non requis. Plan B : caractéristiques pré-calculées.

**CoursIA** : [Production Integration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/04-Applications/04-3-Production-Integration.ipynb) · [Evaluating Generated Text](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/22_Evaluating_Generated_Text.ipynb)

**Références** : [C2PA Specification](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html) · [SynthID](https://deepmind.google/technologies/synthid/) · [NIST GenAI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

### H5 — Constitution IA et coût des refus

**Difficulté : 3/5** · Mots-clés : `constitutional-ai`, `guardrails`, `refusal`, `evaluation`

Définir une politique de réponse, l'appliquer par prompt ou filtre puis mesurer sécurité et sur-refus. Le verrou technique est le compromis entre violations évitées et requêtes légitimes refusées.

- **MVP** : constitution versionnée, 100 scénarios sûrs/limites/dangereux, deux mécanismes et rapport.
- **Réussite** : taux de violation, faux refus, cohérence des explications, coût et latence.
- **Extensions** : critiques multiples, politiques par domaine, tests multilingues.
- **Faisabilité** : outils simulés et API texte ; budget inférieur à 10 €. Plan B : modèle local.

**CoursIA** : [Prompt Security Red Team](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09b_Prompt_Security_RedTeam.ipynb) · [Production Patterns](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb)

**Références** : [Constitutional AI](https://arxiv.org/abs/2212.08073) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) · [OWASP GenAI](https://genai.owasp.org/)

---

## I — Adaptation de modèles et inférence locale

### I1 — QLoRA sans contamination de l'évaluation

**Difficulté : 4/5** · Mots-clés : `qlora`, `fine-tuning`, `data-leakage`, `evaluation`

Adapter un petit modèle à une tâche structurée et prouver que le gain ne vient ni d'une fuite train/test ni d'une mauvaise baseline. Les domaines de biais, recrutement, extraction documentaire et fallacies sont exclus.

- **MVP** : dataset versionné, contrôles de doublons, baseline prompt-only, QLoRA et test tenu à l'écart.
- **Réussite** : métrique adaptée, intervalles de confiance, coût mémoire/temps et analyse d'erreurs.
- **Extensions** : comparaison RAG, quantification, autre taille de modèle.
- **Faisabilité** : Colab ou GPU partagé, petit modèle uniquement ; budget cible inférieur à 10 € ; aucun GPU requis pour la démo si l'adapter est sauvegardé. Plan B : entraînement très réduit.

**CoursIA** : [QLoRA Quantization](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-02-QLoRA-Quantization-Python.ipynb) · [Supervised Fine-Tuning](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-03-Supervised-FineTuning-SFT-Python.ipynb) · [LoRA Fine-Tuning](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/21_LoRA_FineTuning.ipynb)

**Références** : [QLoRA](https://arxiv.org/abs/2305.14314) · [PEFT](https://huggingface.co/docs/peft/) · [Data Contamination in LLMs](https://arxiv.org/abs/2311.04850)

### I2 — Inférence locale .NET face aux API cloud

**Difficulté : 3/5** · Mots-clés : `dotnet`, `local-inference`, `quantization`, `benchmark`

Comparer LLamaSharp, ONNX Runtime GenAI ou TensorSharp à une API cloud sur une tâche contrôlée. Construire une frontière coût–latence–qualité plutôt qu'un simple serveur local.

- **MVP** : deux moteurs locaux ou un local/un cloud, même jeu de 50 requêtes, instrumentation mémoire et tokens.
- **Réussite** : p50/p95, débit, mémoire, qualité, coût projeté et protocole reproductible.
- **Extensions** : quantifications multiples, batching, streaming.
- **Faisabilité** : modèles compacts ; CPU accepté ; budget cloud de comparaison inférieur à 8 €. Plan B : GGUF très quantifié et sous-échantillon.

**CoursIA** : [Inference Mechanics](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/10b_Inference_Mechanics.ipynb) · [ORT GenAI Bake-Off](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/10f_ORTGenAI_DotNet_BakeOff.ipynb) · [Quantization](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/11_Quantization.ipynb)

**Références** : [LLamaSharp](https://github.com/SciSharp/LLamaSharp) · [ONNX Runtime GenAI](https://onnxruntime.ai/docs/genai/) · [llama.cpp](https://github.com/ggml-org/llama.cpp)

### I3 — Frontière coût-précision du test-time compute

**Difficulté : 4/5** · Mots-clés : `reasoning`, `test-time-compute`, `tree-of-thoughts`, `scaling`

Étudier combien de calcul à l'inférence améliore réellement une tâche vérifiable : échantillonnage multiple, vote, Tree of Thoughts et modèle à raisonnement natif.

- **MVP** : deux jeux de problèmes, quatre budgets de calcul, trois stratégies et vérificateur automatique.
- **Réussite** : courbes accuracy/coût/latence, analyse par difficulté et point de rendement décroissant.
- **Extensions** : sélection adaptative du budget, self-consistency pondérée.
- **Faisabilité** : très consommateur de tokens ; budget dur de 20 € et petites séries pilotes. Plan B : modèle local ou résultats mis en cache.

**CoursIA** : [Tree of Thoughts](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/15_Tree_of_Thoughts_Search.ipynb) · [Scaling Test-Time Compute](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/16_Scaling_Test_Time_Compute.ipynb) · [Native Reasoning vs Scaling](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/17_Native_Reasoning_vs_Scaling.ipynb)

**Références** : [Tree of Thoughts](https://arxiv.org/abs/2305.10601) · [Self-Consistency](https://arxiv.org/abs/2203.11171) · [Scaling LLM Test-Time Compute](https://arxiv.org/abs/2408.03314)

### I4 — Fusion et routage de modèles spécialisés

**Difficulté : 5/5** · Mots-clés : `model-merging`, `routing`, `specialization`, `benchmark`

Combiner ou router de petits modèles spécialisés sans perdre leurs compétences propres. Le verrou technique est de démontrer un gain sur un holdout multi-domaines plutôt que sur les données d'adaptation.

- **MVP** : deux spécialistes, une baseline générale, fusion ou routeur et jeu de test tenu à l'écart.
- **Réussite** : qualité par domaine, oubli, mémoire, latence et coût comparés aux spécialistes isolés.
- **Extensions** : plusieurs méthodes de fusion, routeur appris, quantification.
- **Faisabilité** : petits modèles et adapters ; GPU partagé recommandé. Plan B : fusion d'adapters pré-entraînés.

**CoursIA** : [Model Merging Routing](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-05-ModelMerging-Routing-Python.ipynb) · [QLoRA Quantization](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-02-QLoRA-Quantization-Python.ipynb)

**Références** : [MergeKit](https://github.com/arcee-ai/mergekit) · [TIES-Merging](https://arxiv.org/abs/2306.01708) · [PEFT](https://huggingface.co/docs/peft/)

---

## J — Données, science et aide à la décision

### J1 — Assistant de preuves scientifiques

**Difficulté : 3/5** · Mots-clés : `scientific-rag`, `evidence`, `citations`, `uncertainty`

Répondre à une question scientifique par une chaîne d'affirmations reliées à des passages vérifiables. Le verrou technique est la couverture et la force des preuves, non la production d'un résumé d'articles.

- **MVP** : corpus public d'au moins 30 articles, extraction d'affirmations, citations et tableau de preuves contradictoires.
- **Réussite** : précision des citations, couverture des affirmations, contradictions détectées et calibration de l'abstention.
- **Extensions** : graphes de citations, recherche web, réplication de résultats.
- **Faisabilité** : abstracts ou corpus ouvert ; budget inférieur à 12 €. Plan B : corpus local pré-indexé.

**CoursIA** : [PDF Web Search](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/06_PDF_Web_Search.ipynb) · [RAG moderne](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/05_RAG_Modern.ipynb)

**Références** : [Semantic Scholar API](https://api.semanticscholar.org/api-docs/) · [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) · [SciFact](https://arxiv.org/abs/2004.14974)

### J2 — Analyste multimodal de données

**Difficulté : 4/5** · Mots-clés : `data-analysis`, `charts`, `multimodal`, `verification`

Répondre à des questions sur tableaux et graphiques en produisant calculs, visualisations et traces vérifiables. Le verrou technique est la correspondance entre réponse narrative, code exécuté et valeurs sources.

- **MVP** : trois jeux publics, 40 questions, génération de code bornée et rapport liant chaque chiffre à son calcul.
- **Réussite** : exactitude numérique, exécution, fidélité des graphiques et taux de réponses non justifiées.
- **Extensions** : images de graphiques, détection d'anomalies, questions interactives.
- **Faisabilité** : Python/pandas en sandbox ; GPU inutile. Plan B : requêtes et graphiques prédéfinis.

**CoursIA** : [Code Interpreter](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/07_Code_Interpreter.ipynb) · [Semantic Kernel Multimodal](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/07-SemanticKernel-MultiModal.ipynb)

**Références** : [Pandas](https://pandas.pydata.org/docs/) · [Vega-Lite](https://vega.github.io/vega-lite/) · [ChartQA](https://arxiv.org/abs/2203.10244)

### J3 — Expériences reproductibles auto-validées

**Difficulté : 4/5** · Mots-clés : `experiments`, `reproducibility`, `code-generation`, `validation`

Transformer une hypothèse et un protocole structuré en expérience exécutable, puis contrôler que résultats et conclusions restent cohérents. Le verrou technique est la validation automatique de la chaîne expérimentale.

- **MVP** : dix protocoles simples, environnement figé, exécution isolée, contrôles statistiques et rapport.
- **Réussite** : taux d'exécution propre, reproductibilité multi-runs, erreurs méthodologiques détectées et conclusions corrigées.
- **Extensions** : seeds multiples, provenance des données, génération de contre-expériences.
- **Faisabilité** : expériences synthétiques courtes ; aucun GPU. Plan B : templates paramétrés sans génération libre.

**CoursIA** : [NotebookMaker](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/10-SemanticKernel-NotebookMaker.ipynb) · [Evaluating Generated Text](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/22_Evaluating_Generated_Text.ipynb)

**Références** : [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current) · [SciPy](https://docs.scipy.org/doc/scipy/) · [Jupyter Reproducible Research](https://jupyter.org/)

---

## K — IA responsable, gouvernance et sobriété

### K1 — Confidentialité des données synthétiques

**Difficulté : 4/5** · Mots-clés : `synthetic-data`, `privacy`, `utility`, `membership-inference`

Générer des données tabulaires synthétiques et mesurer simultanément utilité et risque de mémorisation. Le verrou technique est de ne pas déclarer les données privées sans attaque ni métrique.

- **MVP** : dataset public, deux générateurs, tests d'utilité et attaque simple d'inférence d'appartenance.
- **Réussite** : compromis utilité/confidentialité, intervalles de confiance et identification des lignes à risque.
- **Extensions** : confidentialité différentielle, attributs rares, audit par sous-groupes.
- **Faisabilité** : données publiques ou artificielles uniquement ; GPU inutile. Plan B : générateurs statistiques.

**CoursIA** : [Structured Outputs](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/03_Structured_Outputs.ipynb) · [Supervised Fine-Tuning](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/FineTuning/FT-03-Supervised-FineTuning-SFT-Python.ipynb)

**Références** : [NIST Privacy Framework](https://www.nist.gov/privacy-framework) · [Membership Inference Attacks](https://arxiv.org/abs/1610.05820) · [SDMetrics](https://docs.sdv.dev/sdmetrics/)

### K2 — Traçabilité et licences des générations

**Difficulté : 2/5** · Mots-clés : `licensing`, `provenance`, `metadata`, `compliance`

Construire une chaîne qui associe à chaque génération ses modèles, prompts, sources, transformations et contraintes de licence. Le verrou technique est la traçabilité exploitable et vérifiable, non un texte juridique généré.

- **MVP** : manifeste JSON, règles de compatibilité simples, trois pipelines média et interface d'audit.
- **Réussite** : couverture des métadonnées, violations injectées détectées, faux positifs et export reproductible.
- **Extensions** : C2PA, SBOM de modèles, politiques organisationnelles.
- **Faisabilité** : métadonnées synthétiques et licences publiques ; aucun GPU. Plan B : artefacts pré-générés.

**CoursIA** : [Production Integration](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/04-Applications/04-3-Production-Integration.ipynb) · [Production Patterns](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb)

**Références** : [SPDX](https://spdx.dev/) · [Model Cards](https://arxiv.org/abs/1810.03993) · [C2PA](https://c2pa.org/)

### K3 — Sobriété : coût, énergie et tokens

**Difficulté : 3/5** · Mots-clés : `efficiency`, `energy`, `tokens`, `benchmark`

Mesurer puis réduire les ressources consommées par une tâche GenAI sans dégrader excessivement sa qualité. Le verrou technique est une frontière qualité–coût–énergie instrumentée.

- **MVP** : 50 requêtes, trois configurations, comptage tokens/temps/énergie estimée et stratégie d'optimisation.
- **Réussite** : courbes de Pareto, répétitions, économie obtenue et impact qualité statistiquement décrit.
- **Extensions** : quantification, batching, cache, routage local/cloud.
- **Faisabilité** : petits modèles et mesures logicielles ; budget inférieur à 10 €. Plan B : estimation énergétique documentée.

**CoursIA** : [Quantization](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/11_Quantization.ipynb) · [Performance Optimization](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/03-Orchestration/03-3-Performance-Optimization.ipynb)

**Références** : [CodeCarbon](https://mlco2.github.io/codecarbon/) · [MLCO2 Impact](https://mlco2.github.io/impact/) · [Green Algorithms](https://www.green-algorithms.org/)

---

## L — Applications sectorielles évaluables

### L1 — Assistant médical borné avec abstention

**Difficulté : 4/5** · Mots-clés : `healthcare`, `abstention`, `grounding`, `safety`

Répondre sur un corpus médical public et limité, avec citations et abstention hors périmètre. Le verrou technique est la détection d'incertitude et d'hors-domaine ; le système ne pose aucun diagnostic réel.

- **MVP** : corpus institutionnel, 60 questions incluant pièges/hors-domaine, réponses citées et mécanisme d'abstention.
- **Réussite** : exactitude, fidélité des citations, courbe couverture-risque et erreurs critiques analysées.
- **Extensions** : langage patient/professionnel, contradictions, revue experte.
- **Faisabilité** : données publiques et scénarios fictifs uniquement. Plan B : réponses extractives locales.

**CoursIA** : [Medical Chatbot](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/CaseStudies/Medical-Chatbot/medical_chatbot.ipynb) · [Hands-On Grounding](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/RAG-et-Memoire-Semantique/01-Hands-On-Grounding.ipynb)

**Références** : [WHO — Ethics and governance of AI for health](https://www.who.int/publications/i/item/9789240029200) · [TRIPOD+AI](https://www.tripod-statement.org/) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

### L2 — Analyse financière sourcée et auditable

**Difficulté : 3/5** · Mots-clés : `finance`, `filings`, `citations`, `audit`

Extraire des indicateurs de rapports publics et produire une analyse dont chaque chiffre est relié à sa source et à son calcul. Le verrou technique est l'auditabilité numérique, non la recommandation d'investissement.

- **MVP** : dix rapports publics, 30 questions, extraction structurée, calculs vérifiés et citations de pages.
- **Réussite** : exactitude numérique, provenance, détection de périodes/unités incompatibles et taux d'abstention.
- **Extensions** : tableaux scannés, comparaison d'entreprises, détection d'anomalies.
- **Faisabilité** : rapports publics ; aucun conseil financier réel. Plan B : petit corpus local annoté.

**CoursIA** : [PDF Web Search](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/06_PDF_Web_Search.ipynb) · [Structured Outputs](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/03_Structured_Outputs.ipynb)

**Références** : [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) · [XBRL International](https://www.xbrl.org/) · [FinQA](https://arxiv.org/abs/2109.00122)

### L3 — Tuteur adaptatif avec mesure d'apprentissage

**Difficulté : 4/5** · Mots-clés : `education`, `tutoring`, `adaptation`, `learning-gain`

Adapter explications et exercices à un modèle explicite de maîtrise, sans se réduire à générer un quiz. Le verrou technique est la décision pédagogique et la mesure du progrès.

- **MVP** : domaine borné, diagnostic initial, trois niveaux d'aide, journal de maîtrise et évaluation pré/post.
- **Réussite** : gain d'apprentissage sur scénarios ou utilisateurs consentants, calibration du modèle et qualité des feedbacks.
- **Extensions** : oubli espacé, plusieurs stratégies, accessibilité.
- **Faisabilité** : contenu public et données synthétiques ; étude humaine facultative et consentie. Plan B : apprenants simulés.

**CoursIA** : [Educational Content Generation](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Image/04-Applications/04-1-Educational-Content-Generation.ipynb) · [NotebookMaker](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/SemanticKernel/10-SemanticKernel-NotebookMaker.ipynb)

**Références** : [Knowledge Tracing](https://dl.acm.org/doi/10.5555/1161135.1161179) · [UNESCO guidance for generative AI in education](https://unesdoc.unesco.org/ark:/48223/pf0000386693) · [Bloom's taxonomy](https://cft.vanderbilt.edu/guides-sub-pages/blooms-taxonomy/)

---

## Proposer un sujet libre

Un sujet libre doit définir un verrou technique différent des [réalisations historiques](HISTORIQUE-SUJETS.md), un MVP en six semaines, une baseline, des métriques, deux ressources CoursIA, trois références externes et un plan B. Utilisez le [formulaire de proposition](https://github.com/jsboigeEPF/2026-MSMIN5IN52-GenAI/issues/new?template=proposition-sujet.yml) avant tout développement.
