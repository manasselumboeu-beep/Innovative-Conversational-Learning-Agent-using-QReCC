export interface Fact {
  id: string;
  turn: number;
  confidence: number;
  summary?: string;
}

export interface TurnRecord {
  question: string;
  rewritten: string;
  answer: string;
  had_comprehension_check: boolean;
  confusion_type: string;
}

export interface SessionState {
  known_facts: Fact[];
  confusion_count_last_5: number;
  current_style: "foundation" | "standard" | "expert";
  turn_history: TurnRecord[];
  proficiency_estimate: number;
}

export interface Message {
  id: string;
  role: "student" | "tutor";
  content: string;
  isStreaming?: boolean;
  confusionType?: string;
  styleUsed?: string;
  classificationResult?: string;
}

export interface TurnMeta {
  confusion: { confused: boolean; type: string };
  classification: { type: string; rewritten?: string };
  style: { style: string; reason: string };
}

export const INITIAL_SESSION: SessionState = {
  known_facts: [],
  confusion_count_last_5: 0,
  current_style: "standard",
  turn_history: [],
  proficiency_estimate: 0.5,
};
