"use client";

import { useState, useCallback, useRef } from "react";
import {
  SessionState,
  Message,
  TurnMeta,
  INITIAL_SESSION,
} from "@/types/session";

function parseSSE(chunk: string): Array<{ event: string; data: string }> {
  const events: Array<{ event: string; data: string }> = [];
  const blocks = chunk.split("\n\n");
  for (const block of blocks) {
    const lines = block.split("\n");
    let event = "message";
    let data = "";
    for (const line of lines) {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      else if (line.startsWith("data:")) data = line.slice(5).trim();
    }
    if (data) events.push({ event, data });
  }
  return events;
}

export function useSession() {
  const [sessionState, setSessionState] = useState<SessionState>(INITIAL_SESSION);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [turnMeta, setTurnMeta] = useState<TurnMeta | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim() || isLoading) return;

      abortRef.current?.abort();
      abortRef.current = new AbortController();

      const studentMsg: Message = {
        id: crypto.randomUUID(),
        role: "student",
        content: question,
      };

      const tutorMsgId = crypto.randomUUID();
      const tutorMsg: Message = {
        id: tutorMsgId,
        role: "tutor",
        content: "",
        isStreaming: true,
      };

      setMessages((prev) => [...prev, studentMsg, tutorMsg]);
      setIsLoading(true);

      const meta: TurnMeta = {
        confusion: { confused: false, type: "none" },
        classification: { type: "self_contained" },
        style: { style: "standard", reason: "default" },
      };

      let accumulatedText = "";

      try {
        const resp = await fetch("/api/turn", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, session_state: sessionState }),
          signal: abortRef.current.signal,
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

        const reader = resp.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE blocks (separated by \n\n)
          const boundary = buffer.lastIndexOf("\n\n");
          if (boundary === -1) continue;

          const complete = buffer.slice(0, boundary + 2);
          buffer = buffer.slice(boundary + 2);

          for (const { event, data } of parseSSE(complete)) {
            try {
              const payload = JSON.parse(data);
              switch (event) {
                case "token":
                  accumulatedText += (payload.text as string) ?? "";
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === tutorMsgId
                        ? { ...m, content: accumulatedText }
                        : m
                    )
                  );
                  break;
                case "confusion":
                  meta.confusion = {
                    confused: payload.confused,
                    type: payload.type,
                  };
                  break;
                case "classification":
                  meta.classification = {
                    type: payload.type,
                    rewritten: payload.rewritten ?? undefined,
                  };
                  break;
                case "style":
                  meta.style = { style: payload.style, reason: payload.reason };
                  break;
                case "state":
                  setSessionState(payload as SessionState);
                  break;
                case "done":
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === tutorMsgId
                        ? {
                            ...m,
                            isStreaming: false,
                            confusionType: meta.confusion.type,
                            styleUsed: meta.style.style,
                            classificationResult: meta.classification.type,
                          }
                        : m
                    )
                  );
                  setTurnMeta({ ...meta });
                  break;
                case "error":
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === tutorMsgId
                        ? {
                            ...m,
                            content: accumulatedText || "An error occurred. Please try again.",
                            isStreaming: false,
                          }
                        : m
                    )
                  );
                  break;
              }
            } catch {
              // skip malformed event
            }
          }
        }
      } catch (err: unknown) {
        if ((err as Error).name === "AbortError") return;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === tutorMsgId
              ? {
                  ...m,
                  content: accumulatedText || "Something went wrong. Please try again.",
                  isStreaming: false,
                }
              : m
          )
        );
      } finally {
        setIsLoading(false);
      }
    },
    [sessionState, isLoading]
  );

  const resetSession = useCallback(() => {
    abortRef.current?.abort();
    setSessionState(INITIAL_SESSION);
    setMessages([]);
    setTurnMeta(null);
    setIsLoading(false);
  }, []);

  return {
    sessionState,
    messages,
    isLoading,
    turnMeta,
    sendMessage,
    resetSession,
  };
}
