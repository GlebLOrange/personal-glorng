import { WEATHER_ROUTE_NAME } from "@/constants/weather";

export type SmallToolTab = {
  id: string;
  label: string;
  to: string;
  name: string;
};

/** Compact window peers — shared by SmallToolsWindow and /tools utils pills. */
export const SMALL_TOOL_TABS: readonly SmallToolTab[] = [
  { id: "weather", label: "weather", to: "/weather", name: WEATHER_ROUTE_NAME },
  { id: "calculator", label: "calculator", to: "/calculator", name: "calculator" },
  {
    id: "password-generator",
    label: "password generator",
    to: "/password-generator",
    name: "password-generator",
  },
  { id: "qr-generator", label: "qr generator", to: "/qr-generator", name: "qr-generator" },
  { id: "url-shortener", label: "url shortener", to: "/shortener", name: "shortener" },
  { id: "file-share", label: "file share", to: "/file-share", name: "tool-file-share" },
  { id: "data-extract", label: "data extract", to: "/data-extract", name: "tool-data-extract" },
  { id: "vid-download", label: "video downloader", to: "/vid-download", name: "vid-download" },
  { id: "email", label: "send email", to: "/tools/send-email", name: "tool-email" },
  { id: "ai-chat", label: "ai chat", to: "/admin/ai-chat", name: "tool-ai-chat" },
] as const;

/** Slugs that belong in the compact utils window (tab pills only). */
export const SMALL_TOOL_TAB_SLUGS = new Set(SMALL_TOOL_TABS.map((tab) => tab.id));

const PUBLIC_SMALL_TOOL_IDS = new Set([
  "weather",
  "calculator",
  "password-generator",
  "qr-generator",
  "url-shortener",
]);

const ACCESS_SMALL_TOOL_IDS = new Set(["file-share", "data-extract", "vid-download"]);

/** Tabs a visitor can open. Public tools always; extras need access; email and ai chat need a superuser. */
export function visibleSmallToolTabs(input: {
  canAccess: (slug: string) => boolean;
  isSuperuser: boolean;
  aiChatEnabled: boolean;
}): SmallToolTab[] {
  return SMALL_TOOL_TABS.filter((tab) => {
    if (PUBLIC_SMALL_TOOL_IDS.has(tab.id)) return true;
    if (tab.id === "ai-chat") return input.isSuperuser && input.aiChatEnabled;
    if (tab.id === "email") return input.isSuperuser;
    if (ACCESS_SMALL_TOOL_IDS.has(tab.id)) return input.canAccess(tab.id);
    return false;
  });
}
