# AdaptiveTutor: A Conversational Learning System
### Complete Plan - Research Design + Deployable Prototype on Vercel

---

## Table of Contents

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

**Example turn:**

```json
{
  "Context": [
    "What are the pros and cons of electric cars?",
    "Some pros: easier on the environment, electricity is cheaper..."
  ],
  "Question": "Tell me more about Tesla",
  "Rewrite": "Tell me more about Tesla the car company.",
  "Answer": "Tesla Inc. is an American automotive and energy company...",
  "Answer_URL": "https://en.wikipedia.org/wiki/Tesla,_Inc."
}
```

The raw `Question` is ambiguous - "Tesla" could be the scientist. The `Rewrite` resolves this using context. This annotation is the training signal for context-dependent disambiguation.

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

### 2.5 Baseline Performance Gap

The original QReCC paper reports a baseline F1 of **19.10** against a human upper bound of **75.45**. This gap signals enormous room for improvement on factual retrieval alone. On the broader task of supporting learning, the gap is likely wider still.

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

**Why this fails for learning:** A tutor that does not model the learner cannot adapt. It gives the same explanation to a beginner and an expert.

### 3.4 Purely Reactive Systems

Existing systems wait for a question and produce an answer. They never ask for clarification when a question is vague, never check understanding after answering, and never detect when a follow-up suggests the previous answer missed the mark.

**Why this fails for learning:** Skilled teachers do all of these things. A purely reactive AI is a faster search engine, not a tutor.

### 3.5 No Confusion Signal

No existing QReCC-based system detects when a student is confused. Confusion produces recognisable linguistic patterns - repetition, vague reformulation, hedging - but these are never modelled. Undetected confusion compounds: a student who does not understand Turn 3 will ask increasingly confused questions through Turn 6, and the system will dutifully answer each one without addressing the root misunderstanding.

---

## 4. Two Foundational Design Principles

Every architectural decision follows from two principles.

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

All pedagogical knowledge - how to explain, how to respond to confusion, how to scaffold - lives in a directory of `SKILL.md` files in plain English. Python is the thin orchestrator that reads the right file and includes it in the LLM system prompt. When a teacher discovers a new pattern of student confusion, they edit a markdown file and the next conversation immediately benefits. No redeploy. No code change. No retraining.

---

## 5. Prototype Scope: What Is Built Now vs. Deferred

The full system has seven modules. The prototype implements four - the ones that demonstrate the most distinctive research contributions while remaining deployable on Vercel within its serverless timeout constraints.

### What Is Built in the Prototype

| Module | What It Does | Why It Is Included |
|---|---|---|
| **Module 1 (simplified)** | Lightweight conversation memory carried in the browser | Required for any multi-turn system; browser state avoids a database |
| **Module 2** | Three-way question classifier + proactive clarification | The most novel departure from standard QReCC approaches |
| **Module 3** | Adaptive explanation style via SKILL.md files | Demonstrates the skills directory principle; lightweight - just changes the system prompt |
| **Module 6** | Two-layer confusion detector | The strongest research contribution; rule layer is instant, LLM layer is one extra call |

### What Is Deferred to the Full System

| Deferred Component | Reason |
|---|---|
| Module 4 - Domain concept graph | Requires building a 200-node graph and prerequisite logic; too much for a prototype sprint |
| Module 5 - BM25 + cross-encoder retrieval | Indexing a 50K-passage corpus exceeds Vercel's function memory and cold-start tolerance |
| Module 7 - Dialogue coherence tracker | Depends on the concept graph; deferred with it |
| Full 4-tier fallback chain | Prototype uses single model + graceful error response |
| Prometheus observability | Console logging in prototype; full metrics in full system |
| Per-student trajectory monitoring | Requires persistent storage; deferred |

### What the Prototype Still Keeps from the Full Plan

- All Pydantic schemas (Vercel supports Python serverless functions)
- Logic gates (pure Python, zero latency overhead)
- Regex validators including the content safety blocklist
- The full skills directory structure committed to the repo
- The CLQ evaluation metrics, run offline against conversation logs

---

## 6. Prototype System Architecture

One complete turn in the prototype, from browser to Hugging Face and back:

