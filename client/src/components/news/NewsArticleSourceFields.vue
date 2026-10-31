<script setup lang="ts">
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import type { NewsArticleFormData, NewsSource } from "@/types";

const form = defineModel<NewsArticleFormData>({ required: true });

const props = defineProps<{
  canWrite: boolean;
  sources: NewsSource[];
}>();

function applySource(sourceId: number | null): void {
  const source = props.sources.find((item) => item.id === sourceId);
  form.value.source_id = sourceId;
  if (!source) return;
  form.value.source_name = source.name;
  form.value.source_feed_url = source.feed_url;
}
</script>

<template>
  <Card>
    <h2 class="card-title mb-4">source</h2>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <BaseSelect
        :model-value="form.source_id ?? ''"
        label="source"
        :disabled="!canWrite"
        @update:model-value="
          (value) => applySource(value === '' || value == null ? null : Number(value))
        "
      >
        <option value="">auto from URL host</option>
        <option v-for="source in sources" :key="source.id" :value="source.id">
          {{ source.name }}{{ source.host ? ` (${source.host})` : "" }}
        </option>
      </BaseSelect>
      <BaseInput v-model="form.source_name" label="source name" :disabled="!canWrite" />
      <BaseInput
        v-model="form.source_url"
        label="article url"
        tip="example.com or https://…"
        type="url"
        :disabled="!canWrite"
      />
      <BaseInput
        v-model="form.source_feed_url"
        label="feed url"
        tip="example.com or https://…"
        type="url"
        :disabled="!canWrite"
      />
      <BaseInput
        v-model="form.source_published_at"
        type="datetime-local"
        label="published at"
        :disabled="!canWrite"
      />
    </div>
  </Card>
</template>
