import { ref } from "vue";

import type { Toast } from "@/types";

const toasts = ref<Toast[]>([]);
let nextId = 0;
const timers = new Map<number, ReturnType<typeof setTimeout>>();
const durations = new Map<number, number>();

function clearTimer(id: number): void {
  const timer = timers.get(id);
  if (timer) {
    clearTimeout(timer);
    timers.delete(id);
  }
}

function scheduleDismiss(id: number, duration: number): void {
  clearTimer(id);
  timers.set(
    id,
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id);
      timers.delete(id);
      durations.delete(id);
    }, duration),
  );
}

export function useNotify() {
  function toast(message: string, type: Toast["type"] = "info", duration?: number): void {
    const id = nextId++;
    const ms = duration ?? (type === "error" ? 6000 : 4000);
    toasts.value.push({ id, message, type });
    durations.set(id, ms);
    scheduleDismiss(id, ms);
  }

  function dismiss(id: number): void {
    clearTimer(id);
    durations.delete(id);
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  function pause(id: number): void {
    clearTimer(id);
  }

  function resume(id: number): void {
    if (!toasts.value.some((t) => t.id === id)) return;
    const ms = durations.get(id) ?? 4000;
    scheduleDismiss(id, ms);
  }

  return { toasts, toast, dismiss, pause, resume };
}
