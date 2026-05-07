# 🎓 Project Report: AdaptiveTutor - A Conversational Learning System

## 1. Project Overview
**AdaptiveTutor** is an innovative conversational learning agent built on the QReCC dataset. It is designed to detect student confusion, adapt explanation styles in real-time, and improve dialogue quality beyond simple answer correctness. Unlike standard QA systems, AdaptiveTutor behaves like a proactive teacher, not just a search engine.

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

## 6. System Architecture
The system operates as a 5-step pipeline:
1. **Confusion Detection**: Rule-based (ROUGE-L) and LLM-based detection of student misunderstanding.
2. **Question Classification**: Deciding if a question is clear, needs rewriting, or indicates confusion.
3. **Style Selection**: Estimating proficiency and selecting the appropriate `SKILL.md` (Foundation, Standard, Expert).
4. **Answer Generation**: Streaming responses using the selected pedagogical style.
5. **Memory Update**: Extracting new facts to update the learner's persistent state.

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

## 3. Analyse du Dataset QReCC et Stratégies Innovantes
Le projet utilise le dataset QReCC de trois manières concrètes :
- **Rewriting** : Les annotations humaines servent de signal pour notre moteur de clarté.
- **Structure de Conversation** : Les échanges multi-tours informent la conception de notre mémoire de session.
- **Évaluation** : Utilisation du jeu de tests pour calculer nos six nouvelles métriques **CLQ** (Conversational Learning Quality).

Les stratégies innovantes proposées (mémoire structurée, détection de confusion à deux couches, styles pédagogiques injectés) visent à transformer une expérience de recherche d'information en une véritable expérience d'apprentissage tutoré.

## 4. Limitations des Approches Existantes
Le système répond aux lacunes des modèles actuels :
- **Contexte limité à la désambiguïsation** : Nous l'utilisons pour modéliser l'apprenant.
- **Biais vers la métrique F1** : Nous privilégions la qualité pédagogique (CLQ).
- **Absence de détection de confusion** : Nous identifions activement les blocages de l'élève pour les résoudre avant de poursuivre.

## 5. Scénarios d'Apprentissage Réels
Voici comment le système réagit dans des situations concrètes :

*   **Scénario A : L'élève qui approfondit**
    *   *Comportement* : Pose une question courte comme "Et pour l'énergie ?".
    *   *Réponse IA* : Identifie une question **résolvable**, la reformule en contexte et maintient un flux fluide sans redemander le sujet.
*   **Scénario B : L'élève perdu**
    *   *Comportement* : Répète sa question ou exprime son incompréhension.
    *   *Réponse IA* : Détecte la **confusion**, bascule en style **Fondation** et utilise une analogie simplifiée au lieu d'une définition technique.
*   **Scénario C : L'élève avancé**
    *   *Comportement* : Démontre une compréhension rapide sur plusieurs échanges.
    *   *Réponse IA* : Augmente l'estimation de maîtrise et passe en style **Expert**, offrant des détails plus techniques et des références scientifiques.

## 6. Métriques CLQ (Qualité de l'Apprentissage)
Six métriques originales mesurent la qualité pédagogique :
1. **CRR** : Taux de résolution de la confusion.
2. **ESP** : Précision du style d'explication.
3. **CCE** : Engagement lors des vérifications de compréhension.
4. **CUR** : Taux d'utilisation du contexte.
5. **URR** : Taux de répétition inutile.
6. **CP** : Précision des demandes de clarification.

---
*Pour plus de détails techniques, veuillez consulter le fichier README.md à la racine du projet.*
