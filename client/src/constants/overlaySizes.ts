/** Shared max-width tokens for BaseModal and BaseDrawer. */
export type OverlayMaxWidth = "md" | "lg" | "xl" | "2xl";

export const OVERLAY_MAX_WIDTH_CLASS: Record<OverlayMaxWidth, string> = {
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-xl",
  "2xl": "max-w-2xl",
};
