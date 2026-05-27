import { ref } from "vue";

import { useNotify } from "./useNotify";

export function useClipboard() {
  const copied = ref(false);
  const { toast } = useNotify();

  async function copy(text: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(text);
      copied.value = true;
      toast("Copied to clipboard", "success");
      setTimeout(() => {
        copied.value = false;
      }, 2000);
    } catch {
      toast("Failed to copy", "error");
    }
  }

  return { copied, copy };
}
