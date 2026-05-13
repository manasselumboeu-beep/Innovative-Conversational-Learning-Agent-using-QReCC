"use client";

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/types/session";
import { ConfusionBadge } from "./ConfusionBadge";
import { User, Sparkles } from "lucide-react";

interface Props {
  messages: Message[];
  isLoading: boolean;
}

export function ChatWindow({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar bg-transparent">
      <div className="max-w-3xl mx-auto w-full px-4 py-12 flex flex-col gap-10">
        {messages.map((msg) => (
          <div key={msg.id} className="group relative flex items-start gap-4 md:gap-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Avatar Column */}
            <div className="flex-shrink-0 mt-1">
              {msg.role === "student" ? (
                <div className="w-8 h-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-gray-500 shadow-sm">
                  <User className="w-5 h-5" />
                </div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center text-white shadow-md ring-2 ring-gray-50">
                  <span className="text-sm">🎓</span>
                </div>
              )}
            </div>

            {/* Content Column */}
            <div className="flex-1 min-w-0 space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-gray-900 tracking-tight">
                  {msg.role === "student" ? "You" : "AdaptiveTutor"}
                </span>
                
                {/* Subtle Metadata for AI messages */}
                {msg.role === "tutor" && !msg.isStreaming && (
                  <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    {msg.confusionType && msg.confusionType !== "none" && (
                      <ConfusionBadge type={msg.confusionType} show={true} />
                    )}
                    {msg.styleUsed && (
                      <span className="flex items-center gap-1 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 px-2 py-0.5 rounded-full border border-gray-100">
                        <Sparkles className="w-2.5 h-2.5" /> {msg.styleUsed}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {msg.role === "student" ? (
                <div className="text-gray-800 text-[16px] leading-relaxed whitespace-pre-wrap font-medium bg-gray-50 px-5 py-3 rounded-2xl rounded-tl-none inline-block border border-gray-100 shadow-sm">
                  {msg.content}
                </div>
              ) : (
                <div className="prose prose-sm md:prose-base prose-neutral max-w-none text-gray-800 leading-relaxed font-normal">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content || "Thinking..."}
                  </ReactMarkdown>
                  
                  {msg.isStreaming && (
                    <span className="inline-block w-2 h-4 bg-gray-900 ml-1 animate-pulse align-middle" />
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Empty Space at Bottom */}
        <div ref={bottomRef} className="h-12" />
      </div>
    </div>
  );
}
