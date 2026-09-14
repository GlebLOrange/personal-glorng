import { nextTick } from "vue";

/** Filled (trimmed) lines — same filter as save. */
export function filledListCount(items: string[]): number {
  return items.map((item) => item.trim()).filter(Boolean).length;
}

export function splitPasteLines(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

/** Focus a field by data attribute, scoped to the details root when available. */
export async function focusRecipeListField(
  root: HTMLElement | null | undefined,
  selector: string,
  index: number,
): Promise<void> {
  await nextTick();
  const scope: ParentNode = root ?? document;
  const fields = scope.querySelectorAll<HTMLElement>(selector);
  fields[index]?.focus();
}

export function insertBlankAfter(items: string[], index: number): string[] {
  const next = [...items];
  next.splice(index + 1, 0, "");
  return next;
}

export function replaceWithPasteLines(
  items: string[],
  index: number,
  lines: string[],
): string[] {
  const next = [...items];
  next.splice(index, 1, ...lines);
  return next;
}