```
┌─────────────────────────────────────────────────────────────────────┐
│  BROWSER (React / Next.js)                                          │
│  Holds session_state in useState:                                   │
│  { known_facts, confusion_count, current_style, turn_history }     │
│  Sends { question, session_state } on every turn                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  POST /api/turn
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VERCEL PYTHON API ROUTE  (/api/turn.py)                            │
│                                                                     │
│  Step 1 - Module 6: Confusion Detector (rule layer, no HF call)    │
│    Input:  question + turn_history                                  │
│    Output: ConfusionSignal (Pydantic-validated)                     │
│                                                                     │
│  Step 2 - Module 2: Question Classifier                             │
│    Input:  question + turn_history + confusion_signal               │
│    HF call #1: constrained JSON classification                      │
│    Output: QuestionClassification (Pydantic-validated)              │
│    Logic gates: validate classification consistency                 │
│                                                                     │
│  Step 3 - Module 3: Style Selector                                  │
│    Input:  session_state (confusion_count + turn_count)             │
│    Output: StyleSelection (Pydantic-validated)                      │
│    Logic gates: no expert after confusion; max one level rise       │
│    Reads:  appropriate SKILL.md from /skills/explanation/           │
│                                                                     │
│  Step 4 - Answer Generation                                         │
│    Input:  rewritten_question + SKILL.md content + known_facts      │
│            + confusion context if detected                          │
│    HF call #2: answer generation with SKILL.md system prompt       │
│    Layer 2: regex blocklist on output                               │
│    Layer 3: logic gates (no fact repetition, citation check)        │
│                                                                     │
│  Step 5 - Memory Update (optional)                                  │
│    HF call #3: only if answer passed validation                     │
│    Extract new facts → MemoryUpdate (Pydantic-validated)            │
│    Logic gates: max 5 new facts per turn; no duplicate facts        │
│                                                                     │
│  Returns: { answer, updated_session_state, debug_info }            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  HUGGING FACE INFERENCE API                                         │
│  Model: mistralai/Mistral-7B-Instruct-v0.3                         │
│  HF call #1: question classification                                │
│  HF call #2: answer generation (streamed)                          │
│  HF call #3: memory fact extraction (async, optional)              │
└─────────────────────────────────────────────────────────────────────┘
```

**Maximum 3 HF calls per turn.** In practice, most turns skip call #3 if no new concepts were introduced. Call #1 only fires if the rule layer in Module 6 is inconclusive.

---

## 7. Deployment Architecture: Vercel + Hugging Face

### 7.1 Why This Stack

| Concern | Solution |
|---|---|
| No GPU required | Hugging Face Inference API runs the model on their infrastructure |
| No server to manage | Vercel serverless functions, scale to zero when idle |
| Public URL, no auth | Anyone with the link can use the demo |
| No database | Session state lives in the browser, sent with each request |
| No cold-start penalty on skills | SKILL.md files committed to the repo, read from disk |
| Python for Pydantic and logic gates | Vercel's Python runtime supports `.py` files in the `api/` directory |

### 7.2 Latency Reality and Mitigations

The Hugging Face free Inference API queues requests and can take 10–30 seconds per call under load. Three calls per turn could push against Vercel's 60-second Pro function timeout in the worst case.

**Mitigation strategies:**

**Stream the answer.** HF supports token streaming. The student sees text appearing within 2–3 seconds rather than waiting for the full response. This is the highest-impact latency fix.

**Rule layer first.** The confusion detector's rule layer (Module 6, Step 1) runs in pure Python with zero network cost. It eliminates the LLM classification call entirely for the most common patterns. Most turns never fire HF call #1.

**Memory extraction is async.** HF call #3 is the least time-sensitive. It can be fired asynchronously after the answer is returned to the browser and its result applied on the next turn.

**Upgrade path.** For a demo where latency matters, a dedicated Hugging Face Inference Endpoint costs approximately $0.06/hour and eliminates queue wait entirely.

### 7.3 Session State in the Browser

Vercel functions are stateless. The episodic memory is carried in the browser and sent with each POST request as a JSON body:

```json
{
  "question": "What does ATP actually do?",
  "session_state": {
    "known_facts": [
      { "id": "photosynthesis_overview", "turn": 2, "confidence": 0.9 }
    ],
    "confusion_count_last_5": 1,
    "current_style": "foundation",
    "turn_history": [
      { "question": "How does photosynthesis work?", "answer": "...",
        "had_comprehension_check": false },
      { "question": "And what about respiration?", "answer": "...",
        "had_comprehension_check": false }
    ]
  }
}
```

The API route validates the incoming `session_state` against the `LearnerState` Pydantic schema on every request, updates it, and returns the updated object. The browser stores it in `useState` and sends it with the next turn.

---

## 8. Skills Directory: Where Pedagogical Knowledge Lives

