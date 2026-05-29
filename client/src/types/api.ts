export interface ApiErrorResponse {
  detail?: string | { msg: string }[];
  message?: string;
}

export interface ApiErrorShape {
  response?: {
    status?: number;
    data?: ApiErrorResponse;
  };
  message?: string;
}

export function isApiError(err: unknown): err is ApiErrorShape {
  return typeof err === "object" && err !== null && "response" in err;
}

export function getApiErrorMessage(err: unknown, fallback = "Request failed"): string {
  if (isApiError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail[0]?.msg) {
      return detail[0].msg;
    }
    if (err.message?.trim()) {
      return err.message;
    }
  }
  if (err instanceof Error && err.message.trim()) {
    return err.message;
  }
  return fallback;
}

export async function getApiErrorMessageFromBlob(
  err: unknown,
  fallback = "Request failed",
): Promise<string> {
  if (isApiError(err) && err.response?.data instanceof Blob) {
    try {
      const text = await err.response.data.text();
      const json = JSON.parse(text) as ApiErrorResponse;
      if (typeof json.detail === "string") {
        return json.detail;
      }
    } catch {
      return fallback;
    }
  }
  return getApiErrorMessage(err, fallback);
}
