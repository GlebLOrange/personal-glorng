import { computed, nextTick, onMounted, type Ref } from "vue";

import { useChatConfig } from "@/composables/useChatConfig";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useSearchChat } from "@/composables/useSearchChat";
import { useAuthStore } from "@/stores/auth";
import type { AdminChatConfig } from "@/types/search";

/**
 * Admin AI chat: config, transcript, send/clear, and stream errors.
 * Setup status stays on the settings tab.
 */
export function useAiChat(chatEnd: Ref<HTMLElement | null>) {
  const { toast } = useNotify();
  const { isSuperuser } = usePermissions();
  const canSend = computed(() => isSuperuser.value);

  const {
    config: chatConfig,
    loading: configLoading,
    loadConfig,
    isReady,
  } = useChatConfig<AdminChatConfig>({
    path: "/tools/ai-chat/config",
    fallback: {
      enabled: false,
      configured: false,
      model: "",
      provider: "",
      base_url: null,
    },
    onError: (message) => toast(message, "error"),
  });

  const { messages, input, loading, send, clear } = useSearchChat({
    endpoint: "/api/tools/ai-chat",
    onError: (message) => toast(message, "error"),
    beforeSend: async () => {
      const auth = useAuthStore();
      if (!auth.isAuthenticated) {
        toast("Not authenticated", "error");
        return false;
      }
      if (!canSend.value) {
        toast("Superuser access required", "error");
        return false;
      }
      if (!isReady.value) {
        toast("AI chat is not configured — open the settings tab", "error");
        return false;
      }
      return true;
    },
  });

  const providerLabel = computed(() => chatConfig.value?.provider ?? "…");
  const modelLabel = computed(() => chatConfig.value?.model ?? "…");

  function scrollToBottom(): void {
    nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
  }

  async function handleSend(): Promise<void> {
    try {
      await send();
      scrollToBottom();
    } catch {
      // toast handled in useSearchChat
    }
  }

  onMounted(() => {
    void loadConfig().then(() => {
      if (chatConfig.value && !chatConfig.value.configured) {
        toast("AI chat is not configured — open the settings tab", "error");
      }
    });
  });

  return {
    chatConfig,
    configLoading,
    loadConfig,
    isReady,
    canSend,
    providerLabel,
    modelLabel,
    messages,
    input,
    loading,
    clear,
    handleSend,
  };
}
