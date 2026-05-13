"use client";

import { PromptBox } from "./ui/chatgpt-prompt-input";

interface Props {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function MessageInput({ onSend, isLoading }: Props) {
  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <PromptBox 
        onSend={onSend} 
        isLoading={isLoading} 
        placeholder="Ask a question... (Shift+Enter for new line)"
      />
      <p className="text-xs text-gray-400 text-center mt-2">
        Powered by AdaptiveTutor · Enter to send
      </p>
    </div>
  );
}
