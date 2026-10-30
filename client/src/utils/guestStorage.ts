/** Trim and cap a string field from untrusted guest localStorage input. */
export function trimField(value: unknown, maxLength: number): string {
  if (typeof value !== "string") {
    return "";
  }
  return value.trim().slice(0, maxLength);
}

/** Next negative numeric id so guest rows never collide with server ids. */
export function nextNegativeId(items: Array<{ id: number }>): number {
  let min = 0;
  for (const item of items) {
    if (item.id < min) {
      min = item.id;
    }
  }
  return min - 1;
}
