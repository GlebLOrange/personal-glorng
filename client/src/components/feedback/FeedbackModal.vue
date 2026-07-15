<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const emit = defineEmits<{ close: [] }>();

const email = ref("");
const theme = ref("");
const message = ref("");
const loading = ref(false);
const { toast } = useNotify();

const canSubmit = computed(() => email.value.trim() && theme.value.trim() && message.value.trim());

async function submit(): Promise<void> {
  if (!canSubmit.value) return;
  loading.value = true;
  try {
    await api.post("/feedback", {
      email: email.value,
      theme: theme.value,
      message: message.value,
    });
    toast("Feedback sent — thank you!", "success");
    emit("close");
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to send feedback", "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <BaseModal title="send feedback" @close="$emit('close')">
    <form class="space-y-3" @submit.prevent="submit">
      <BaseInput
        v-model="email"
        type="email"
        placeholder="email (your@email.com)"
        aria-label="email (your@email.com)"
      />
      <BaseInput
        v-model="theme"
        placeholder="subject (what is this about?)"
        aria-label="subject (what is this about?)"
      />
      <BaseTextarea
        v-model="message"
        placeholder="feedback (your message...)"
        aria-label="feedback (your message...)"
      />
      <BaseButton variant="primary" :disabled="!canSubmit || loading" class="w-full">
        {{ loading ? "sending..." : "send feedback" }}
      </BaseButton>
    </form>
  </BaseModal>
</template>
