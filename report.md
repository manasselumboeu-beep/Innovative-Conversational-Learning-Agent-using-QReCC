# 🎓 Project Report: AdaptiveTutor - A Conversational Learning System


## 1. Project Overview
**AdaptiveTutor** is an innovative conversational learning agent built on the QReCC dataset. It is designed to detect student confusion, adapt explanation styles in real-time, and improve dialogue quality beyond simple answer correctness. Unlike standard QA systems, AdaptiveTutor behaves like a proactive teacher, not just a search engine.

this project uses a highly structured "Skill-Based Prompting" system. It is the core of how the tutor adapts its behavior without requiring a massive, static prompt for every turn.

  Instead of one long prompt, the system dynamically assembles a system prompt by layering several Markdown files (SKILL.md) based on the current context:

  1. The Prompt Architecture
  The system builds the final prompt in modules/adaptive_teacher.py using these layers:
   * INDEX.md (Global): Defines the identity of "AdaptiveTutor" and general pedagogical principles (e.g., "One concept at a time," "Never say 'simply'").
   * Style Skills: Depending on your calculated proficiency, it loads either explanation/foundation/SKILL.md, standard/SKILL.md, or expert/SKILL.md. These control technical depth and sentence length.
  2. Why is it needed?
  This system is critical for several reasons:
   * Latency & Cost: By only loading the "skills" needed for the current turn, the prompt stays lean, saving tokens and speeding up response times.
   * Consistency: The Markdown-based skills act as "pedagogical guardrails," ensuring the AI doesn't break character or use condescending language.
   * Maintainability: If you want to change how the tutor explains complex physics, you only edit skills/domain/science/physics/SKILL.md rather than hunting through Python code or a 5,000-word prompt file.

  3. Meta-Prompts
  The project also uses specialized Meta-Prompts for background tasks (found in skills/meta/):
   * question_classification: Decides if your question needs context resolution.
   * memory_extraction: Analyzes the tutor's own answers to extract "Facts" it has taught you, which are then saved to your LearnerState.

---

## 2. Supporting Learning Dialogue
To better support learning dialogue, AI must move beyond static retrieval. AdaptiveTutor addresses this through four key dimensions:

*   **Understanding Follow-up Questions**: Instead of treating follow-ups as isolated queries, our system uses a **Proactive Question Clarity Engine**. It identifies whether a question is self-contained or requires context resolution (resolvable).
*   **Maintaining Conversational Context**: We replace flat history concatenation with a **Structured Episodic Memory**. This tracks not only the dialogue history but also the "Learner State"—what the student already knows and their current level of understanding.
*   **Adapting Explanations**: The system estimates student proficiency in real-time. It dynamically injects different pedagogical "skills" (Foundation, Standard, Expert) to ensure the language complexity matches the student's needs.
*   **Improving Learning Interactions**: We shift the focus from "giving the right answer" to "ensuring understanding." This is achieved through proactive confusion detection and targeted clarification requests that guide the student back to the learning path.

---

## 3. Dataset Exploration and Analysis: QReCC

### 3.1 What is QReCC?
QReCC (*Question Rewriting in Conversational Context*) is a large-scale dataset containing **14,000 conversations** and **81,000 question-answer pairs**, averaging 6 turns per conversation. It combines data from QuAC (document-grounded), TREC CAsT (information-seeking), and Google Natural Questions.

### 3.2 Dataset Schema
Each turn in the dataset provides:
- `Question`: The raw, often ambiguous student question.
- `Context`: History of previous questions and answers.
- `Rewrite`: A human-annotated, self-contained version of the question.
- `Answer`: The factual answer and source URL.

### 3.3 How QReCC was used in this Project
QReCC was not just a data source; it informed the core architecture:
- **Rewrite Annotations**: Used as the training/signal source for our **Module 2 (Question Clarity Engine)** to distinguish between self-contained and resolvable questions.
- **Conversation Structure**: Informed the design of the **Module 1 (Episodic Memory)**, ensuring the agent maintains context over multiple turns.
- **Evaluation**: The test set is used to compute both standard accuracy metrics and our novel **Conversational Learning Quality (CLQ) metrics**.
- **Research Gap**: By identifying what QReCC *doesn't* label (student confusion, proficiency, pedagogical quality), we defined the research space for our innovation components.

---