All pedagogical knowledge lives in a directory of markdown files committed to the repo. Vercel includes them in the deployment bundle. The Python API route reads the relevant file at request time and injects its content into the LLM system prompt.

### 8.1 Directory Structure (Prototype)

```
/skills
  /INDEX.md                              ← Read at startup; global rules
  /explanation
    /foundation/SKILL.md                 ← Beginner-level explanation style
    /standard/SKILL.md                   ← Intermediate explanation style
    /expert/SKILL.md                     ← Advanced explanation style
  /interaction
    /handle_confusion/SKILL.md           ← How to respond when confusion is detected
    /clarification_request/SKILL.md      ← How to ask for clarification
    /comprehension_check/SKILL.md        ← When and how to inject check-in questions
    /scaffolding/SKILL.md                ← How to decompose a complex answer
  /domain/science
    /biology/SKILL.md                    ← Biology-specific explanation patterns
    /physics/SKILL.md                    ← Physics-specific explanation patterns
    /common_misconceptions/SKILL.md      ← Known misconceptions and how to address them
  /meta
    /memory_extraction/SKILL.md          ← How to extract facts from a completed answer
    /confusion_classification/SKILL.md   ← How to classify a confusion signal
    /question_classification/SKILL.md    ← How to classify question type
```

### 8.2 What Each SKILL.md Contains

```markdown
# Foundation Explanation Style

## When to Use
- Student's confusion_count_last_5 is greater than 0
- Student's proficiency estimate is below 0.4
- Student explicitly asked for a simpler explanation

## Process
1. Acknowledge what the student already knows from prior turns
2. Introduce ONE new concept only
3. Use a concrete everyday analogy
4. Keep sentences under 15 words
5. End with a check-in question

## Quality Checklist
- [ ] No more than 3 sentences per idea
- [ ] No technical jargon without an inline definition
- [ ] At least one concrete example
- [ ] Ends with an invitation for the student to respond

## Anti-Patterns
- Do not list multiple concepts in parallel
- Do not use "actually" or "in fact" (reads as condescending)
- Do not assume prerequisite knowledge not yet confirmed
```

### 8.3 The Compounding Flywheel

When a teacher using the demo notices students keep confusing osmosis with diffusion, they add an entry to `/skills/domain/science/biology/SKILL.md`. The change is a commit. The next Vercel deployment picks it up. No code change. No model retraining. Knowledge accumulates in human-readable files rather than disappearing into Python strings.

---

## 9. Defense-in-Depth: Adapted for the Prototype

The full five-layer system is preserved in the prototype with one adaptation: Layer 0 uses prompt-level JSON constraints rather than grammar-based sampling, because the Hugging Face Inference API does not expose token-level decoding control.

### 9.1 Layer 0 - Prompt-Level JSON Constraints

Structured outputs are enforced via explicit system prompt instructions:

- System prompt: *"Respond ONLY with a JSON object matching this exact schema. No preamble, no explanation, no markdown fences."*
- The expected schema is shown as a typed example in the prompt
- The response is extracted and fed to the Pydantic validator before any further processing

This is weaker than true constrained decoding (which mathematically prevents invalid tokens) but catches the large majority of structural failures. Layer 1 provides the real safety net.

### 9.2 Layer 1 - Pydantic Schemas

All structured outputs are typed Pydantic models:

```
ConfusionSignal        - confused: bool, type: Literal[5 options], trigger_turn: int
QuestionClassification - question_type: Literal[3 options], needs_rewrite: bool
MemoryUpdate           - new_facts: list[Fact] max 5, concept_id: str pattern-validated
StyleSelection         - style: Literal[3 options], reason: Literal[4 options]
LearnerState           - proficiency_estimate: float [0,1], confusion_count: int [0,5]
TutorResponse          - answer_text: str, cited_facts: list, has_comprehension_check: bool
```

### 9.3 Layer 2 - Regex Validators

All patterns live in `validators/regex_patterns.py`, version-controlled:

**Allowlist** (field values must match):
- Citation URLs restricted to: `wikipedia.org`, `khanacademy.org`, `britannica.com`
- Concept IDs: `^[a-z][a-z_]{2,40}$`

**Blocklist** (any match rejects the response and routes to fallback):
- HTML/JS injection: `<script`, `javascript:`, `onerror=`, `data:text/html`
- Prompt injection: `ignore previous instructions`, `system:`, `you are now`
- Inappropriate content patterns (curated, version-controlled list)
- Personal information in generated text: email and phone patterns

### 9.4 Layer 3 - Logic Gates

