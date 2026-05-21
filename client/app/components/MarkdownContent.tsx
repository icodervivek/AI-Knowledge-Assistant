import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MarkdownContent({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => (
          <p style={{ marginBottom: "10px", lineHeight: "1.75", letterSpacing: "-0.01em" }}>{children}</p>
        ),
        h1: ({ children }) => (
          <h1 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#1a1a18", marginBottom: "10px", marginTop: "16px", letterSpacing: "-0.02em" }}>{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 style={{ fontSize: "1.05rem", fontWeight: 600, color: "#1a1a18", marginBottom: "8px", marginTop: "14px", letterSpacing: "-0.015em" }}>{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 style={{ fontSize: "0.95rem", fontWeight: 600, color: "#3a3a36", marginBottom: "6px", marginTop: "12px", letterSpacing: "-0.01em" }}>{children}</h3>
        ),
        ul: ({ children }) => (
          <ul style={{ paddingLeft: "20px", marginBottom: "10px", listStyleType: "disc" }}>{children}</ul>
        ),
        ol: ({ children }) => (
          <ol style={{ paddingLeft: "20px", marginBottom: "10px", listStyleType: "decimal" }}>{children}</ol>
        ),
        li: ({ children }) => (
          <li style={{ marginBottom: "4px", color: "#3a3a36", letterSpacing: "-0.01em" }}>{children}</li>
        ),
        strong: ({ children }) => (
          <strong style={{ color: "#1a1a18", fontWeight: 600 }}>{children}</strong>
        ),
        em: ({ children }) => (
          <em style={{ color: "#1d5037", fontStyle: "italic" }}>{children}</em>
        ),
        code: ({ children, className }) => {
          const isBlock = className?.includes("language-");
          return isBlock ? (
            <code style={{
              display: "block",
              background: "#f0ebe0",
              border: "1px solid #ddd8cc",
              borderRadius: "8px",
              padding: "12px 16px",
              fontSize: "0.8rem",
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              color: "#1d5037",
              overflowX: "auto",
              marginBottom: "10px",
            }}>{children}</code>
          ) : (
            <code style={{
              background: "#f0ebe0",
              border: "1px solid #ddd8cc",
              borderRadius: "4px",
              padding: "2px 6px",
              fontSize: "0.8rem",
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              color: "#1d5037",
            }}>{children}</code>
          );
        },
        blockquote: ({ children }) => (
          <blockquote style={{
            borderLeft: "3px solid #1d5037",
            paddingLeft: "14px",
            color: "#6b6860",
            fontStyle: "italic",
            margin: "10px 0",
          }}>{children}</blockquote>
        ),
        hr: () => (
          <hr style={{ border: "none", borderTop: "1px solid #ddd8cc", margin: "14px 0" }} />
        ),
        table: ({ children }) => (
          <div style={{ overflowX: "auto", marginBottom: "10px" }}>
            <table style={{ borderCollapse: "collapse", width: "100%", fontSize: "0.85rem" }}>{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th style={{ background: "#f5f0e6", border: "1px solid #ddd8cc", padding: "8px 12px", textAlign: "left", color: "#1a1a18", fontWeight: 600 }}>{children}</th>
        ),
        td: ({ children }) => (
          <td style={{ border: "1px solid #ddd8cc", padding: "7px 12px", color: "#3a3a36" }}>{children}</td>
        ),
      }}
    >
      {children}
    </ReactMarkdown>
  );
}
