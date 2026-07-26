/** sessionStorage key for Feedback → EmailTool draft handoff (not secrets; still cleared on consume). */
export const EMAIL_DRAFT_STORAGE_KEY = "glorng:email-draft";

export interface EmailDraft {
  to: string;
  subject: string;
  body: string;
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

/** Validate and normalize a draft payload; returns null when shape is invalid. */
export function parseEmailDraft(raw: unknown): EmailDraft | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const record = raw as Record<string, unknown>;
  if (!isString(record.to) || !isString(record.subject) || !isString(record.body)) {
    return null;
  }
  return {
    to: record.to,
    subject: record.subject,
    body: record.body,
  };
}

/** Persist an email draft for the next EmailTool mount. */
export function writeEmailDraft(draft: EmailDraft): void {
  sessionStorage.setItem(EMAIL_DRAFT_STORAGE_KEY, JSON.stringify(draft));
}

/**
 * Read and remove a stored email draft.
 * Returns null when missing or invalid.
 */
export function consumeEmailDraft(): EmailDraft | null {
  const raw = sessionStorage.getItem(EMAIL_DRAFT_STORAGE_KEY);
  sessionStorage.removeItem(EMAIL_DRAFT_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return parseEmailDraft(JSON.parse(raw));
  } catch {
    return null;
  }
}
