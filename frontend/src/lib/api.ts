export type ChatResponse = {
  reply: string;
  thread_id: string;
  employee_id: string;
  employee_email: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function postChat(
  message: string,
  employeeEmail: string,
  threadId?: string | null,
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Employee-Email": employeeEmail,
    },
    body: JSON.stringify({
      message,
      thread_id: threadId || undefined,
    }),
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) detail = data.detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(detail);
  }

  return response.json() as Promise<ChatResponse>;
}
