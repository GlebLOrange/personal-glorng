import { safeNavigationHref } from "@/utils/safeUrl";

export const CONTACT_ORDER = ["email", "telegram", "linkedin", "github"] as const;

export type ContactLinkId = (typeof CONTACT_ORDER)[number];

export const CONTACT_LABELS: Record<ContactLinkId, string> = {
  email: "Email",
  telegram: "Telegram",
  linkedin: "LinkedIn",
  github: "GitHub",
};

export interface ContactLink {
  id: ContactLinkId;
  label: string;
  href: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const INQUIRY_SUBJECT = "Work inquiry";
const INQUIRY_BODY =
  "Hi Gleb,\n\nI'd like to talk about a role / contract. Here's a short brief:\n\n";
const TELEGRAM_INQUIRY_TEXT =
  "Hi Gleb, I'd like to talk about a role or contract.";

function contactHref(id: ContactLinkId, raw: string): string | null {
  if (id === "email") {
    if (!EMAIL_PATTERN.test(raw)) return null;
    const params = new URLSearchParams({
      subject: INQUIRY_SUBJECT,
      body: INQUIRY_BODY,
    });
    return `mailto:${raw}?${params.toString()}`;
  }

  if (id === "telegram") {
    const base = safeNavigationHref(raw);
    if (!base) return null;
    try {
      const url = new URL(base);
      if (!url.searchParams.has("text")) {
        url.searchParams.set("text", TELEGRAM_INQUIRY_TEXT);
      }
      return url.toString();
    } catch {
      return base;
    }
  }

  return safeNavigationHref(raw);
}

export function buildContactLinks(links: Partial<Record<ContactLinkId, string>>): ContactLink[] {
  return CONTACT_ORDER.flatMap((id) => {
    const raw = links[id]?.trim();
    if (!raw) {
      return [];
    }

    const href = contactHref(id, raw);
    if (!href) {
      return [];
    }
    return [{ id, label: CONTACT_LABELS[id], href }];
  });
}
