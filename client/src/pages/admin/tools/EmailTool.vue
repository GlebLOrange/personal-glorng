<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const route = useRoute();
const to = ref("");
const subject = ref("");
const body = ref("");

onMounted(() => {
  if (route.query.to) to.value = String(route.query.to);
  if (route.query.subject) subject.value = String(route.query.subject);
  if (route.query.body) body.value = String(route.query.body);
});
const loading = ref(false);
const previewHtml = ref("");
const { toast } = useNotify();

const canSend = computed(() => to.value.trim() && subject.value.trim() && body.value.trim());

async function send(): Promise<void> {
  if (!canSend.value) return;
  loading.value = true;
  try {
    await api.post("/tools/email/send", {
      to: to.value,
      subject: subject.value,
      body: body.value,
    });
    toast("Email sent", "success");
    to.value = "";
    subject.value = "";
    body.value = "";
    previewHtml.value = "";
  } catch (err) {
    console.error(err);
    toast("Failed to send email", "error");
  } finally {
    loading.value = false;
  }
}

async function preview(): Promise<void> {
  if (!subject.value.trim() || !body.value.trim()) return;
  try {
    const { data } = await api.post<{ html: string }>("/tools/email/preview", {
      to: to.value || "preview@example.com",
      subject: subject.value,
      body: body.value,
    });
    previewHtml.value = data.html;
  } catch (err) {
    console.error(err);
    toast("Failed to generate preview", "error");
  }
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
      <h3 class="text-sm text-surface-mid font-mono">Preview</h3>
      <div
        class="border border-surface-border rounded-lg p-4 bg-white"
        v-html="previewHtml"
      />
    </div>
  </AdminPageLayout>
</template>
