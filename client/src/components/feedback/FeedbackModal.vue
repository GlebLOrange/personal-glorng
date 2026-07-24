<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const props = withDefaults(
  defineProps<{
    open?: boolean;
    /** inquiry = hire/work path; feedback = product notes */
    intent?: "inquiry" | "feedback";
  }>(),
  { open: true, intent: "feedback" },
);

const emit = defineEmits<{ close: [] }>();

const isInquiry = computed(() => props.intent === "inquiry");

const email = ref("");
const theme = ref(isInquiry.value ? "Work inquiry" : "");
const message = ref("");
const loading = ref(false);
const { toast } = useNotify();

const canSubmit = computed(() => email.value.trim() && theme.value.trim() && message.value.trim());

const copy = computed(() =>
  isInquiry.value
    ? {
        title: "get in touch",
        subjectLabel: "Subject",
        subjectPlaceholder: "Role, contract, or collaboration",
        messageLabel: "Brief",
        messagePlaceholder: "What are you hiring for, timeline, and how to reach you…",
        submit: "send inquiry",
        success: "Message sent — I'll reply soon.",
        error: "Failed to send inquiry",
      }
    : {
        title: "send feedback",
        subjectLabel: "Subject",
        subjectPlaceholder: "What is this about?",
        messageLabel: "Message",
        messagePlaceholder: "Your feedback…",
        submit: "send feedback",
        success: "Feedback sent — thank you!",
        error: "Failed to send feedback",
      },
);

async function submit(): Promise<void> {
  if (!canSubmit.value) return;
  loading.value = true;
  try {
    await api.post("/feedback", {
      email: email.value,
      theme: theme.value,
      message: message.value,
    });
    toast(copy.value.success, "success");
    emit("close");
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast(copy.value.error, "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <BaseModal :open="open" :title="copy.title" max-width="md" @close="$emit('close')">
    <form id="feedback-modal-form" class="space-y-3" @submit.prevent="submit">
      <BaseInput
        v-model="email"
        type="email"
        label="Email"
        placeholder="your@email.com"
        autocomplete="email"
      />
      <BaseInput
        v-model="theme"
        :label="copy.subjectLabel"
        :placeholder="copy.subjectPlaceholder"
      />
      <BaseTextarea
        v-model="message"
        :label="copy.messageLabel"
        :placeholder="copy.messagePlaceholder"
        :rows="5"
      />
    </form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton variant="ghost" danger type="button" @click="$emit('close')">cancel</BaseButton>
        <BaseButton
          form="feedback-modal-form"
          variant="success"
          type="submit"
          :loading="loading"
          :disabled="!canSubmit"
        >
          {{ loading ? "sending..." : copy.submit }}
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
