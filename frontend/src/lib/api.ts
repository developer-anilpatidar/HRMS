export type ChatResponse = {
  reply: string;
  thread_id: string;
  employee_id: string;
  employee_email: string;
};

export type ChatThread = {
  thread_id: string;
  title: string;
  message_count: number;
  updated_at: string | null;
};

export type ChatThreadMessage = {
  role: "user" | "assistant" | string;
  content: string;
};

export type ChatThreadDetail = {
  thread_id: string;
  messages: ChatThreadMessage[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function employeeHeaders(employeeEmail: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Employee-Email": employeeEmail,
  };
}

async function readError(response: Response): Promise<string> {
  let detail = `Request failed (${response.status})`;
  try {
    const data = (await response.json()) as { detail?: string };
    if (data.detail) detail = data.detail;
  } catch {
    // ignore JSON parse errors
  }
  return detail;
}

export async function postChat(
  message: string,
  employeeEmail: string,
  threadId?: string | null,
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: employeeHeaders(employeeEmail),
    body: JSON.stringify({
      message,
      thread_id: threadId || undefined,
    }),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json() as Promise<ChatResponse>;
}

export async function listChatThreads(employeeEmail: string): Promise<ChatThread[]> {
  const response = await fetch(`${API_URL}/chat/threads`, {
    headers: employeeHeaders(employeeEmail),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json() as Promise<ChatThread[]>;
}

export async function getChatThread(
  threadId: string,
  employeeEmail: string,
): Promise<ChatThreadDetail> {
  const response = await fetch(`${API_URL}/chat/threads/${threadId}`, {
    headers: employeeHeaders(employeeEmail),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json() as Promise<ChatThreadDetail>;
}
