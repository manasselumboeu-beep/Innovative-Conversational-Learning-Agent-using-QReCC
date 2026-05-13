# Question Classification

## Task
Classify the student's question and determine how to handle it.
Return ONLY a valid JSON object matching the schema below. No preamble, no markdown fences.

## Output Schema
```json
{
  "question_type": "self_contained" | "resolvable" | "confusion_indicating",
  "needs_rewrite": true | false,
  "needs_clarification": true | false,
  "rewritten_question": "<standalone rewrite if needs_rewrite is true, else null>",
  "clarification_prompt": "<clarification message if needs_clarification is true, else null>"
}
```

## Classification Guide

### self_contained
The question can be answered without any conversation context.
Example: "What is photosynthesis?"
needs_rewrite: false, needs_clarification: false

### resolvable
The question uses a pronoun, ellipsis, or implicit reference to prior context,
but can be resolved by inspecting the conversation history.
Example: "Tell me more about it." → "Tell me more about photosynthesis."
needs_rewrite: true — provide the rewritten standalone version.
needs_clarification: false

### confusion_indicating
The question suggests the student misunderstood the previous answer.
Example: After explaining that plants make food from sunlight: "So plants eat dirt?"
needs_rewrite: false, needs_clarification: false
(confusion is handled separately by Module 6)

## Critical Rules
1. needs_clarification and confusion_indicating CANNOT both be true.
2. If needs_rewrite is true, rewritten_question MUST be provided.
3. If needs_clarification is true, clarification_prompt MUST be provided.
4. clarification_prompt must offer exactly 2 options, drawn from the last 2 turns.
5. Prefer resolvable + rewrite over asking for clarification — only ask when truly ambiguous.

## Rewrite Quality Rules
- The rewritten question must be fully self-contained (no pronouns referring to context).
- Do not change the meaning — only resolve references.
- Keep the student's vocabulary and phrasing where possible.
