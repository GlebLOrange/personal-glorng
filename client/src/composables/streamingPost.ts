import { tryRefreshSession } from "@/utils/authSession";

const USER_SAFE_ERRORS: Record<number, string> = {
  401: "Please sign in again.",
  403: "You don't have permission to do that.",
  429: "Too many requests — try again shortly.",
  503: "Search is unavailable right now.",
};

export function userSafeStreamError(
  status: number,
  detail?: string,
  options?: { adminChat?: boolean },
): string {
  if (status === 503 && options?.adminChat) {
    return "AI chat is unavailable — check Settings";
  }
  if (status === 429 && options?.adminChat) {
    return "You're sending messages too quickly — wait a few minutes";
  }
  return USER_SAFE_ERRORS[status] ?? detail ?? "Failed to get AI response";
}

export async function streamingPost(
  url: string,
  body: unknown,
  init?: { signal?: AbortSignal },
): Promise<Response> {
  const doFetch = () =>
    fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: init?.signal,
    });

  let response = await doFetch();
  if (response.status === 401 && (await tryRefreshSession())) {
    response = await doFetch();
  }
  return response;
}
