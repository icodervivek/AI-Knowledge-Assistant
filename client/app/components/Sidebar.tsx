"use client";

import { useRef } from "react";
import { C } from "./palette";
import {
  IconBrain, IconUpload, IconFile, IconRefresh,
  IconDocx, IconExcel, Spinner, SpinnerLight,
} from "./icons";

type SidebarProps = {
  file: File | null;
  onFileChange: (file: File) => void;
  uploading: boolean;
  onUpload: () => void;
  reindexing: boolean;
  onReindex: () => void;
  exportingDocx: boolean;
  onExportDocx: () => void;
  exportingExcel: boolean;
  onExportExcel: () => void;
  hasMessages: boolean;
};

export function Sidebar({
  file, onFileChange,
  uploading, onUpload,
  reindexing, onReindex,
  exportingDocx, onExportDocx,
  exportingExcel, onExportExcel,
  hasMessages,
}: SidebarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <aside
      className="flex flex-col shrink-0"
      style={{ width: "272px", background: C.sidebarBg, borderRight: `1px solid ${C.sidebarBorder}` }}
    >
      {/* Brand */}
      <div className="px-6 pt-7 pb-5">
        <div className="flex items-center gap-3">
          <div
            className="flex items-center justify-center rounded-xl text-white shrink-0"
            style={{ width: "36px", height: "36px", background: C.accent }}
          >
            <IconBrain />
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight" style={{ color: C.textPrimary, letterSpacing: "-0.01em" }}>
              Knowledge AI
            </p>
            <p className="text-xs" style={{ color: C.textMuted }}>
              RAG-powered assistant
            </p>
          </div>
        </div>
      </div>

      <div style={{ height: "1px", background: C.sidebarBorder, margin: "0 24px" }} />

      {/* Documents */}
      <div className="px-6 pt-5 flex-1">
        <p className="text-xs font-semibold uppercase mb-3" style={{ color: C.labelText, letterSpacing: "0.08em" }}>
          Documents
        </p>

        {/* Drop zone */}
        <div
          onClick={() => fileInputRef.current?.click()}
          className="rounded-xl cursor-pointer transition-all mb-3 flex flex-col items-center justify-center"
          style={{
            border: `1.5px dashed ${C.inputBorder}`,
            padding: "18px 12px",
            background: file ? "#f0ebe0" : "transparent",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = C.accent;
            e.currentTarget.style.background = C.accentLight;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = C.inputBorder;
            e.currentTarget.style.background = file ? "#f0ebe0" : "transparent";
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={(e) => { if (e.target.files) onFileChange(e.target.files[0]); }}
          />
          {file ? (
            <div className="flex items-center gap-2" style={{ color: C.accent }}>
              <IconFile />
              <span
                className="text-xs font-medium"
                style={{ maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
              >
                {file.name}
              </span>
            </div>
          ) : (
            <>
              <div className="mb-1.5" style={{ color: C.textMuted }}><IconUpload /></div>
              <p className="text-xs" style={{ color: C.textMuted }}>Click to select a file</p>
            </>
          )}
        </div>

        {/* Upload button */}
        <button
          onClick={onUpload}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 rounded-xl text-sm font-medium text-white transition-all"
          style={{
            padding: "10px 16px",
            background: uploading ? C.accentHover : C.accent,
            opacity: uploading ? 0.75 : 1,
            cursor: uploading ? "not-allowed" : "pointer",
            letterSpacing: "-0.01em",
          }}
          onMouseEnter={(e) => { if (!uploading) e.currentTarget.style.background = C.accentHover; }}
          onMouseLeave={(e) => { if (!uploading) e.currentTarget.style.background = C.accent; }}
        >
          {uploading ? <><SpinnerLight /> Uploading...</> : <><IconUpload /> Upload Document</>}
        </button>

        {/* Re-index button */}
        <button
          onClick={onReindex}
          disabled={reindexing}
          className="w-full flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all"
          style={{
            padding: "10px 16px",
            marginTop: "8px",
            background: "transparent",
            border: `1.5px solid ${C.inputBorder}`,
            color: C.textSecondary,
            opacity: reindexing ? 0.65 : 1,
            cursor: reindexing ? "not-allowed" : "pointer",
            letterSpacing: "-0.01em",
          }}
          onMouseEnter={(e) => {
            if (!reindexing) {
              e.currentTarget.style.borderColor = C.accent;
              e.currentTarget.style.color = C.accent;
              e.currentTarget.style.background = C.accentLight;
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = C.inputBorder;
            e.currentTarget.style.color = C.textSecondary;
            e.currentTarget.style.background = "transparent";
          }}
        >
          {reindexing ? <><Spinner /> Re-indexing...</> : <><IconRefresh /> Re-index Documents</>}
        </button>
      </div>

      {/* Export */}
      <div className="px-6 pb-5 pt-5" style={{ borderTop: `1px solid ${C.sidebarBorder}` }}>
        <p className="text-xs font-semibold uppercase mb-3" style={{ color: C.labelText, letterSpacing: "0.08em" }}>
          Export Conversation
        </p>
        <div className="flex flex-col gap-2">
          <button
            onClick={onExportDocx}
            disabled={exportingDocx || !hasMessages}
            className="flex items-center gap-2 rounded-xl text-sm font-medium text-white transition-all"
            style={{
              padding: "9px 14px",
              background: C.docxBg,
              opacity: exportingDocx || !hasMessages ? 0.4 : 1,
              cursor: exportingDocx || !hasMessages ? "not-allowed" : "pointer",
              letterSpacing: "-0.01em",
            }}
            onMouseEnter={(e) => { if (!exportingDocx && hasMessages) e.currentTarget.style.background = C.docxHover; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = C.docxBg; }}
          >
            {exportingDocx ? <><SpinnerLight size="xs" /> Exporting...</> : <><IconDocx /> Export as DOCX</>}
          </button>

          <button
            onClick={onExportExcel}
            disabled={exportingExcel || !hasMessages}
            className="flex items-center gap-2 rounded-xl text-sm font-medium text-white transition-all"
            style={{
              padding: "9px 14px",
              background: C.excelBg,
              opacity: exportingExcel || !hasMessages ? 0.4 : 1,
              cursor: exportingExcel || !hasMessages ? "not-allowed" : "pointer",
              letterSpacing: "-0.01em",
            }}
            onMouseEnter={(e) => { if (!exportingExcel && hasMessages) e.currentTarget.style.background = C.excelHover; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = C.excelBg; }}
          >
            {exportingExcel ? <><SpinnerLight size="xs" /> Exporting...</> : <><IconExcel /> Export as Excel</>}
          </button>
        </div>
      </div>

      {/* Ethical AI */}
      <div className="px-6 pb-5 pt-4" style={{ borderTop: `1px solid ${C.sidebarBorder}` }}>
        <p className="text-xs font-semibold uppercase mb-2" style={{ color: C.labelText, letterSpacing: "0.08em" }}>
          Ethical AI
        </p>
        <p className="text-xs leading-relaxed" style={{ color: C.textMuted }}>
          This assistant answers only from uploaded documents. Always verify critical information with authoritative sources. Do not upload confidential or personal data.
        </p>
      </div>
    </aside>
  );
}
