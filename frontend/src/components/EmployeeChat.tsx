"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { postChat } from "@/lib/api";

type Role = "user" | "assistant" | "system";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
};

const EMPLOYEE_EMAIL =
  process.env.NEXT_PUBLIC_EMPLOYEE_EMAIL ?? "neha.verma@novatech.example";

const SUGGESTIONS = [
  "Who am I and who is my manager?",
  "What is my casual leave balance for 2026?",
  "Show my leave requests.",
];

function newId() {
  return crypto.randomUUID();
}

export default function EmployeeChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: newId(),
      role: "assistant",
      content:
        "Hi — I’m your Employee Agent. Ask about your profile, leave balance, or apply for leave.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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
      const data = await postChat(trimmed, EMPLOYEE_EMAIL);
      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "assistant", content: data.reply },
      ]);
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

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <header className="border-b border-teal-900/10 bg-white/70 px-4 py-4 backdrop-blur-md sm:px-6">
        <div className="mx-auto flex w-full max-w-3xl items-end justify-between gap-4">
          <div>
            <p className="font-[family-name:var(--font-display)] text-2xl tracking-tight text-teal-950 sm:text-3xl">
              NovaTech HRMS
            </p>
            <p className="mt-1 text-sm text-teal-900/70">Employee Agent chat</p>
          </div>
          <p className="rounded-md bg-teal-950/5 px-3 py-1.5 text-xs text-teal-900/80">
            Signed in as <span className="font-medium">{EMPLOYEE_EMAIL}</span>
          </p>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-4 py-6 sm:px-6">
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

        {!loading && messages.length <= 2 && (
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

        {error && (
          <p className="mt-2 text-center text-xs text-rose-700">
            Tip: ensure API (`uvicorn`) and Ollama are running. {error}
          </p>
        )}
      </main>
    </div>
  );
}
