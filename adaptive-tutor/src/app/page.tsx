"use client";

import React from "react";
import { useSession } from "@/hooks/useSession";
import { ChatWindow } from "@/components/ChatWindow";
import { PromptBox } from "@/components/ui/chatgpt-prompt-input";
import { 
  ChevronDown, 
  ChevronLeft, 
  ChevronRight, 
  Brain, 
  Settings2,
  Trophy,
  History,
  Info,
  CircleHelp,
  LogOut
} from "lucide-react";

export default function Home() {
  const {
    sessionState,
    messages,
    isLoading,
    sendMessage,
    resetSession,
  } = useSession();

  const isEmpty = messages.length === 0;

  return (
    <div className="flex h-screen bg-white font-sans text-gray-900 overflow-hidden">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="w-72 border-r border-gray-100 bg-[#f9f9f9] flex flex-col shrink-0">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white text-xl">
              🎓
            </div>
            <div>
              <h1 className="font-semibold text-gray-900 text-sm leading-tight">AdaptiveTutor</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Learning System</p>
            </div>
          </div>

          <div className="space-y-8">
            {/* Teaching Style Section */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Settings2 className="w-4 h-4 text-gray-400" />
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Teaching Style</h2>
              </div>
              <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {sessionState.current_style.replace(/_/g, " ")}
                  </span>
                  <div className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                    {Math.round(sessionState.proficiency_estimate * 100)}%
                  </div>
                </div>
                <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-blue-600 h-full transition-all duration-500" 
                    style={{ width: `${sessionState.proficiency_estimate * 100}%` }}
                  />
                </div>
              </div>
            </section>

            {/* Session Stats Section */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Trophy className="w-4 h-4 text-gray-400" />
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Session</h2>
              </div>
              <div className="space-y-3 bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 flex items-center gap-2">
                    <History className="w-3 h-3" /> Turns
                  </span>
                  <span className="text-xs font-bold text-gray-900">{sessionState.turn_history.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 flex items-center gap-2">
                    <Info className="w-3 h-3" /> Proficiency
                  </span>
                  <span className="text-xs font-bold text-gray-900">
                    {Math.round(sessionState.proficiency_estimate * 100)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 flex items-center gap-2">
                    <CircleHelp className="w-3 h-3" /> Confusion (last 5)
                  </span>
                  <span className={`text-xs font-bold ${sessionState.confusion_count_last_5 > 0 ? "text-orange-600" : "text-green-600"}`}>
                    {sessionState.confusion_count_last_5}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 flex items-center gap-2">
                    <Brain className="w-3 h-3" /> Known facts
                  </span>
                  <span className="text-xs font-bold text-gray-900">{sessionState.known_facts.length}</span>
                </div>
              </div>
            </section>

            {/* Session Memory Section */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-4 h-4 text-gray-400" />
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Session Memory</h2>
              </div>
              <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm max-h-48 overflow-y-auto custom-scrollbar">
                {sessionState.known_facts.length > 0 ? (
                  <ul className="space-y-2">
                    {sessionState.known_facts.map((fact, i) => (
                      <li key={i} className="text-[11px] text-gray-600 border-b border-gray-50 pb-2 last:border-0">
                        {fact}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-[11px] text-gray-400 italic">No facts learned yet.</p>
                )}
              </div>
            </section>
          </div>
        </div>

        <div className="mt-auto p-6 border-t border-gray-100">
          <button
            onClick={resetSession}
            className="w-full flex items-center justify-center gap-2 text-xs font-semibold text-gray-500 hover:text-red-600 hover:bg-red-50 p-3 rounded-xl transition-all border border-transparent hover:border-red-100"
          >
            <LogOut className="w-4 h-4" /> Reset Session
          </button>
        </div>
      </aside>

      {/* ── Main content area ────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0 relative bg-[#fcfcfc]">
        {/* Top bar */}
        <div className="absolute top-6 left-6 z-10">
          <button className="flex items-center space-x-2 px-3 py-1 border border-gray-200 bg-white rounded-lg hover:bg-gray-50 transition shadow-sm">
            <span className="text-sm font-medium">AdaptiveTutor Demo</span>
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>

        {isEmpty ? (
          /* Empty State / Landing */
          <div className="flex-1 flex flex-col items-center justify-center px-6 relative">
            <button className="absolute left-6 top-1/2 -translate-y-1/2 bg-neutral-800 text-white p-2 rounded-lg hidden md:flex items-center justify-center shadow-lg hover:bg-black transition">
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <button className="absolute right-6 top-1/2 -translate-y-1/2 bg-neutral-800 text-white p-2 rounded-lg hidden md:flex items-center justify-center shadow-lg hover:bg-black transition">
              <ChevronRight className="w-5 h-5" />
            </button>

            <h1 className="text-4xl md:text-5xl font-medium mb-12 tracking-tight text-center">
              How Can I Help You
            </h1>

            <div className="w-full max-w-3xl">
              <PromptBox 
                onSend={sendMessage} 
                isLoading={isLoading} 
                className="rounded-[2rem] p-4 shadow-xl border-gray-200"
              />
            </div>
          </div>
        ) : (
          /* Active Chat State */
          <>
            <div className="flex-1 overflow-hidden flex flex-col">
              <ChatWindow messages={messages} isLoading={isLoading} />
            </div>
            
            <div className="p-6 bg-transparent">
              <div className="max-w-3xl mx-auto w-full">
                <PromptBox 
                  onSend={sendMessage} 
                  isLoading={isLoading} 
                  className="rounded-[2rem] p-4 shadow-lg border-gray-100"
                />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
