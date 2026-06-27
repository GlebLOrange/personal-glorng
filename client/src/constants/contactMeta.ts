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

function contactHref(id: ContactLinkId, raw: string): string | null {
  if (id === "email") {
    return EMAIL_PATTERN.test(raw) ? `mailto:${raw}` : null;
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
