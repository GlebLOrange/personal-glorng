import { WEATHER_ROUTE_NAME } from "@/constants/weather";

export type SmallToolTab = {
  id: string;
  label: string;
  to: string;
  name: string;
};

/** Compact tab window peers — shared by SmallToolsWindow and /tools utils section. */
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
] as const;

/** Slugs that belong in the /tools utils section (tab pills only). */
export const SMALL_TOOL_TAB_SLUGS = new Set(SMALL_TOOL_TABS.map((tab) => tab.id));