Pure Python in the Vercel function, zero LLM cost:

- Proficiency estimate cannot change by more than 0.2 per turn
- Expert style is blocked when `confusion_count_last_5 > 0`
- Style cannot rise more than one level per turn
- A fact ID cannot appear in `TutorResponse.cited_facts` if it is already in `known_facts`
- Comprehension check: at most one per three-turn window
- `ConfusionSignal.trigger_turn` must be a valid index in `turn_history`
- `confusion_indicating` classification and `needs_clarification` cannot both be true

### 9.5 Retry Policy

- HF API network timeout or rate limit (429): retry up to 2 times with 2-second backoff
- `ValidationError` or logic gate violation: no retry - route immediately to fallback
- One-shot temperature bump (0.0 → 0.3) allowed on a generation retry, once per turn only

---

## 10. Module 1 - Lightweight Browser-State Memory

**Research question:** Can a simplified version of structured episodic memory, carried entirely in browser state with no server-side persistence, provide enough context to meaningfully improve multi-turn conversations over flat history concatenation?

### 10.1 What Is Stored

The prototype keeps a focused subset of episodic memory in browser `useState`:

```json
{
  "known_facts": [
    { "id": "photosynthesis_overview", "turn": 2, "confidence": 0.9 },
    { "id": "chlorophyll_role", "turn": 3, "confidence": 0.8 }
  ],
  "confusion_count_last_5": 1,
  "current_style": "foundation",
  "turn_history": [
    {
      "question": "How does photosynthesis work?",
      "rewritten": "How does photosynthesis work?",
      "answer": "Photosynthesis is the process by which...",
      "had_comprehension_check": false
    }
  ]
}
```

The full episodic memory in the complete system also tracks `misconceptions`, `explored_topics`, and `open_questions`. The prototype uses `confusion_count_last_5` and `turn_history` as proxies for these.

### 10.2 How It Is Used

- `known_facts` is passed to the generation prompt to prevent re-explaining already-received concepts (guards the Unnecessary Repetition Rate metric)
- `confusion_count_last_5` drives style selection in Module 3
- `turn_history` is the context window for confusion detection and question classification
- `current_style` is carried forward as the prior state for logic gate checks

### 10.3 Memory Update After Each Turn

After a successful answer, HF call #3 extracts new facts using `memory_extraction/SKILL.md` as the system prompt. Output is a `MemoryUpdate` object (schema-validated). Logic gates check for duplicate IDs and cap new facts per turn at 5. The updated `session_state` is returned to the browser.

---

## 11. Module 2 - Proactive Question Clarity Engine

**Research question:** Instead of always rewriting a question silently, can the tutor decide when to ask for clarification, when to silently rewrite, and when the question reveals a deeper misunderstanding that should be addressed before answering?

### 11.1 Three-Way Classification

Every question is classified into one of three regimes via a schema-constrained HF call:

| Class | Description | Action |
|---|---|---|
| `self_contained` | No context needed to answer | Pass directly to generation |
| `resolvable` | Ambiguous but resolvable from conversation history | Silent rewrite, then generate |
| `confusion_indicating` | Suggests the student misunderstood the previous answer | Load `handle_confusion/SKILL.md`, re-address prior concept first |

**Training signal from QReCC:** Where `Question == Rewrite`, the question is `self_contained`. Where they differ, it is `resolvable`. The ROUGE-L delta between the two provides the boundary signal for the classifier.

### 11.2 Clarification Request Generation

When a question cannot be resolved even from context, the tutor generates a targeted clarification using `clarification_request/SKILL.md`. The options offered are drawn from the last two turns in `turn_history`, not invented by the model:

> *"I want to make sure I help with the right thing. Are you asking about [topic from turn N-1] or [topic from turn N-2]?"*

### 11.3 Logic Gates on Classification

- If `confusion_indicating`, `trigger_turn` must be a valid index in `turn_history`
- `needs_clarification` and `confusion_indicating` cannot both be true
- A `self_contained` classification on a question beginning with "it", "that", "they", or "this" is downgraded to `resolvable`

---

## 12. Module 3 - Adaptive Teaching Behaviour

**Research question:** Can the tutor infer a student's current comprehension level from conversational signals alone, and adapt its explanation style accordingly without any fine-tuning?

### 12.1 Proficiency Estimation

No labels exist in QReCC for proficiency. Proxy signals derived from browser state:

