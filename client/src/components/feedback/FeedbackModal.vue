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
import { useApiAction } from "@/composables/useApiAction";

const EMAIL_HELP = "use a full address like name@example.com";

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
const theme = ref(isInquiry.value ? "work inquiry" : "");
const message = ref("");
const { run: runSubmit, loading } = useApiAction();

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
        subjectPlaceholder: "role, contract, or collaboration",
        messagePlaceholder: "what are you hiring for, timeline, and how to reach you…",
        submit: "send inquiry",
        success: "message sent — i'll reply soon.",
        error: "failed to send inquiry",
      }
    : {
        title: "send feedback",
        subjectPlaceholder: "what is this about?",
        messagePlaceholder: "your feedback…",
        submit: "send feedback",
        success: "feedback sent — thank you!",
        error: "failed to send feedback",
      },
);

async function submit(): Promise<void> {
  if (!canSubmit.value) return;
  const ok = await runSubmit(
    async () => {
      await api.post("/feedback", {
        email: email.value.trim(),
        theme: theme.value,
        message: message.value,
      });
      return true;
    },
    { successMessage: copy.value.success, errorMessage: copy.value.error },
  );
  if (ok) emit("close");
}
</script>

<template>
  <BaseModal :open="open" :title="copy.title" max-width="md" @close="$emit('close')">
    <form id="feedback-modal-form" class="space-y-3" @submit.prevent="submit">
      <BaseInput
        v-model="email"
        type="email"
        placeholder="your@email.com"
        autocomplete="email"
        :tone="emailTone"
        :error="emailError"
      />
      <BaseInput v-model="theme" :placeholder="copy.subjectPlaceholder" />
      <BaseTextarea v-model="message" :placeholder="copy.messagePlaceholder" :rows="3" />
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton variant="secondary" type="button" @click="$emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            form="feedback-modal-form"
            family="2xx"
            type="submit"
            :disabled="loading || !canSubmit"
          >
            {{ loading ? "sending…" : copy.submit }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseModal>
</template>
