"use client";

import { useState, useEffect, useRef } from "react";

const API = "http://127.0.0.1:8000/api";

type Notebook = { id: number; name: string; created_at: string };
type FileItem = { id: number; original_filename: string; is_processed: boolean };
type Message = { role: "user" | "assistant"; content: string };

export default function Home() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedNotebook, setSelectedNotebook] = useState<string | null>(null);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState("");
  const [newNotebookName, setNewNotebookName] = useState("");
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { fetchNotebooks(); }, []);
  useEffect(() => { if (selectedNotebook) fetchFiles(); }, [selectedNotebook]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const fetchNotebooks = async () => {
    const res = await fetch(`${API}/notebooks`);
    const data = await res.json();
    setNotebooks(data.notebooks || []);
  };

  const fetchFiles = async () => {
    if (!selectedNotebook) return;
    const res = await fetch(`${API}/notebooks/${selectedNotebook}/files`);
    const data = await res.json();
    setFiles(data.files || []);
  };

  const createNotebook = async () => {
    if (newNotebookName.trim().length < 3) return;
    const res = await fetch(`${API}/notebooks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newNotebookName.trim() }),
    });
    if (res.ok) {
      setNewNotebookName("");
      fetchNotebooks();
    }
  };

  const deleteNotebook = async (name: string) => {
    await fetch(`${API}/notebooks/${name}`, { method: "DELETE" });
    if (selectedNotebook === name) { setSelectedNotebook(null); setFiles([]); setMessages([]); }
    fetchNotebooks();
  };

  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedNotebook || !e.target.files?.[0]) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", e.target.files[0]);
    await fetch(`${API}/notebooks/${selectedNotebook}/upload`, { method: "POST", body: formData });
    setUploading(false);
    fetchFiles();
  };

  const processFiles = async () => {
    if (!selectedNotebook) return;
    setProcessing(true);
    setStatus("Processing files...");
    const res = await fetch(`${API}/notebooks/${selectedNotebook}/process`, { method: "POST" });
    const data = await res.json();
    setStatus(data.message || "Done!");
    setProcessing(false);
    fetchFiles();
    setTimeout(() => setStatus(""), 3000);
  };

  const sendMessage = async () => {
    if (!query.trim() || !selectedNotebook || loading) return;
    const userMsg: Message = { role: "user", content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notebook_name: selectedNotebook, query: userMsg.content }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response || data.detail }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Something went wrong. Please try again." }]);
    }
    setLoading(false);
  };

  const allProcessed = files.length > 0 && files.every(f => f.is_processed);

  return (
    <div className="flex h-screen bg-[#fafaf8] font-[family-name:var(--font-geist-sans)]">

      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-stone-200 bg-white">
        {/* Brand */}
        <div className="px-5 py-5 border-b border-stone-100">
          <h1 className="text-sm font-semibold tracking-widest uppercase text-stone-800">
            RAG Document Chat
          </h1>
          <p className="text-xs text-stone-400 mt-0.5">Chat with your documents</p>
        </div>

        {/* Create Notebook */}
        <div className="px-4 py-4 border-b border-stone-100">
          <p className="text-[10px] uppercase tracking-widest text-stone-400 mb-2">New Notebook</p>
          <div className="flex gap-1.5">
            <input
              className="flex-1 text-xs border border-stone-200 rounded-md px-2.5 py-1.5 outline-none focus:border-stone-400 bg-stone-50"
              placeholder="Name..."
              value={newNotebookName}
              onChange={e => setNewNotebookName(e.target.value)}
              onKeyDown={e => e.key === "Enter" && createNotebook()}
            />
            <button
              onClick={createNotebook}
              className="text-xs bg-stone-800 text-white px-2.5 py-1.5 rounded-md hover:bg-stone-700 transition-colors"
            >+</button>
          </div>
        </div>

        {/* Notebook List */}
        <div className="flex-1 overflow-y-auto px-3 py-3">
          <p className="text-[10px] uppercase tracking-widest text-stone-400 px-1 mb-2">Notebooks</p>
          {notebooks.length === 0 && (
            <p className="text-xs text-stone-400 px-1">No notebooks yet</p>
          )}
          {notebooks.map(nb => (
            <div
              key={nb.id}
              onClick={() => { setSelectedNotebook(nb.name); setMessages([]); }}
              className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer mb-1 transition-colors ${
                selectedNotebook === nb.name
                  ? "bg-stone-800 text-white"
                  : "hover:bg-stone-100 text-stone-700"
              }`}
            >
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm">📓</span>
                <span className="text-xs truncate">{nb.name}</span>
              </div>
              <button
                onClick={e => { e.stopPropagation(); deleteNotebook(nb.name); }}
                className={`opacity-0 group-hover:opacity-100 text-xs px-1 transition-opacity ${
                  selectedNotebook === nb.name ? "text-stone-300 hover:text-white" : "text-stone-400 hover:text-red-500"
                }`}
              >✕</button>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {!selectedNotebook ? (
          /* Empty State */
          <div className="flex-1 flex flex-col items-center justify-center text-center px-8">
            <div className="w-16 h-16 bg-stone-100 rounded-2xl flex items-center justify-center mb-4 text-3xl">📄</div>
            <h2 className="text-lg font-semibold text-stone-700 mb-2">Select or create a notebook</h2>
            <p className="text-sm text-stone-400 max-w-sm">
              Create a notebook, upload your documents, process them, then start chatting.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">

            {/* Top Bar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200 bg-white">
              <div>
                <h2 className="text-sm font-semibold text-stone-800">📓 {selectedNotebook}</h2>
                <p className="text-xs text-stone-400">{files.length} file{files.length !== 1 ? "s" : ""} · {files.filter(f => f.is_processed).length} processed</p>
              </div>
              <div className="flex items-center gap-2">
                {status && <span className="text-xs text-stone-500 bg-stone-100 px-3 py-1 rounded-full">{status}</span>}
                <input ref={fileInputRef} type="file" accept=".pdf,.txt,.md,.docx" className="hidden" onChange={uploadFile} />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="text-xs border border-stone-200 px-3 py-1.5 rounded-lg hover:bg-stone-50 transition-colors text-stone-600 disabled:opacity-50"
                >
                  {uploading ? "Uploading..." : "↑ Upload"}
                </button>
                <button
                  onClick={processFiles}
                  disabled={processing || files.length === 0}
                  className={`text-xs px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 ${
                    allProcessed
                      ? "bg-green-50 text-green-700 border border-green-200"
                      : "bg-stone-800 text-white hover:bg-stone-700"
                  }`}
                >
                  {processing ? "Processing..." : allProcessed ? "✓ Processed" : "⚡ Process Files"}
                </button>
              </div>
            </div>

            {/* Files List */}
            {files.length > 0 && (
              <div className="px-6 py-2 bg-stone-50 border-b border-stone-100 flex gap-2 flex-wrap">
                {files.map(f => (
                  <span key={f.id} className={`text-[10px] px-2 py-1 rounded-full border ${
                    f.is_processed
                      ? "bg-green-50 text-green-700 border-green-200"
                      : "bg-amber-50 text-amber-700 border-amber-200"
                  }`}>
                    {f.is_processed ? "✓" : "○"} {f.original_filename}
                  </span>
                ))}
              </div>
            )}

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <p className="text-sm text-stone-400">
                    {files.length === 0
                      ? "Upload and process files to start chatting"
                      : !allProcessed
                      ? "Process your files first, then ask a question"
                      : "Ask a question about your documents"}
                  </p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-stone-800 text-white rounded-br-sm"
                      : "bg-white border border-stone-200 text-stone-700 rounded-bl-sm shadow-sm"
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-stone-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex gap-1 items-center">
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{animationDelay:"0ms"}}></span>
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{animationDelay:"150ms"}}></span>
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{animationDelay:"300ms"}}></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="px-6 py-4 border-t border-stone-200 bg-white">
              <div className="flex gap-3 items-end">
                <textarea
                  className="flex-1 border border-stone-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-stone-400 resize-none bg-stone-50 leading-relaxed"
                  placeholder="Ask a question about your documents..."
                  rows={1}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !query.trim()}
                  className="bg-stone-800 text-white px-5 py-3 rounded-xl text-sm hover:bg-stone-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
              <p className="text-[10px] text-stone-400 mt-2">Press Enter to send · Shift+Enter for new line</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
