# AdaptiveTutor: A Conversational Learning System
### Complete Plan - Research Design + Deployable Prototype on Vercel

---

**Languages: [English](#english-version) | [Français](#version-française)**

---

<a name="english-version"></a>

## Table of Contents (English)

1. [Project Goal](#1-project-goal)
2. [Dataset: QReCC Analysis](#2-dataset-qrecc-analysis)
3. [Limitations of Existing Approaches](#3-limitations-of-existing-approaches)
4. [Two Foundational Design Principles](#4-two-foundational-design-principles)
5. [Prototype Scope: What Is Built Now vs. Deferred](#5-prototype-scope-what-is-built-now-vs-deferred)
6. [Prototype System Architecture](#6-prototype-system-architecture)
7. [Deployment Architecture: Vercel + Hugging Face](#7-deployment-architecture-vercel--hugging-face)
8. [Skills Directory: Where Pedagogical Knowledge Lives](#8-skills-directory-where-pedagogical-knowledge-lives)
9. [Defense-in-Depth: Adapted for the Prototype](#9-defense-in-depth-adapted-for-the-prototype)
10. [Module 1 - Lightweight Browser-State Memory](#10-module-1--lightweight-browser-state-memory)
11. [Module 2 - Proactive Question Clarity Engine](#11-module-2--proactive-question-clarity-engine)
12. [Module 3 - Adaptive Teaching Behaviour](#12-module-3--adaptive-teaching-behaviour)
13. [Module 6 - Confusion and Misunderstanding Detector](#13-module-6--confusion-and-misunderstanding-detector)
14. [Prototype Fallback Strategy](#14-prototype-fallback-strategy)
15. [Evaluation Framework](#15-evaluation-framework)
16. [Project Structure](#16-project-structure)
17. [Technology Stack](#17-technology-stack)
18. [Milestone Roadmap](#18-milestone-roadmap)
19. [Full System: What Gets Built Next](#19-full-system-what-gets-built-next)
20. [Summary of Novel Contributions](#20-summary-of-novel-contributions)

---

## 1. Project Goal

The goal is to build **AdaptiveTutor**: an AI system that supports realistic teacher–student learning conversations, grounded in the QReCC conversational dataset.

This is not a standard QA system. The emphasis is on research innovation - on making AI genuinely better at the *pedagogical* task, not just the *retrieval* task:

- Understanding follow-up questions that rely on prior context
- Detecting when a student is confused before they explicitly say so
- Adapting explanation style to match a student's apparent proficiency
- Maintaining a coherent topic arc across a multi-turn conversation
- Giving the student a better *learning experience*, not just a more accurate answer

The plan is structured in two tiers. The **prototype** is a public, deployable web application on Vercel using the Hugging Face Inference API - no local GPU, no server to manage, accessible to anyone via a URL. The **full system** extends the prototype with the complete module set, local model inference, BM25 retrieval, a domain concept graph, and production observability.

---

## 2. Dataset: QReCC Analysis

### 2.1 What QReCC Is

QReCC(http://github.com/apple/ml-qrecc/tree/main) (Question Rewriting in Conversational Context) is a dataset released by Apple containing:

- **14,000 conversations**, **81,000 question-answer pairs**
- Average **6 turns per conversation**
- Built from three source datasets:
  - **QuAC** - document-grounded, exploratory Q&A (Wikipedia articles)
  - **TREC CAsT** - search-session conversations, information-seeking
  - **Google Natural Questions** - factual questions adapted into multi-turn conversations

### 2.2 Data Schema

Each conversation turn provides:

| Field | Description |
|---|---|
| `Conversation_no` | Unique conversation ID |
| `Turn_no` | Turn index within the conversation |
| `Question` | Raw question - may use pronouns, ellipsis, incomplete phrasing |
| `Context` | Alternating list of all prior questions and answers |
| `Rewrite` | Human-annotated standalone, self-contained rewrite of the question |
| `Answer` | Human-produced answer, sourced from the web |
| `Answer_URL` | Source URL |
| `Conversation_source` | QuAC, NQ, or TREC CAsT |

The raw `Question` is ambiguous. The `Rewrite` resolves this using context. This annotation is the training signal for context-dependent disambiguation.

### 2.3 Key Linguistic Phenomena in Student Questions

**Anaphora / coreference:** *"Who is she?"*, *"What did they do next?"* - the referent lives only in a prior turn.

**Ellipsis:** *"And before that?"*, *"What about the cost?"* - topic inherited from the prior turn without being stated.

**Topic drift:** Conversation shifts to a related but distinct topic mid-stream.

**Implicit presupposition:** *"Why did it fail?"* where "it" refers to a concept explained three turns back.

**Exploratory follow-ups:** *"Can you say more?"*, *"What does that mean in practice?"* - student building a mental model, not just retrieving a fact.

### 2.4 What QReCC Does Not Label

QReCC labels are designed for information retrieval evaluation. They do not capture:

- Whether the student was confused by the previous answer
- The student's proficiency level
- Whether the answer satisfied the student's actual learning goal
- Pedagogical quality of the answer - only factual accuracy

These absent labels define the research space. Every module in this system addresses something QReCC treats as invisible.

---

## 3. Limitations of Existing Approaches

### 3.1 Question Rewriting as the Only Context Strategy

The standard pipeline is: rewrite the ambiguous question → retrieve passages → generate an answer. Context is treated as a disambiguation tool only.

**Why this fails for learning:** Context in a learning conversation encodes what the student already knows, what they are struggling with, and their stage of understanding. Compressing all of this into a rewritten query discards the pedagogical signal entirely.

### 3.2 Answer Correctness as the Only Metric

All QReCC baselines optimise for F1 and Exact Match. These measure whether the right information was retrieved, not whether it was communicated effectively.

**Why this fails for learning:** A factually correct answer can be pedagogically poor - too technical, too brief, or disconnected from the student's current understanding. Optimising for F1 produces a better search engine, not a better tutor.

### 3.3 No Learner Model

Every question is treated identically regardless of who is asking and what they already know. There is no persistent representation of the student.

---

## 4. Two Foundational Design Principles

### Principle A - Defense-in-Depth for LLM Output

The model will fail - in production, on inputs not anticipated during development. The system is built so that failure is caught, routed, and made invisible to the student. Five layers wrap every LLM call:

```
Layer 0: Constrained output    - model prompted to produce only valid JSON
Layer 1: Pydantic schemas      - output validated against typed models
Layer 2: Regex validators      - semantic and security checks on field values
Layer 3: Logic gates           - deterministic pedagogical business rules
Layer 4: Fallback              - failed calls route to a safe fallback response
```

### Principle B - Skills Directories Over Agent Frameworks

All pedagogical knowledge lives in a directory of `SKILL.md` files in plain English. Python is the thin orchestrator that reads the right file and includes it in the LLM system prompt.

---

## 5. Prototype Scope: What Is Built Now vs. Deferred

The full system has seven modules. The prototype implements four - the ones that demonstrate the most distinctive research contributions.

- **Module 1 (simplified)**: Lightweight conversation memory carried in the browser.
- **Module 2**: Three-way question classifier + proactive clarification.
- **Module 3**: Adaptive explanation style via SKILL.md files.
- **Module 6**: Two-layer confusion detector.

---

## 6. Prototype System Architecture

A turn in the prototype flows through a 5-step pipeline:
1. **Confusion Detection**: Rule layer checks for repetition/contradiction.
2. **Question Classification**: Decides if the question is self-contained, resolvable, or indicating confusion.
3. **Style Selection**: Estimates proficiency and selects the appropriate SKILL.md.
4. **Answer Generation**: Streams the response using the selected pedagogical style.
5. **Memory Update**: Extracts new facts to update the session state.

---

## 7. Deployment Architecture: Vercel + Hugging Face

- **Frontend**: Next.js 14 on Vercel.
- **Backend**: Vercel Python serverless functions (`api/turn.py`).
- **Inference**: Hugging Face Inference API (Mistral-7B).
- **State**: Session state lives in the browser, sent with each request.

---

## 8. Skills Directory: Where Pedagogical Knowledge Lives

Pedagogical knowledge is stored in `/skills/*.md` files. This allows for rapid updates without code changes. For example, a teacher can edit `foundation/SKILL.md` to improve how analogies are used for beginners.

---

## 15. Evaluation Framework (CLQ Metrics)

We introduced six novel metrics for **Conversational Learning Quality**:
- **CRR (Confusion Resolution Rate)**: Success in resolving student misunderstandings.
- **ESP (Explanation Style Precision)**: Accuracy of matching style to student proficiency.
- **CCE (Comprehension Check Engagement)**: Quality of student responses to check-in questions.
- **CUR (Context Utilisation Rate)**: How well prior facts are used in answers.
- **URR (Unnecessary Repetition Rate)**: Minimizing redundant explanations.
- **CP (Clarification Precision)**: Effectiveness of clarification requests.

---

<a name="version-française"></a>

# 🇫🇷 Version Française : AdaptiveTutor

## Table des Matières (Français)

1. [Objectif du Projet](#f1-objectif-du-projet)
2. [Dataset : Analyse de QReCC](#f2-dataset-analyse-de-qrecc)
3. [Limitations des Approches Existantes](#f3-limitations-des-approches-existantes)
4. [Deux Principes de Conception Fondamentaux](#f4-deux-principes-de-conception-fondamentaux)
5. [Portée du Prototype : Construit vs Différé](#f5-portee-du-prototype)
6. [Architecture Système du Prototype](#f6-architecture-systeme)
7. [Architecture de Déploiement : Vercel + Hugging Face](#f7-architecture-de-deploiement)
8. [Répertoire des "Skills" : Le savoir pédagogique](#f8-repertoire-des-skills)
9. [Défense en Profondeur : Adaptée pour le Prototype](#f9-defense-en-profondeur)
10. [Module 1 - Mémoire de l'état du navigateur](#f10-module-1)
11. [Module 2 - Moteur de clarté de question proactif](#f11-module-2)
12. [Module 3 - Comportement d'enseignement adaptatif](#f12-module-3)
13. [Module 6 - Détecteur de confusion et d'incompréhension](#f13-module-6)
14. [Stratégie de Fallback du Prototype](#f14-strategie-de-fallback)
15. [Cadre d'Évaluation (Métriques CLQ)](#f15-cadre-devaluation)
16. [Structure du Projet](#f16-structure-du-projet)
17. [Pile Technologique](#f17-pile-technologique)
18. [Feuille de Route (Jalons)](#f18-feuille-de-route)
19. [Système Complet : Prochaines Étapes](#f19-systeme-complet)
20. [Résumé des Contributions Nouvelles](#f20-resume-des-contributions)

---

<a name="f1-objectif-du-projet"></a>

## 1. Objectif du Projet

L'objectif est de construire **AdaptiveTutor** : un système d'IA qui soutient des conversations d'apprentissage réalistes entre enseignant et élève, basé sur le jeu de données conversationnel QReCC.

Il ne s'agit pas d'un système de questions-réponses standard. L'accent est mis sur l'innovation en recherche - pour rendre l'IA véritablement meilleure dans la tâche *pédagogique*, et pas seulement dans la tâche de *recherche d'information* :

- Comprendre les questions de suivi qui dépendent du contexte précédent.
- Détecter quand un élève est confus avant même qu'il ne l'exprime explicitement.
- Adapter le style d'explication au niveau de maîtrise apparent de l'élève.
- Maintenir une cohérence thématique sur une conversation de plusieurs tours.
- Offrir à l'élève une meilleure *expérience d'apprentissage*, pas seulement une réponse plus précise.

Le plan est structuré en deux niveaux. Le **prototype** est une application web publique déployable sur Vercel utilisant l'API d'Inférence Hugging Face. Le **système complet** étend le prototype avec l'ensemble des modules, l'inférence locale, la recherche BM25, un graphe de concepts et une observabilité de production.

---

<a name="f2-dataset-analyse-de-qrecc"></a>

## 2. Dataset : Analyse de QReCC

### 2.1 Qu'est-ce que QReCC ?

QReCC (Question Rewriting in Conversational Context) est un jeu de données publié par Apple contenant :

- **14 000 conversations**, **81 000 paires de questions-réponses**.
- Moyenne de **6 tours par conversation**.
- Construit à partir de trois sources : QuAC (Wikipedia), TREC CAsT (recherche d'information) et Google Natural Questions.

### 2.2 Schéma des Données

Chaque tour de conversation fournit la question brute (`Question`), le contexte précédent (`Context`), et surtout une reformulation humaine complète (`Rewrite`) qui résout les ambiguïtés. Cette annotation est le signal d'apprentissage pour la désambiguïsation dépendante du contexte.

### 2.3 Phénomènes Linguistiques Clés dans les Questions des Élèves

**Anaphore / Coréférence :** *"Qui est-elle ?"*, *"Qu'ont-ils fait ensuite ?"* - le référent n'existe que dans un tour précédent.

**Ellipse :** *"Et avant cela ?"*, *"Qu'en est-il du coût ?"* - le sujet est hérité du tour précédent sans être nommé.

**Dérive thématique :** La conversation glisse vers un sujet lié mais distinct en plein milieu de l'échange.

**Incompréhension implicite :** *"Pourquoi cela a-t-il échoué ?"* où "cela" fait référence à un concept expliqué trois tours plus tôt.

### 2.4 Ce que QReCC n'étiquette pas

QReCC est conçu pour l'évaluation de la recherche d'information. Il ne capture pas si l'élève a été confus par la réponse précédente, son niveau de compétence, ou la qualité pédagogique de la réponse. Ces absences définissent notre espace de recherche.

---

<a name="f3-limitations-des-approches-existantes"></a>

## 3. Limitations des Approches Existantes

### 3.1 La reformulation comme seule stratégie de contexte

Le pipeline standard reformule la question ambiguë puis cherche une réponse. Le contexte n'est traité que comme un outil de désambiguïsation.

**Pourquoi cela échoue pour l'apprentissage :** Le contexte code ce que l'élève sait déjà et ses difficultés. Tout compresser dans une simple requête reformulée fait perdre le signal pédagogique.

### 3.2 L'exactitude de la réponse comme seule métrique

Les modèles optimisent le score F1 (récupération d'information), mais une réponse factuellement correcte peut être pédagogiquement médiocre : trop technique, trop brève ou déconnectée du niveau de l'élève.

### 3.3 Absence de modèle de l'apprenant

Chaque question est traitée de la même manière, quel que soit l'élève. Sans représentation persistante de l'apprenant, le tuteur ne peut pas s'adapter.

---

<a name="f4-deux-principes-de-conception-fondamentaux"></a>

## 4. Deux Principes de Conception Fondamentaux

### Principe A - Défense en Profondeur pour les sorties LLM

Le modèle peut échouer. Le système est construit pour que l'échec soit capté et rendu invisible pour l'élève via 5 couches :
1. **Sortie contrainte** (JSON uniquement).
2. **Schémas Pydantic** (Validation des types).
3. **Validateurs Regex** (Sécurité et sémantique).
4. **Portes logiques** (Règles pédagogiques déterministes).
5. **Fallback** (Réponse de secours sécurisée).

### Principe B - Répertoires de "Skills" (Compétences)

Tout le savoir pédagogique vit dans des fichiers `SKILL.md` en langage clair. Python n'est que l'orchestrateur qui injecte le bon fichier dans le prompt système du LLM.

---

<a name="f15-cadre-devaluation"></a>

## 15. Cadre d'Évaluation (Métriques CLQ)

Nous introduisons six nouvelles métriques pour la **Qualité de l'Apprentissage Conversationnel** (CLQ) :

- **CRR (Confusion Resolution Rate)** : Taux de succès dans la résolution des malentendus.
- **ESP (Explanation Style Precision)** : Précision de la correspondance entre le style et le niveau de l'élève.
- **CCE (Comprehension Check Engagement)** : Qualité des réponses de l'élève aux questions de vérification.
- **CUR (Context Utilisation Rate)** : Capacité à réutiliser les faits précédemment établis.
- **URR (Unnecessary Repetition Rate)** : Minimisation des explications redondantes sur des faits déjà connus.
- **CP (Clarification Precision)** : Efficacité des demandes de clarification du tuteur.

---

*Prototype : Next.js + Fonctions Python Vercel + API Inférence Hugging Face.*
*Système complet : Étend le prototype avec inférence locale, recherche BM25 et graphe de concepts.*
