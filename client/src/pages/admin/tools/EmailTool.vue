<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import PageShell from "@/components/layout/PageShell.vue";
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
  <PageShell
    title="send email"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'send email' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
  >
    <div class="page-tool-actions">
      <AdminListToolbar>
        <template #start>
          <div class="flex w-full items-center justify-between gap-2">
            <ToolbarPillButton
              action="create"
              :disabled="!subject || !body || loading"
              @click="preview"
            >
              preview
            </ToolbarPillButton>
            <ToolbarPillButton
              action="save"
              type="button"
              :disabled="!canSend || loading"
              @click="send"
            >
              {{ loading ? "sending…" : "send" }}
            </ToolbarPillButton>
          </div>
        </template>
      </AdminListToolbar>

      <form class="flex w-full flex-col gap-3" @submit.prevent="send">
        <BaseInput
          id="email-to"
          v-model="to"
          type="email"
          label="to"
          tip="email@example.com"
          autocomplete="email"
          spellcheck="false"
          class="w-full"
        />
        <BaseInput
          id="email-subject"
          v-model="subject"
          label="subject"
          autocomplete="off"
          class="w-full"
        />
        <BaseTextarea
          id="email-body"
          v-model="body"
          :rows="6"
          label="body"
          autocomplete="off"
          class="w-full"
        />
      </form>
    </div>

    <div
      v-if="previewHtml"
      class="w-full min-w-0 self-stretch space-y-2"
      role="status"
      aria-live="polite"
    >
      <h3 class="text-sm text-surface-mid">preview</h3>
      <!-- eslint-disable vue/no-v-html -- preview HTML is sanitized with DOMPurify -->
      <div
        class="border border-surface-border rounded-lg p-4 bg-white"
        v-html="sanitizedPreviewHtml"
      />
      <!-- eslint-enable vue/no-v-html -->
    </div>
  </PageShell>
</template>
