<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { consumeEmailDraft } from "@/utils/emailDraft";
import { sanitizeEmailHtml } from "@/utils/sanitizeEmailHtml";

const to = ref("");
const subject = ref("");
const body = ref("");

onMounted(() => {
  const draft = consumeEmailDraft();
  if (!draft) return;
  to.value = draft.to;
  subject.value = draft.subject;
  body.value = draft.body;
});
const previewHtml = ref("");
const { loading, run } = useApiAction();

const canSend = computed(() => to.value.trim() && subject.value.trim() && body.value.trim());

const sanitizedPreviewHtml = computed(() =>
  previewHtml.value ? sanitizeEmailHtml(previewHtml.value) : "",
);

async function send(): Promise<void> {
  if (!canSend.value) return;
  const ok = await run(
    async () => {
      await api.post("/tools/email/send", {
        to: to.value,
        subject: subject.value,
        body: body.value,
      });
      return true;
    },
    { successMessage: "Email sent", errorMessage: "Failed to send email" },
  );
  if (!ok) return;
  to.value = "";
  subject.value = "";
  body.value = "";
  previewHtml.value = "";
}

async function preview(): Promise<void> {
  if (!subject.value.trim() || !body.value.trim()) return;
  const data = await run(
    async () => {
      const response = await api.post<{ html: string }>("/tools/email/preview", {
        to: to.value || "preview@example.com",
        subject: subject.value,
        body: body.value,
      });
      return response.data;
    },
    { errorMessage: "Failed to generate preview", logErrors: false },
  );
  if (data) previewHtml.value = data.html;
}
</script>

<template>
  <AdminPageLayout hub="tools" title="email" back-to="/tools">
    <AdminListToolbar>
      <template #start>
        <div class="flex w-full min-w-0 items-center justify-between gap-2">
          <ToolbarPillButton family="1xx" :disabled="!subject || !body || loading" @click="preview">
            preview
          </ToolbarPillButton>
          <ToolbarPillButton
            family="2xx"
            type="button"
            :disabled="!canSend || loading"
            @click="send"
          >
            {{ loading ? "sending…" : "send" }}
          </ToolbarPillButton>
        </div>
      </template>
    </AdminListToolbar>

    <form class="space-y-3 mb-8" @submit.prevent="send">
      <BaseInput
        id="email-to"
        v-model="to"
        type="email"
        placeholder="to"
        aria-label="to"
        autocomplete="email"
        spellcheck="false"
      />
      <BaseInput
        id="email-subject"
        v-model="subject"
        placeholder="subject"
        aria-label="subject"
        autocomplete="off"
      />
      <BaseTextarea
        id="email-body"
        v-model="body"
        :rows="6"
        placeholder="body"
        aria-label="body"
        autocomplete="off"
      />
    </form>

    <div
      v-if="previewHtml"
      class="space-y-2"
      role="status"
      aria-live="polite"
    >
      <h3 class="text-sm text-surface-mid">preview</h3>
      <!-- eslint-disable-next-line vue/no-v-html -- preview HTML is sanitized with DOMPurify -->
      <div
        class="border border-surface-border rounded-lg p-4 bg-white"
        v-html="sanitizedPreviewHtml"
      />
    </div>
  </AdminPageLayout>
</template>