| Signal | Implication |
|---|---|
| `confusion_count_last_5 > 0` | Low current comprehension |
| `confusion_count_last_5 == 0` for 3+ turns | Comprehension stable or recovering |
| Question vocabulary complexity (readability score, computed in Python) | Higher score → higher proficiency |
| Turn 1 or 2 of a new session | Default to `standard`; insufficient data |

These signals produce a `proficiency_estimate ∈ [0.0, 1.0]`, computed deterministically in Python - no LLM call.

### 12.2 Style Selection and SKILL.md Injection

Style is selected as a `StyleSelection` Pydantic object. Logic gates enforce the constraints. The corresponding SKILL.md file is read from disk and injected into the system prompt for answer generation:

| Style | Condition | SKILL.md Loaded |
|---|---|---|
| `foundation` | `proficiency_estimate < 0.4` or `confusion_count_last_5 > 0` | `/skills/explanation/foundation/SKILL.md` |
| `standard` | `0.4 ≤ proficiency_estimate ≤ 0.75`, no recent confusion | `/skills/explanation/standard/SKILL.md` |
| `expert` | `proficiency_estimate > 0.75` and `confusion_count_last_5 == 0` | `/skills/explanation/expert/SKILL.md` |

When confusion is detected by Module 6, `handle_confusion/SKILL.md` is prepended to the system prompt regardless of style level.

### 12.3 Comprehension Check Injection

After every third turn with `confusion_count_last_5 == 0`, the `comprehension_check/SKILL.md` is appended to the system prompt. The logic gate checks: no comprehension check if one was delivered in the last three turns (tracked in `turn_history[].had_comprehension_check`).

---

## 13. Module 6 - Confusion and Misunderstanding Detector

**Research question:** Can we detect when a student's follow-up question signals that the previous answer was not understood, classify what kind of confusion it represents, and respond differently before answering the new question?

### 13.1 Confusion Taxonomy

| Type | Description | Example signal |
|---|---|---|
| `repetition` | Student asks essentially the same question again | ROUGE-L > 0.7 vs. a prior question |
| `vague` | Student re-asks with vaguer terms | "What do you mean?", "Can you explain again?" |
| `contradiction` | Student asserts something inconsistent with a prior answer | "But you said...", "But isn't it..." |
| `scope` | Sudden drilling into a specific sub-question after a broad answer | Suggests prior answer was too abstract |
| `none` | No confusion signal | Normal follow-up |

### 13.2 Two-Layer Detection

**Layer 1 - Deterministic rules (no HF call, runs instantly):**

- ROUGE-L between current question and each question in `turn_history` - threshold 0.7 detects `repetition`
- Keyword match: `["again", "mean", "don't understand", "confused", "explain again", "what do you mean"]` → `vague`
- Pattern `"but you said|but didn't you|you told me"` → `contradiction`

If the rule layer produces a result, no HF call is made. Most turns are `none`, meaning the common case costs zero extra tokens.

**Layer 2 - Constrained LLM classification (only when rules are inconclusive):**

A schema-constrained HF call with `confusion_classification/SKILL.md` as the system prompt, returning a `ConfusionSignal` object. Logic gates then validate that `trigger_turn` is a real index and `evidence_phrase` is a substring of the actual conversation text - the model cannot hallucinate evidence.

### 13.3 Response to Detected Confusion

When confusion is detected:
1. The current question is not answered immediately
2. `handle_confusion/SKILL.md` is loaded and prepended to the system prompt
3. Style drops one level (logic gate enforces this)
4. `confusion_count_last_5` is incremented in session state
5. The tutor addresses the prior concept with an alternative approach, then returns to the student's new question

---

## 14. Prototype Fallback Strategy

The full system has a four-tier fallback chain. The prototype simplifies to two tiers.

```
Tier 1: Hugging Face Inference API (primary)
        Full pipeline: Modules 1, 2, 3, 6 - all validation layers
        │
        ├── Network timeout → retry up to 2× with 2s backoff
        ├── Pydantic ValidationError → no retry, go to Tier 2
        └── Logic gate violation → no retry, go to Tier 2

Tier 2: Graceful static response
        A fixed, pre-written response:
        "That's a thoughtful question - let me make sure I give you
         the clearest answer I can. Could you tell me a bit more about
         which part feels unclear? That will help me explain it better."
        Passes all regex validators (it is static text, not model output).
        Failed turn is logged to console with full context for debugging.
```

The key rule applies even at prototype scale: a fallback that can produce invalid output is not a fallback. The static response still runs through the regex blocklist before being returned. It always passes - but the check always runs.

---

## 15. Evaluation Framework

### 15.1 Standard QReCC Metrics

