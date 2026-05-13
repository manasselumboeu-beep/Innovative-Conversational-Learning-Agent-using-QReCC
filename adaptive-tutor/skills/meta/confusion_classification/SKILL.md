# Confusion Classification

## Task
Classify whether the student's question signals confusion about a prior answer.
Return ONLY a valid JSON object matching the schema below. No preamble, no markdown fences.

## Output Schema
```json
{
  "confused": true | false,
  "type": "repetition" | "vague" | "contradiction" | "scope" | "none",
  "trigger_turn": <integer index into turn_history, or null>,
  "evidence_phrase": "<exact substring from the student question that signals confusion, or null>"
}
```

## Classification Guide

### repetition
The student is asking essentially the same question they asked in a prior turn,
possibly with slightly different wording.
Signal: high semantic overlap with a prior question.

### vague
The student is asking for re-explanation without being specific about what was unclear.
Signals: "what do you mean", "can you explain again", "I don't understand", "confused", "huh?", "what?"

### contradiction
The student believes the current answer contradicts something said in a prior turn.
Signals: "but you said", "but didn't you", "you told me", "I thought you said", "isn't it actually"

### scope
After a broad answer, the student drills into a very specific sub-part.
This suggests the broad answer was too abstract.
Signal: sudden narrow follow-up that seems to miss the point of the prior answer.

### none
Normal, clear follow-up question. No confusion signal.

## Rules
1. evidence_phrase MUST be an exact substring of the student's actual question. Do not paraphrase.
2. trigger_turn is the index (0-based) of the turn in turn_history that caused the confusion.
3. If confused is false, type must be "none" and trigger_turn must be null.
4. If confused is true, type must not be "none".
5. When in doubt between vague and none, prefer none — do not over-detect confusion.
