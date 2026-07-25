<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { isValidEmail } from "@/constants/contactMeta";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const EMAIL_HELP = "Use a full address like name@example.com";

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

const emailTone = computed<"error" | "success" | undefined>(() => {
  if (!email.value.trim()) return undefined;
  return isValidEmail(email.value) ? "success" : "error";
});

const emailError = computed(() => (emailTone.value === "error" ? EMAIL_HELP : undefined));

const canSubmit = computed(
  () =>
    isValidEmail(email.value) && theme.value.trim().length > 0 && message.value.trim().length > 0,
);

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
      email: email.value.trim(),
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
        :tone="emailTone"
        :error="emailError"
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
      />    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton
            danger
            type="button"
            @click="$emit('close')"
          >
            cancel
          </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            form="feedback-modal-form"
            family="2xx"
            type="submit"
            :disabled="loading || !canSubmit"
          >
            {{ loading ? "sending..." : copy.submit }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseModal>
</template>