Retained for research credibility and comparison with prior work:

- **F1** and **Exact Match** on Answer vs. gold Answer
- **ROUGE-L** on rewrites vs. gold Rewrite

Computed offline by replaying QReCC test conversations through the prototype API.

### 15.2 Conversational Learning Quality (CLQ) Metrics

Six novel metrics measuring pedagogical quality, computed from exported conversation logs:

| Metric | Abbreviation | Definition |
|---|---|---|
| **Confusion Resolution Rate** | CRR | Fraction of detected confusion signals not re-detected within 2 turns |
| **Explanation Style Precision** | ESP | Fraction of turns where selected style matches `proficiency_estimate` |
| **Comprehension Check Engagement** | CCE | Fraction of comprehension checks that receive responses over 15 words |
| **Context Utilisation Rate** | CUR | Fraction of `known_facts` referenced in subsequent answers |
| **Unnecessary Repetition Rate** | URR | Fraction of answers re-explaining content already in `known_facts` |
| **Clarification Precision** | CP | Fraction of clarification requests followed by a clearer student question |

### 15.3 Human Evaluation Protocol

For 50 sampled conversations from public demo usage:

1. **Clarity (1–5):** Was the explanation clear at the student's apparent level?
2. **Responsiveness (1–5):** Did the tutor respond correctly to signs of confusion?
3. **Naturalness (1–5):** Did the conversation feel natural, not robotic?
4. **Usefulness (1–5):** Did the student appear to learn something from the exchange?

Human scores validate the automated CLQ metrics via Pearson correlation (CRR vs. Responsiveness, ESP vs. Clarity).

### 15.4 Ablation Studies

| Ablation | What Is Removed | Metric Affected |
|---|---|---|
| No Module 6 | Confusion always treated as `none` | CRR drops; style never adapts to confusion |
| No Module 2 | All questions passed raw to generation | ROUGE-L drops; URR may increase |
| Fixed style | `standard` on every turn | ESP becomes 0; CRR likely drops |
| SKILL.md vs hard-coded prompts | Markdown replaced with Python strings | Same metric scores; update agility test measures time to fix a known failure |

---

## 16. Project Structure

```
adaptive-tutor/
│
├── skills/                                ← All pedagogical knowledge (static, in repo)
│   ├── INDEX.md
│   ├── explanation/
│   │   ├── foundation/SKILL.md
│   │   ├── standard/SKILL.md
│   │   └── expert/SKILL.md
│   ├── interaction/
│   │   ├── handle_confusion/SKILL.md
│   │   ├── clarification_request/SKILL.md
│   │   ├── comprehension_check/SKILL.md
│   │   └── scaffolding/SKILL.md
│   ├── domain/science/
│   │   ├── biology/SKILL.md
│   │   ├── physics/SKILL.md
│   │   └── common_misconceptions/SKILL.md
│   └── meta/
│       ├── memory_extraction/SKILL.md
│       ├── confusion_classification/SKILL.md
│       └── question_classification/SKILL.md
│
├── api/                                   ← Vercel Python serverless functions
│   └── turn.py                            # Main handler: all modules + validation
│
├── validators/                            ← Pure Python, zero dependencies
│   ├── regex_patterns.py                  # Allowlists + blocklists (version-controlled)
│   └── logic_gates.py                     # Pedagogical business rules
│
├── schemas/                               ← Pydantic models
│   ├── confusion.py                       # ConfusionSignal
│   ├── classification.py                  # QuestionClassification
│   ├── memory.py                          # MemoryUpdate, Fact, LearnerState
│   ├── style.py                           # StyleSelection
│   └── response.py                        # TutorResponse
│
├── modules/                               ← Module logic (called by api/turn.py)
│   ├── confusion_detector.py              # Module 6: rule layer + LLM classification
│   ├── clarity_engine.py                  # Module 2: three-way classifier + rewriter
│   ├── adaptive_teacher.py                # Module 3: proficiency estimation + SKILL.md
│   ├── memory_manager.py                  # Module 1: memory update + dedup
│   └── skill_loader.py                    # Reads SKILL.md files from /skills/
│
├── src/                                   ← Next.js frontend (TypeScript)
│   ├── app/
│   │   ├── page.tsx                       # Main chat page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ChatWindow.tsx                 # Message list
│   │   ├── MessageInput.tsx               # Input box + send
│   │   ├── StyleIndicator.tsx             # Shows current style (foundation/standard/expert)
│   │   ├── ConfusionBadge.tsx             # Debug overlay: confusion type detected
│   │   └── MemoryPanel.tsx                # Collapsible panel: known_facts (research demo)
│   └── hooks/
│       └── useSession.ts                  # useState wrapper for session_state
│
├── data/
│   ├── load_qrecc.py                      # Download and parse QReCC
│   └── analyse_dataset.py                 # EDA helper
│
├── evaluation/
│   ├── standard_metrics.py                # F1, EM, ROUGE-L
│   └── clq_metrics.py                     # CRR, ESP, CCE, CUR, URR, CP
│
├── experiments/
│   ├── ablation_confusion.py
│   ├── ablation_clarity.py
│   ├── ablation_style.py
│   └── ablation_skills_vs_prompts.py
│
├── tests/
│   ├── test_schemas.py
│   ├── test_logic_gates.py
│   ├── test_regex_validators.py
│   └── test_modules.py
│
├── notebooks/
│   ├── 01_dataset_eda.ipynb
│   ├── 02_confusion_signal_analysis.ipynb
│   └── 03_results_analysis.ipynb
│
├── vercel.json                            # Python runtime config + function timeout
├── requirements.txt                       # pydantic, rouge-score, requests
├── package.json                           # Next.js dependencies
└── README.md
```

