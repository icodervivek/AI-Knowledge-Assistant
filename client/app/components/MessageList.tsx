import type { RefObject } from "react";
import type { Message } from "../types";
import { C } from "./palette";
import { IconBrain } from "./icons";
import { MarkdownContent } from "./MarkdownContent";

type MessageListProps = {
  messages: Message[];
  loading: boolean;
  messagesEndRef: RefObject<HTMLDivElement | null>;
};

export function MessageList({ messages, loading, messagesEndRef }: MessageListProps) {
  return (
    <div
      className="flex-1 overflow-y-auto px-8 py-8"
      style={{ scrollbarWidth: "thin", scrollbarColor: `${C.divider} ${C.pageBg}` }}
    >
      {messages.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center h-full text-center select-none">
          <div
            className="flex items-center justify-center rounded-2xl mb-4"
            style={{ width: "56px", height: "56px", background: C.cardBg, border: `1px solid ${C.cardBorder}`, color: C.accent }}
          >
            <IconBrain />
          </div>
          <p className="text-sm font-medium" style={{ color: C.textSecondary }}>
            No conversation yet
          </p>
          <p className="text-xs mt-1" style={{ color: C.textMuted }}>
            Upload a document, then ask a question to get started.
          </p>
        </div>
      )}

      <div className="space-y-6 max-w-3xl mx-auto">
        {messages.map((message, index) => (
          <div key={index} className="space-y-3">
            {/* User bubble */}
            <div className="flex justify-end">
              <div
                className="rounded-2xl text-sm leading-relaxed"
                style={{
                  background: C.userBubble,
                  color: "#ffffff",
                  padding: "11px 16px",
                  maxWidth: "520px",
                  borderBottomRightRadius: "5px",
                  letterSpacing: "-0.01em",
                }}
              >
                {message.question}
              </div>
            </div>

            {/* AI bubble */}
            <div className="flex gap-3">
              <div
                className="flex items-center justify-center rounded-xl shrink-0 mt-0.5"
                style={{ width: "30px", height: "30px", background: C.accentLight, border: `1px solid ${C.cardBorder}`, color: C.accent }}
              >
                <IconBrain />
              </div>

              <div
                className="flex-1 rounded-2xl"
                style={{
                  background: C.cardBg,
                  border: `1px solid ${C.cardBorder}`,
                  padding: "16px 20px",
                  borderTopLeftRadius: "5px",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
                }}
              >
                
                <div className="text-sm leading-7" style={{ color: C.textPrimary }}>
                  <MarkdownContent>{message.answer}</MarkdownContent>
                  {loading && index === messages.length - 1 && (
                    <span className="animate-pulse inline-block ml-0.5" style={{ color: C.accent }}>▊</span>
                  )}
                </div>

                {message.citations.length > 0 && (
                  <>
                    <div style={{ height: "1px", background: C.divider, margin: "12px 0" }} />
                    <div>
                      <p className="text-xs font-semibold uppercase mb-2" style={{ color: C.labelText, letterSpacing: "0.08em" }}>
                        Sources
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {message.citations.map((citation, i) => (
                          <span
                            key={i}
                            className="rounded-full text-xs px-2.5 py-1"
                            style={{ background: C.pillBg, border: `1px solid ${C.pillBorder}`, color: C.pillText }}
                          >
                            {citation}
                          </span>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
