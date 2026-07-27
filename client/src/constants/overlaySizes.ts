/** Shared max-width tokens for BaseModal and BaseDrawer. */
export type OverlayMaxWidth = "sm" | "md" | "lg" | "xl" | "2xl";

export const OVERLAY_MAX_WIDTH_CLASS: Record<OverlayMaxWidth, string> = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-xl",
  "2xl": "max-w-2xl",
};
