# Memory Extraction — Fact Extraction from Completed Answers

## Task
Extract new factual concepts introduced in the tutor's answer that the student has now been exposed to.
Return ONLY a valid JSON object matching the schema below. No preamble, no markdown fences.

## Output Schema
```json
{
  "new_facts": [
    {
      "id": "concept_id_in_snake_case",
      "turn": <turn_number_as_integer>,
      "confidence": <float_between_0_and_1>,
      "summary": "One sentence: what the student was told about this concept."
    }
  ]
}
```

## Rules for Fact Extraction
1. Only extract concepts that were substantively explained — not just mentioned in passing.
2. The id must match ^[a-z][a-z_]{2,40}$ — snake_case, 3–41 characters.
3. confidence:
   - 0.9: Core claim made with clear explanation and example.
   - 0.7: Concept introduced but not deeply explained.
   - 0.5: Briefly mentioned; student may not have absorbed it.
4. Do not extract meta-statements ("the tutor explained that...") — extract the fact itself.
5. Maximum 5 facts per turn. Prioritise the most important ones.
6. Do not extract facts already present in known_facts (provided in the prompt context).

## Example
Given answer: "Photosynthesis is how plants make food from sunlight. Chlorophyll is the green
pigment that captures light energy. Plants need CO2 and water as inputs."

Output:
```json
{
  "new_facts": [
    {"id": "photosynthesis_overview", "turn": 3, "confidence": 0.9,
     "summary": "Photosynthesis is the process by which plants produce food using sunlight."},
    {"id": "chlorophyll_role", "turn": 3, "confidence": 0.8,
     "summary": "Chlorophyll is the green pigment in plants that captures light energy."},
    {"id": "photosynthesis_inputs", "turn": 3, "confidence": 0.7,
     "summary": "Photosynthesis requires CO2 and water as inputs."}
  ]
}
```
