import { ref } from "vue";

import type { Toast } from "@/types";

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useNotify() {
  function toast(
    message: string,
    type: Toast["type"] = "info",
    duration = 3000,
  ): void {
    const id = nextId++;
    toasts.value.push({ id, message, type });
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id);
    }, duration);
  }

  function dismiss(id: number): void {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  return { toasts, toast, dismiss };
}
