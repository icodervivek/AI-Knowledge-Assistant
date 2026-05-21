"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import type { Message } from "./types";
import { C } from "./components/palette";
import { Sidebar } from "./components/Sidebar";
import { ChatHeader } from "./components/ChatHeader";
import { MessageList } from "./components/MessageList";
import { ChatInput } from "./components/ChatInput";

const API = "http://127.0.0.1:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail ?? error.response?.data?.message;
    if (typeof detail === "string") return detail;
    if (error.message) return error.message;
  }
  return fallback;
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);
  const [exportingExcel, setExportingExcel] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function uploadFile() {
    if (!file) {
      toast.warning("Please select a file before uploading.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data", "X-API-Key": API_KEY },
      });
      toast.success("File uploaded successfully.");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, "File upload failed. Please try again."));
    } finally {
      setUploading(false);
    }
  }

  async function askQuestion() {
    if (!question.trim()) {
      toast.warning("Please enter a question.");
      return;
    }
    setLoading(true);
    const userQuestion = question;
    setQuestion("");
    setMessages((prev) => [...prev, { question: userQuestion, answer: "", citations: [] }]);
    try {
      const response = await axios.post(
        `${API}/ask`,
        { question: userQuestion },
        { headers: { "X-API-Key": API_KEY } },
      );
      const fullAnswer = response.data.answer;
      let current = "";
      for (const char of fullAnswer) {
        current += char;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            answer: current,
            citations: response.data.citations,
          };
          return updated;
        });
        await new Promise((resolve) => setTimeout(resolve, 10));
      }
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, "Could not get an answer."));
    } finally {
      setLoading(false);
    }
  }

  async function exportDocx() {
    if (!messages.length) {
      toast.warning("Ask a question before exporting.");
      return;
    }
    setExportingDocx(true);
    try {
      const response = await axios.post(
        `${API}/export/docx`,
        { messages },
        { responseType: "blob", headers: { "X-API-Key": API_KEY } },
      );
      triggerDownload(response.data, "response.docx");
      toast.success("DOCX exported successfully.");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, "DOCX export failed. Please try again."));
    } finally {
      setExportingDocx(false);
    }
  }

  async function exportExcel() {
    if (!messages.length) {
      toast.warning("Ask a question before exporting.");
      return;
    }
    setExportingExcel(true);
    try {
      const response = await axios.post(
        `${API}/export/excel`,
        { messages },
        { responseType: "blob", headers: { "X-API-Key": API_KEY } },
      );
      triggerDownload(response.data, "response.xlsx");
      toast.success("Excel exported successfully.");
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error, "Excel export failed. Please try again."));
    } finally {
      setExportingExcel(false);
    }
  }

  async function reindex() {
    setReindexing(true);
    try {
      const response = await axios.post(
        `${API}/reindex`,
        {},
        { headers: { "X-API-Key": API_KEY } },
      );
      toast.success(`Re-indexed ${response.data.files_indexed} files successfully.`);
    } catch (error) {
      toast.error(getErrorMessage(error, "Re-index failed."));
    } finally {
      setReindexing(false);
    }
  }

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: C.pageBg, color: C.textPrimary, fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      <ToastContainer position="top-right" autoClose={3000} theme="light" />

      <Sidebar
        file={file}
        onFileChange={setFile}
        uploading={uploading}
        onUpload={uploadFile}
        reindexing={reindexing}
        onReindex={reindex}
        exportingDocx={exportingDocx}
        onExportDocx={exportDocx}
        exportingExcel={exportingExcel}
        onExportExcel={exportExcel}
        hasMessages={messages.length > 0}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader loading={loading} />
        <MessageList messages={messages} loading={loading} messagesEndRef={messagesEndRef} />
        <ChatInput question={question} onChange={setQuestion} onAsk={askQuestion} loading={loading} />
      </main>
    </div>
  );
}

function triggerDownload(data: BlobPart, filename: string) {
  const url = window.URL.createObjectURL(new Blob([data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
