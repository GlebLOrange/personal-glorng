<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { newsSourceEnabledClass } from "@/constants/filterColors";

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

const title = computed(() => (props.mode === "create" ? "+ source" : "edit source"));

function patch(patchValue: Partial<NewsSourceForm>): void {
  emit("update:form", { ...props.form, ...patchValue });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}
</script>

<template>
  <BaseDrawer
    :open="open"
    :title="title"
    max-width="md"
    :header-class="newsSourceEnabledClass(form.enabled)"
    @close="emit('close')"
  >
    <form id="news-source-form" class="space-y-4" @submit.prevent="emit('save')">
      <BaseInput
        :model-value="form.feed_url"
        placeholder="feed url"
        type="url"
        required
        @update:model-value="patch({ feed_url: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.name"
        placeholder="title"
        required
        @update:model-value="patch({ name: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.category"
        placeholder="category"
        required
        @update:model-value="patch({ category: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.region"
        placeholder="region"
        required
        @update:model-value="patch({ region: toStringValue($event) })"
      />
      <label
        class="flex cursor-pointer items-center rounded-md px-2.5 py-1.5 text-sm has-[:focus-visible]:outline-none has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-accent-blue/50"
        :class="newsSourceEnabledClass(form.enabled)"
      >
        <input
          :checked="form.enabled"
          type="checkbox"
          class="sr-only"
          @change="patch({ enabled: ($event.target as HTMLInputElement).checked })"
        />
        {{ form.enabled ? "enabled" : "disabled" }}
      </label>
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton type="button" variant="secondary" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton type="submit" form="news-source-form" family="2xx" :disabled="loading">
            {{ loading ? "saving..." : "save" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
