import { WEATHER_ROUTE_NAME } from "@/constants/weather";

export type SmallToolTab = {
  id: string;
  label: string;
  to: string;
  name: string;
  /** Login-only tools — hidden from guests. */
  requiresAuth?: boolean;
  /** Capability slug when requiresAuth. */
  slug?: string;
};

/** Compact tab window peers — shared by SmallToolsWindow and /tools utils spoiler. */
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
  {
    id: "vid-download",
    label: "video downloader",
    to: "/vid-download",
    name: "vid-download",
    requiresAuth: true,
    slug: "vid-download",
  },
  {
    id: "email",
    label: "send email",
    to: "/tools/send-email",
    name: "tool-email",
    requiresAuth: true,
    slug: "email",
  },
] as const;

/** Slugs that belong in the /tools utils spoiler (tab pills only). */
export const SMALL_TOOL_TAB_SLUGS = new Set(SMALL_TOOL_TABS.map((tab) => tab.id));
