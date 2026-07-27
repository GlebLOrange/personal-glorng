<script setup lang="ts">
import { computed, ref } from "vue";

import BaseInput from "@/components/ui/BaseInput.vue";
import FieldHelp from "@/components/ui/FieldHelp.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { SEARCH_MIN_QUERY_LENGTH } from "@/constants/search";

const props = defineProps<{
  addLocation: (query: string) => Promise<void>;
  disabled?: boolean;
  helperText?: string | null;
}>();

const city = ref("");
const error = ref<string | null>(null);
const saving = ref(false);

const canSubmit = computed(
  () => city.value.trim().length >= SEARCH_MIN_QUERY_LENGTH && !saving.value && !props.disabled,
);

async function submit(): Promise<void> {
  const trimmed = city.value.trim();
  if (trimmed.length < SEARCH_MIN_QUERY_LENGTH) {
    error.value = `Enter at least ${SEARCH_MIN_QUERY_LENGTH} characters`;
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    await props.addLocation(trimmed);
    city.value = "";
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to add location";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="submit">
    <div class="mb-4 flex min-w-0 flex-wrap items-center gap-2">
      <h2 class="flex items-center gap-2 text-lg font-bold text-surface-light">
        <slot name="heading" />
        <FieldHelp v-if="props.helperText" :text="props.helperText" />
      </h2>
      <ToolbarPillButton
        type="submit"
        family="2xx"
        class="ml-auto"
        aria-label="add location"
        :disabled="!canSubmit"
      >
        {{ saving ? "adding…" : "+ location" }}
      </ToolbarPillButton>
    </div>
    <BaseInput
      id="weather-city"
      v-model="city"
      placeholder="location (3+ chars)"
      class="min-w-0 w-full"
      aria-label="location"
      :minlength="SEARCH_MIN_QUERY_LENGTH"
      :error="error ?? undefined"
    />
  </form>
</template>