---

## 17. Technology Stack

### Prototype Stack

| Component | Choice | Rationale |
|---|---|---|
| Frontend | Next.js 14 (App Router, TypeScript) | Vercel-native, React, token streaming support |
| Deployment | Vercel | Zero config, free tier, instant public URL |
| LLM inference | Hugging Face Inference API | No GPU; no server management |
| Primary model | `mistralai/Mistral-7B-Instruct-v0.3` | Best balance of quality and HF free-tier availability |
| Fallback model | `HuggingFaceH4/zephyr-7b-beta` | Often faster on HF; strong instruction-following |
| Lightweight option | `microsoft/Phi-3-mini-4k-instruct` | Fastest; lower quality on complex reasoning |
| API runtime | Vercel Python serverless (`api/turn.py`) | Python for Pydantic and logic gates without a separate server |
| Schema enforcement | `pydantic` v2 | Typed outputs, `Literal` constraints |
| Regex validation | Python `re` (stdlib) | No dependencies |
| Session state | React `useState` + request body | No database, no server state |
| Skill loader | Custom Python reading markdown | No framework needed |
| ROUGE-L | `rouge-score` Python package | Classifier training signal from QReCC rewrites |
| Evaluation | `evaluate` (HuggingFace), `rouge-score` | Standard and CLQ metrics |
| Experiment tracking | `mlflow` (local) | Run comparison for ablations |
| Testing | `pytest` | Schema and module unit tests |

### HF Model Selection Guide

| Model | When to Use |
|---|---|
| `Mistral-7B-Instruct-v0.3` | Default; best overall quality on HF free tier |
| `zephyr-7b-beta` | If Mistral queue is long; comparable quality |
| `Phi-3-mini-4k-instruct` | If speed is the priority over answer quality |

### Full System Additions (deferred - Section 19)

`rank_bm25`, `sentence-transformers`, `llama-cpp-python` or `vllm`, `outlines` (true constrained decoding), `prometheus_client`, concept graph JSON.

---

## 18. Milestone Roadmap

 use your  frontend skills here if needed


- [ ] Scaffold Next.js project; deploy "hello world" to Vercel; verify public URL
- [ ] Create `api/turn.py` as a Vercel Python function; confirm Python runtime works end-to-end
- [ ] Define all Pydantic schemas in `schemas/`
- [ ] Write `validators/regex_patterns.py` (allowlists + blocklists)
- [ ] Write `validators/logic_gates.py` (all pedagogical rules - sit with a teacher to derive them)
- [ ] Write all SKILL.md files (populate the full `/skills/` directory)
- [ ] Write `modules/skill_loader.py`
- [ ] Write tests for all schemas, all gates, and all regex patterns


- [ ] Implement `confusion_detector.py` (Module 6): rule layer first, HF call second, both validated
- [ ] Implement `clarity_engine.py` (Module 2): three-way classifier + rewrite path + clarification path
- [ ] Implement `adaptive_teacher.py` (Module 3): proficiency estimation + SKILL.md injection
- [ ] Implement `memory_manager.py` (Module 1): MemoryUpdate extraction + known_facts dedup
- [ ] Wire all modules into `api/turn.py` with correct step ordering
- [ ] Test with hand-crafted conversation inputs; verify each validation layer fires correctly


