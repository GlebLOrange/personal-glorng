<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { sanitizeEmailHtml } from "@/utils/sanitizeEmailHtml";

const route = useRoute();
const to = ref("");
const subject = ref("");
const body = ref("");

onMounted(() => {
  if (route.query.to) to.value = String(route.query.to);
  if (route.query.subject) subject.value = String(route.query.subject);
  if (route.query.body) body.value = String(route.query.body);
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
  <AdminPageLayout title="email">
    <form class="space-y-3 mb-8" @submit.prevent="send">
      <BaseInput v-model="to" type="email" label="To" placeholder="recipient@example.com" />
      <BaseInput v-model="subject" label="Subject" placeholder="Email subject" />
      <BaseTextarea v-model="body" label="Body" :rows="6" placeholder="Write your message..." />
      <div class="flex gap-3">
        <BaseButton variant="primary" :disabled="!canSend || loading">
          {{ loading ? "Sending..." : "Send" }}
        </BaseButton>
        <BaseButton type="button" variant="ghost" :disabled="!subject || !body" @click="preview">
          Preview
        </BaseButton>
      </div>
    </form>

    <div v-if="previewHtml" class="space-y-2">
      <h3 class="text-sm text-surface-mid">Preview</h3>
      <!-- eslint-disable-next-line vue/no-v-html -- preview HTML is sanitized with DOMPurify -->
      <div
        class="border border-surface-border rounded-lg p-4 bg-white"
        v-html="sanitizedPreviewHtml"
      />
    </div>
  </AdminPageLayout>
</template>
