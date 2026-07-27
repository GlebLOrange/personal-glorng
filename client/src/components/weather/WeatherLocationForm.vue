<script setup lang="ts">
import { ref } from "vue";

import BaseInput from "@/components/ui/BaseInput.vue";
import FieldHelp from "@/components/ui/FieldHelp.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";

const props = defineProps<{
  addLocation: (query: string) => Promise<void>;
  disabled?: boolean;
  helperText?: string | null;
}>();

const city = ref("");
const error = ref<string | null>(null);
const saving = ref(false);

async function submit(): Promise<void> {
  const trimmed = city.value.trim();
  if (!trimmed) {
    error.value = "Enter a location to search";
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
        :disabled="saving || !city.trim() || props.disabled"
      >
        {{ saving ? "adding…" : "+ location" }}
      </ToolbarPillButton>
    </div>
    <BaseInput
      id="weather-city"
      v-model="city"
      placeholder="location"
      class="min-w-0 w-full"
      aria-label="location"
      :error="error ?? undefined"
      required
    />
  </form>
</template>
