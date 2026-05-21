import { C } from "./palette";
import { Spinner } from "./icons";

type ChatHeaderProps = {
  loading: boolean;
};


export function ChatHeader({ loading }: ChatHeaderProps) {
  return (
    <div
      className="shrink-0 px-8 py-4 flex items-center"
      style={{ borderBottom: `1px solid ${C.divider}`, background: C.pageBg }}
    >
      <div>
        <h1 className="text-sm font-semibold" style={{ color: C.textPrimary, letterSpacing: "-0.01em" }}>
          Chat
        </h1>
        <p className="text-xs" style={{ color: C.textMuted }}>
          Ask questions about your uploaded documents
        </p>
      </div>
      {loading && (
        <div
          className="ml-auto flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium"
          style={{ background: C.thinkingBg, color: C.thinkingText }}
        >
          <Spinner size="xs" />
          Thinking…
        </div>
      )}
    </div>
  );
}