## 4. Limitations of Existing Approaches
Existing systems based on QReCC often suffer from five key limitations that AdaptiveTutor specifically addresses:
1. **Context as Disambiguation Only**: Discarding pedagogical signals by treating context only as a way to rewrite queries.
2. **F1/Exact Match Bias**: Optimizing for factual retrieval while ignoring communication effectiveness.
3. **No Learner Model**: Treating every student identically regardless of their knowledge.
4. **Purely Reactive Nature**: Never asking for clarification or checking understanding.
5. **Absence of Confusion Signals**: Failing to detect when a student is lost, leading to compounded misunderstandings.

---

## 5. Novel Strategies & Innovation Components
AdaptiveTutor satisfies the project requirements through the following innovative strategies:

| Requirement | Innovation Strategy in AdaptiveTutor |
| :--- | :--- |
| **1. Conversation Context Modelling** | **Module 1**: Structured episodic memory object (Browser-state) replacing flat history concatenation. |
| **2. Question Clarity Strategy** | **Module 2**: Three-way classifier (self-contained / resolvable / confusion-indicating) with proactive clarification. |
| **3. Adaptive Teaching Behaviour** | **Module 3**: Proficiency-estimated style switching (Foundation/Standard/Expert) via SKILL.md injection. |
| **4. Domain-Specific Tutor** | Scoped to high school science (Biology/Physics) with dedicated pedagogical skills. |
| **5. Interaction Quality vs Correctness** | Implementation of **CLQ Metrics** and a skills-based approach focusing on pedagogical flow. |
| **6. Combined Multiple Techniques** | Hybrid approach using rule-based detection, Pydantic validation, and LLM-driven generation. |
| **7. CLQ Evaluation Metric** | **Section 15.2**: Six novel metrics (CRR, ESP, CCE, CUR, URR, CP) with a human validation protocol. |
| **8. Confusion Detection** | **Module 6**: Two-layer confusion detector with a five-class taxonomy (Repetition, Vague, Contradiction, etc.). |
| **9. Lightweight Agent** | Built using **Mistral-7B** (via API) and **Phi-3-mini** (planned for local), avoiding massive compute needs. |
| **10. Multi-turn Coherence** | Module logic designed to maintain topic arcs and resolve ambiguities across turns. |

---

## 6. System Architecture & Prompt Engineering

### 6.1 Skill-Based Prompting System
This project uses a highly structured "Skill-Based Prompting" system. It is the core of how the tutor adapts its behavior without requiring a massive, static prompt for every turn. Instead of one long prompt, the system dynamically assembles a system prompt by layering several Markdown files (`SKILL.md`) based on the current context:

1. **The Prompt Architecture**: The system builds the final prompt in `modules/adaptive_teacher.py` using these layers:
   * **INDEX.md (Global)**: Defines the identity of "AdaptiveTutor" and general pedagogical principles (e.g., "One concept at a time," "Never say 'simply'").
   * **Style Skills**: Depending on your calculated proficiency, it loads either `explanation/foundation/SKILL.md`, `standard/SKILL.md`, or `expert/SKILL.md`. These control technical depth and sentence length.

2. **Why is it needed?**: This system is critical for several reasons:
   * **Latency & Cost**: By only loading the "skills" needed for the current turn, the prompt stays lean, saving tokens and speeding up response times.
   * **Consistency**: The Markdown-based skills act as "pedagogical guardrails," ensuring the AI doesn't break character or use condescending language.
   * **Maintainability**: If you want to change how the tutor explains complex physics, you only edit `skills/domain/science/physics/SKILL.md` rather than hunting through Python code or a 5,000-word prompt file.

3. **Meta-Prompts**: The project also uses specialized Meta-Prompts for background tasks (found in `skills/meta/`):
   * **question_classification**: Decides if your question needs context resolution.
   * **memory_extraction**: Analyzes the tutor's own answers to extract "Facts" it has taught you, which are then saved to your `LearnerState`.

---

## 7. Conversational Learning Quality (CLQ) Metrics
To measure success beyond simple accuracy, we introduced six novel metrics:
- **CRR (Confusion Resolution Rate)**: Success in resolving student misunderstandings.
- **ESP (Explanation Style Precision)**: Accuracy of matching style to student proficiency.
- **CCE (Comprehension Check Engagement)**: Quality of student responses to check-in questions.
- **CUR (Context Utilisation Rate)**: How well prior facts are used in answers.
- **URR (Unnecessary Repetition Rate)**: Minimizing redundant explanations of known facts.
- **CP (Clarification Precision)**: Effectiveness of the agent's clarification requests.

---

## 8. Real-life Learning Scenarios
To illustrate the system's impact, consider these three real-life pedagogical scenarios:

*   **Scenario A: The "Drilling Down" Student**
    *   *Behavior*: After a standard explanation of Photosynthesis, the student asks "Wait, what about the sun?". 
    *   *AI Support*: The system classifies this as **resolvable**, rewrites it to "What is the role of the sun in photosynthesis?", and maintains the **Standard** style since understanding is progressing.
*   **Scenario B: The Lost Student**
    *   *Behavior*: The student asks the same question twice or says "I don't get it."
    *   *AI Support*: **Module 6** detects **repetition** or **vague** confusion. The system immediately switches to **Foundation** style, loads the `handle_confusion` skill, and uses a concrete analogy (e.g., comparing a cell to a factory) instead of technical definitions.
*   **Scenario C: The Advanced Student**
    *   *Behavior*: The student uses high-level vocabulary and shows quick understanding over 3+ turns.
    *   *AI Support*: The **Adaptive Teacher** detects the lack of confusion and high vocabulary complexity. It upgrades the style to **Expert**, providing more technical depth and citing scientific sources without being asked.

---

# 🇫🇷 Rapport de Projet : AdaptiveTutor

## 1. Description du Projet
**AdaptiveTutor** est un agent d'apprentissage conversationnel innovant basé sur le jeu de données QReCC. Il détecte la confusion de l'élève, adapte son style d'explication en temps réel et améliore la qualité du dialogue au-delà de la simple correction des réponses.

## 2. Soutien au Dialogue d'Apprentissage
L'IA peut mieux soutenir le dialogue d'apprentissage en se concentrant sur quatre aspects fondamentaux :

*   **Compréhension des questions de suivi** : Grâce à un moteur de clarté qui analyse si une question nécessite le contexte précédent pour être comprise.
*   **Maintien du contexte conversationnel** : En utilisant une mémoire épisodique structurée qui suit l'évolution des connaissances de l'élève.
*   **Adaptation des explications** : Par l'ajustement dynamique du niveau de langage (Fondation, Standard, Expert) en fonction de la maîtrise démontrée par l'élève.
*   **Amélioration des interactions d'apprentissage** : En ne se contentant pas de répondre, mais en vérifiant activement la compréhension et en demandant des clarifications si nécessaire.

## 3. Système de Prompting Basé sur les "Skills" (Compétences)
Ce projet utilise un système de "Skill-Based Prompting" hautement structuré. C'est le cœur de l'adaptation du tuteur sans nécessiter un prompt statique massif pour chaque tour. Au lieu d'un seul long prompt, le système assemble dynamiquement un prompt système en superposant plusieurs fichiers Markdown (`SKILL.md`) en fonction du contexte actuel :

1. **Architecture du Prompt** : Construit le prompt final dans `modules/adaptive_teacher.py` en utilisant des couches comme `INDEX.md` et des **Skills de Style** (Fondation/Standard/Expert).
2. **Utilité** : Réduit la latence et les coûts, garantit la cohérence pédagogique et facilite la maintenance.
3. **Meta-Prompts** : Utilisés pour la classification des questions et l'extraction de faits en arrière-plan.

## 4. Analyse du Dataset QReCC et Stratégies Innovantes
Le projet utilise le dataset QReCC de trois manières concrètes :
- **Rewriting** : Les annotations humaines servent de signal pour notre moteur de clarté.
- **Structure de Conversation** : Les échanges multi-tours informent la conception de notre mémoire de session.
- **Évaluation** : Utilisation du jeu de tests pour calculer nos six nouvelles métriques **CLQ** (Conversational Learning Quality).

## 5. Limitations des Approches Existantes
Le système répond aux lacunes des modèles actuels :
- **Contexte limité à la désambiguïsation** : Nous l'utilisons pour modéliser l'apprenant.
- **Biais vers la métrique F1** : Nous privilégions la qualité pédagogique (CLQ).
- **Absence de détection de confusion** : Nous identifions activement les blocages de l'élève pour les résoudre avant de poursuivre.

## 6. Scénarios d'Apprentissage Réels
Voici comment le système réagit dans des situations concrètes :

*   **Scénario A : L'élève qui approfondit**
*   **Scénario B : L'élève perdu**
*   **Scénario C : L'élève avancé**

## 7. Métriques CLQ (Qualité de l'Apprentissage)
Six métriques originales mesurent la qualité pédagogique : CRR, ESP, CCE, CUR, URR, CP.

---
*Pour plus de détails techniques, veuillez consulter le fichier README.md à la racine du projet.*
