"use client";

import { C } from "./palette";
import { IconSend, SpinnerLight } from "./icons";

type ChatInputProps = {
  question: string;
  onChange: (value: string) => void;
  onAsk: () => void;
  loading: boolean;
};

export function ChatInput({ question, onChange, onAsk, loading }: ChatInputProps) {
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onAsk();
    }
  }

  return (
    <div
      className="shrink-0 px-8 py-5"
      style={{ borderTop: `1px solid ${C.divider}`, background: C.pageBg }}
    >
      <div className="flex gap-3 items-end max-w-3xl mx-auto">
        <textarea
          value={question}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your document…"
          rows={3}
          className="flex-1 resize-none rounded-xl text-sm transition-all"
          style={{
            background: C.inputBg,
            border: `1.5px solid ${C.inputBorder}`,
            color: C.textPrimary,
            padding: "12px 16px",
            outline: "none",
            fontFamily: "inherit",
            letterSpacing: "-0.01em",
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = C.inputFocus;
            e.currentTarget.style.boxShadow = "0 0 0 3px rgba(29,80,55,0.1)";
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = C.inputBorder;
            e.currentTarget.style.boxShadow = "none";
          }}
        />
        <button
          onClick={onAsk}
          disabled={loading}
          className="flex items-center justify-center rounded-xl text-white transition-all shrink-0"
          style={{
            width: "48px",
            height: "48px",
            background: C.accent,
            opacity: loading ? 0.65 : 1,
            cursor: loading ? "not-allowed" : "pointer",
            boxShadow: loading ? "none" : "0 2px 8px rgba(29,80,55,0.25)",
          }}
          onMouseEnter={(e) => { if (!loading) e.currentTarget.style.background = C.accentHover; }}
          onMouseLeave={(e) => { if (!loading) e.currentTarget.style.background = C.accent; }}
        >
          {loading ? <SpinnerLight /> : <IconSend />}
        </button>
      </div>
      <p className="text-center text-xs mt-2" style={{ color: C.textMuted }}>
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
