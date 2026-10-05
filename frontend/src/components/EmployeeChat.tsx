"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  getChatThread,
  listChatThreads,
  postChat,
  type ChatThread,
} from "@/lib/api";

type Role = "user" | "assistant" | "system";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
};

const EMPLOYEE_EMAIL =
  process.env.NEXT_PUBLIC_EMPLOYEE_EMAIL ?? "neha.verma@novatech.example";

const THREAD_STORAGE_KEY = "hrms.employee.thread_id";

const SUGGESTIONS = [
  "Who am I and who is my manager?",
  "What is my casual leave balance for 2026?",
  "Show my leave requests.",
];

function newId() {
  return crypto.randomUUID();
}

const welcomeMessage = (): ChatMessage => ({
  id: newId(),
  role: "assistant",
  content:
    "Hi — I’m your Employee Agent. Ask about your profile, leave balance, or apply for leave.",
});

export default function EmployeeChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage()]);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingThreads, setLoadingThreads] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const refreshThreads = useCallback(async () => {
    try {
      const data = await listChatThreads(EMPLOYEE_EMAIL);
      setThreads(data);
    } catch {
      // Sidebar list is best-effort; chat can still work.
    } finally {
      setLoadingThreads(false);
    }
  }, []);

  useEffect(() => {
    void refreshThreads();
  }, [refreshThreads]);

  useEffect(() => {
    const saved = window.localStorage.getItem(THREAD_STORAGE_KEY);
    if (!saved) return;

    setLoadingThread(true);
    void getChatThread(saved, EMPLOYEE_EMAIL)
      .then((detail) => {
        setThreadId(detail.thread_id);
        if (detail.messages.length === 0) {
          setMessages([welcomeMessage()]);
          return;
        }
        setMessages(
          detail.messages.map((m) => ({
            id: newId(),
            role: m.role === "user" ? "user" : "assistant",
            content: m.content,
          })),
        );
      })
      .catch(() => {
        window.localStorage.removeItem(THREAD_STORAGE_KEY);
      })
      .finally(() => setLoadingThread(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function startNewChat() {
    window.localStorage.removeItem(THREAD_STORAGE_KEY);
    setThreadId(null);
    setMessages([welcomeMessage()]);
    setError(null);
    setInput("");
    setSidebarOpen(false);
  }

  async function selectThread(id: string) {
    if (loading || loadingThread || id === threadId) {
      setSidebarOpen(false);
      return;
    }
    setLoadingThread(true);
    setError(null);
    try {
      const detail = await getChatThread(id, EMPLOYEE_EMAIL);
      setThreadId(detail.thread_id);
      window.localStorage.setItem(THREAD_STORAGE_KEY, detail.thread_id);
      setMessages(
        detail.messages.length
          ? detail.messages.map((m) => ({
              id: newId(),
              role: m.role === "user" ? "user" : "assistant",
              content: m.content,
            }))
          : [welcomeMessage()],
      );
      setSidebarOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load chat");
    } finally {
      setLoadingThread(false);
    }
  }

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [
      ...prev,
      { id: newId(), role: "user", content: trimmed },
    ]);
    setLoading(true);

    try {
      const data = await postChat(trimmed, EMPLOYEE_EMAIL, threadId);
      setThreadId(data.thread_id);
      window.localStorage.setItem(THREAD_STORAGE_KEY, data.thread_id);
      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "assistant", content: data.reply },
      ]);
      void refreshThreads();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong talking to the API.";
      setError(message);
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: "system",
          content: `Could not reach the agent: ${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void sendMessage(input);
  }

  const sidebarContent = (
    <>
      <div className="border-b border-white/10 px-4 py-5">
        <p className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
          NovaTech HRMS
        </p>
        <p className="mt-1 text-sm text-teal-100/70">Employee Agent</p>
        <p className="mt-3 truncate rounded-md bg-white/10 px-2.5 py-1.5 text-[11px] text-teal-50/90">
          {EMPLOYEE_EMAIL}
        </p>
      </div>

      <div className="p-3">
        <button
          type="button"
          onClick={startNewChat}
          className="w-full rounded-xl bg-teal-500 px-3 py-2.5 text-sm font-medium text-teal-950 transition hover:bg-teal-400"
        >
          New chat
        </button>
      </div>

      <div className="px-3 pb-2 text-[11px] uppercase tracking-wide text-teal-100/50">
        Chats
      </div>

      <div className="flex-1 space-y-1 overflow-y-auto px-2 pb-4">
        {loadingThreads && (
          <p className="px-2 py-3 text-xs text-teal-100/60">Loading chats…</p>
        )}
        {!loadingThreads && threads.length === 0 && (
          <p className="px-2 py-3 text-xs text-teal-100/60">
            No chats yet. Start a conversation.
          </p>
        )}
        {threads.map((thread) => {
          const active = thread.thread_id === threadId;
          return (
            <button
              key={thread.thread_id}
              type="button"
              onClick={() => void selectThread(thread.thread_id)}
              className={
                active
                  ? "w-full rounded-xl bg-white/15 px-3 py-2.5 text-left transition"
                  : "w-full rounded-xl px-3 py-2.5 text-left transition hover:bg-white/10"
              }
            >
              <p className="truncate text-sm text-teal-50">{thread.title}</p>
              <p className="mt-0.5 text-[11px] text-teal-100/55">
                {thread.message_count} messages
              </p>
            </button>
          );
        })}
      </div>
    </>
  );

  return (
    <div className="flex min-h-full flex-1">
      <aside className="hidden h-screen w-72 shrink-0 flex-col border-r border-teal-900/10 bg-teal-950 text-teal-50 md:flex">
        {sidebarContent}
      </aside>

      {sidebarOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <button
            type="button"
            aria-label="Close sidebar"
            className="absolute inset-0 bg-teal-950/40"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="relative z-50 flex h-full w-72 flex-col bg-teal-950 text-teal-50 shadow-2xl">
            {sidebarContent}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center gap-3 border-b border-teal-900/10 bg-white/60 px-4 py-3 backdrop-blur md:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="rounded-md border border-teal-900/15 bg-white px-2.5 py-1.5 text-xs text-teal-900"
          >
            Chats
          </button>
          <p className="truncate text-sm text-teal-900/70">Employee Agent</p>
        </div>

        <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-4 py-6 sm:px-6">
          {loadingThread ? (
            <p className="text-sm text-teal-900/60">Loading conversation…</p>
          ) : (
            <>
              <div className="flex flex-1 flex-col gap-4 overflow-y-auto pb-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={
                      message.role === "user"
                        ? "ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-teal-800 px-4 py-3 text-sm leading-relaxed text-teal-50"
                        : message.role === "system"
                          ? "mx-auto max-w-[90%] rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
                          : "mr-auto max-w-[85%] rounded-2xl rounded-bl-md border border-teal-900/10 bg-white/90 px-4 py-3 text-sm leading-relaxed text-teal-950 shadow-sm"
                    }
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                ))}

                {loading && (
                  <div className="mr-auto max-w-[85%] rounded-2xl rounded-bl-md border border-teal-900/10 bg-white/80 px-4 py-3 text-sm text-teal-800/70">
                    Thinking with Ollama…
                  </div>
                )}
                <div ref={bottomRef} />
              </div>

              {!loading && messages.length <= 2 && !threadId && (
                <div className="mb-3 flex flex-wrap gap-2">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => void sendMessage(suggestion)}
                      className="rounded-full border border-teal-900/15 bg-white/70 px-3 py-1.5 text-left text-xs text-teal-900 transition hover:border-teal-800/40 hover:bg-white"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}

              <form
                onSubmit={onSubmit}
                className="sticky bottom-4 flex gap-2 rounded-2xl border border-teal-900/10 bg-white/90 p-2 shadow-lg shadow-teal-950/5 backdrop-blur"
              >
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Ask about leave, profile, or manager…"
                  disabled={loading}
                  className="min-w-0 flex-1 rounded-xl bg-transparent px-3 py-2.5 text-sm text-teal-950 outline-none placeholder:text-teal-900/40 disabled:opacity-60"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="rounded-xl bg-teal-800 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Send
                </button>
              </form>
            </>
          )}

          {error && (
            <p className="mt-2 text-center text-xs text-rose-700">
              Tip: ensure API (`uvicorn`) and Ollama are running. {error}
            </p>
          )}
        </main>
      </div>
    </div>
  );
}
