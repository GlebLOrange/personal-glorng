<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";

interface NewsSourceForm {
  name: string;
  feed_url: string;
  category: string;
  region: string;
  enabled: boolean;
}

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  form: NewsSourceForm;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:form": [value: NewsSourceForm];
}>();

const title = computed(() => (props.mode === "create" ? "Add source" : "Edit source"));

function patch(patchValue: Partial<NewsSourceForm>): void {
  emit("update:form", { ...props.form, ...patchValue });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}
</script>

<template>
  <BaseDrawer :open="open" :title="title" max-width="md" @close="emit('close')">
    <form id="news-source-form" class="space-y-4" @submit.prevent="emit('save')">
      <BaseInput
        :model-value="form.name"
        label="Name"
        required
        @update:model-value="patch({ name: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.feed_url"
        label="Feed URL"
        type="url"
        required
        @update:model-value="patch({ feed_url: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.category"
        label="Category"
        required
        @update:model-value="patch({ category: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.region"
        label="Region"
        required
        @update:model-value="patch({ region: toStringValue($event) })"
      />
      <label class="flex items-center gap-2 text-sm text-surface-mid">
        <input
          :checked="form.enabled"
          type="checkbox"
          class="size-4 accent-accent-blue"
          @change="patch({ enabled: ($event.target as HTMLInputElement).checked })"
        />
        Enabled
      </label>
    </form>

    <template #footer>
      <div class="flex gap-3">
        <BaseButton type="submit" form="news-source-form" variant="primary" :disabled="loading">
          {{ loading ? "Saving..." : "Save" }}
        </BaseButton>
        <BaseButton type="button" variant="ghost" @click="emit('close')">Cancel</BaseButton>
      </div>
    </template>
  </BaseDrawer>
</template>