- [ ] Build `ChatWindow.tsx` with token streaming display
- [ ] Build `useSession.ts` managing `session_state` in browser state
- [ ] Build `StyleIndicator.tsx` (visible teaching style - key for research demo)
- [ ] Build `ConfusionBadge.tsx` and collapsible `MemoryPanel.tsx`
- [ ] Connect frontend to `api/turn.py`; test end-to-end in browser
- [ ] Handle loading state, error state, and Tier 2 fallback gracefully in UI



- [ ] Load QReCC test set; replay conversations through the API; export logs
- [ ] Compute F1, EM, ROUGE-L against QReCC gold answers
- [ ] Implement and compute all six CLQ metrics against logs
- [ ] Run four ablation experiments; record metric deltas
- [ ] Human evaluation on 50 conversations from the live demo
- [ ] Validate CLQ metrics against human scores (Pearson correlation)
- [ ] Document results in `03_results_analysis.ipynb`

---

## 19. Full System: What Gets Built Next

The prototype proves the research ideas with a live, public URL. The full system extends it with the components deferred from the prototype sprint:

**Module 4 - Domain Concept Graph:** A 200-node JSON graph of high school science concepts with prerequisite edges. Enables prerequisite gap detection, automatic teaching detours, and coherence scoring.

**Module 5 - BM25 + Cross-Encoder Retrieval:** Replaces reliance on the model's parametric knowledge with grounded retrieval from a curated 50K-passage science Wikipedia corpus. `rank_bm25` for sparse retrieval + `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking. Deployed on a persistent server (Render or Railway free tier) since corpus indexing exceeds Vercel function memory.

**Module 7 - Dialogue Coherence Tracker:** Topic arc coherence scoring (pure Python on the concept graph). Automatic bridging statements on topic jumps. Depends on Module 4.

**True Constrained Decoding (Layer 0):** When running local inference via `llama-cpp-python` or `vllm`, `outlines` or `llama.cpp` GBNF enforces JSON schema at the token level. The model physically cannot produce invalid output.

**Full Fallback Chain:** Tier 1 (local Phi-3-mini or Mistral) → Tier 2 (HF Inference API) → Tier 3 (rule-based template responder) → Tier 4 (human-flagged graceful response with queue entry).

**Production Observability:** `prometheus_client` counters per tier and per module. Alert thresholds configured. Per-student trajectory plots. Failed turn logging with full context for teacher review.

---

## 20. Summary of Novel Contributions

### Research Innovations

| # | Research Direction | Novel Strategy |
|---|---|---|
| 1 | Context modelling | Structured episodic memory replacing flat history concatenation (browser-state in prototype; persistent object in full system) |
| 2 | Question clarity | Three-way classifier enabling proactive clarification - not just silent rewriting |
| 3 | Adaptive teaching | Proficiency-estimated style switching via SKILL.md injection; no fine-tuning required |
| 4 | Domain tutor | Concept-graph-aware prerequisite detection with teaching detours (full system) |
| 5 | Multi-technique pipeline | BM25 + cross-encoder + memory-enriched generation + CoT (full system) |
| 6 | Confusion detection | Two-layer detector: deterministic rules first (zero cost), constrained LLM second |
| 7 | Evaluation | Six-metric CLQ framework validated against human ratings |
| 8 | Coherence | Topic arc scorer with automatic bridging (full system) |
| 9 | Deployability | Research prototype behind a public URL; accessible to anyone without setup |

### Production Principles Applied

| Principle | Prototype Application |
|---|---|
| Constrain output at generation time | Prompt-level JSON constraints; `outlines` GBNF in full system |
| Schema enforcement | Pydantic v2 `Literal` types on all structured outputs |
| Regex for semantics and security | URL allowlist; HTML/JS/injection blocklist; inappropriate content blocklist |
| Logic gates | 10+ pedagogical rules: style jumps, fact repetition, confusion consistency, check throttling |
| Deterministic fallback | HF API → graceful static response; no Python exception reaches the student |
| Retry transient errors only | Network timeouts retry; validation failures advance immediately |
| Skills directories over code | All pedagogical knowledge in `/skills/` markdown; Python is thin orchestration |
| Grow skills from use | Failure patterns from demo usage become new SKILL.md entries |
| Human fallback | Graceful static response with console logging (full queue entry in full system) |

---

*Prototype: Next.js + Vercel Python functions + Hugging Face Inference API.*
*No GPU. No database. No server to manage. Public URL from day one.*

*Full system: Extends prototype with local inference, BM25 retrieval, concept graph, four-tier fallback, and production observability.*