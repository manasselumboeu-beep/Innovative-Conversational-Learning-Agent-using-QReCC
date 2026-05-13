"use client";

import { useState } from "react";
import { Fact } from "@/types/session";

interface Props {
  facts: Fact[];
  confusionCount: number;
  turnCount: number;
}

export function MemoryPanel({ facts, confusionCount, turnCount }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden text-xs">
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-gray-600"
      >
        <span className="font-medium flex items-center gap-2">
          <span>🧠</span>
          Session Memory
          {facts.length > 0 && (
            <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full text-xs">
              {facts.length} facts
            </span>
          )}
        </span>
        <span className="text-gray-400">{isOpen ? "▲" : "▼"}</span>
      </button>

      {isOpen && (
        <div className="p-3 bg-white space-y-3">
          <div className="flex gap-4 text-gray-500">
            <span>Turns: <strong className="text-gray-700">{turnCount}</strong></span>
            <span>
              Confusion (last 5):{" "}
              <strong className={confusionCount > 0 ? "text-orange-600" : "text-green-600"}>
                {confusionCount}
              </strong>
            </span>
          </div>

          {facts.length === 0 ? (
            <p className="text-gray-400 italic">No facts extracted yet.</p>
          ) : (
            <ul className="space-y-1.5">
              {facts.map((f) => (
                <li key={f.id} className="flex items-start gap-2">
                  <span className="shrink-0 mt-0.5 w-2 h-2 rounded-full bg-blue-400" />
                  <div>
                    <span className="font-mono text-blue-700">{f.id}</span>
                    {f.summary && (
                      <p className="text-gray-500 mt-0.5">{f.summary}</p>
                    )}
                    <div className="flex gap-2 mt-0.5 text-gray-400">
                      <span>Turn {f.turn}</span>
                      <span>
                        Confidence:{" "}
                        <span
                          className={
                            f.confidence >= 0.8
                              ? "text-green-600"
                              : f.confidence >= 0.6
                              ? "text-yellow-600"
                              : "text-red-500"
                          }
                        >
                          {Math.round(f.confidence * 100)}%
                        </span>
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
