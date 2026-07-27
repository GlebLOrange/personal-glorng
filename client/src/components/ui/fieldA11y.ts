type FieldMessagesOptions = {
  ariaDescribedBy?: unknown;
  hint?: string;
  hintId: string;
  error?: string;
  errorId: string;
};

type FieldAccessibleNameOptions = {
  ariaLabel?: unknown;
  hasVisibleLabel: boolean;
  label?: string;
  prefix?: string;
};

export function buildFieldDescribedBy({
  ariaDescribedBy,
  hint,
  hintId,
  error,
  errorId,
}: FieldMessagesOptions): string | undefined {
  const ids: string[] = [];

  if (typeof ariaDescribedBy === "string" && ariaDescribedBy.trim()) {
    ids.push(...ariaDescribedBy.trim().split(/\s+/));
  }

  if (error) ids.push(errorId);
  else if (hint) ids.push(hintId);

  return ids.length ? [...new Set(ids)].join(" ") : undefined;
}

export function buildFieldAccessibleName({
  ariaLabel,
  hasVisibleLabel,
  label,
  prefix,
}: FieldAccessibleNameOptions): string | undefined {
  if (typeof ariaLabel === "string" && ariaLabel.trim()) return ariaLabel;
  if (hasVisibleLabel) return undefined;
  if (label) return label;
  return prefix || undefined;
}

export function pickNativeAttrs(
  attrs: Record<string, unknown>,
  omittedKeys: string[] = [],
): Record<string, unknown> {
  const omitted = new Set(["class", "style", ...omittedKeys]);
  const nativeAttrs: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(attrs)) {
    if (!omitted.has(key)) nativeAttrs[key] = value;
  }

  return nativeAttrs;
}
