import { ref } from "vue";

/** Shared expand/collapse set for admin list rows (Audit, AppLogs). */
export function useExpandableIds() {
  const expandedIds = ref<Set<number>>(new Set());

  function has(id: number): boolean {
    return expandedIds.value.has(id);
  }

  function toggle(id: number): void {
    const next = new Set(expandedIds.value);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    expandedIds.value = next;
  }

  function clear(): void {
    expandedIds.value = new Set();
  }

  return { expandedIds, has, toggle, clear };
}
