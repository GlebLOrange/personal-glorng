<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";

const props = defineProps<{
  addLocation: (label: string, query: string) => Promise<void>;
  disabled?: boolean;
  helperText?: string | null;
}>();

const city = ref("");
const label = ref("");
const error = ref<string | null>(null);
const saving = ref(false);

async function submit(): Promise<void> {
  const trimmed = city.value.trim();
  if (!trimmed) {
    error.value = "Enter a city to search";
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    await props.addLocation(label.value.trim() || trimmed, trimmed);
    city.value = "";
    label.value = "";
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to add location";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <form class="flex flex-col sm:flex-row sm:items-end gap-3" @submit.prevent="submit">
    <BaseInput
      id="weather-city"
      v-model="city"
      placeholder="City"
      class="flex-1"
      :error="error ?? undefined"
      required
    />
    <BaseInput
      id="weather-label"
      v-model="label"
      placeholder="Label (optional)"
      class="sm:max-w-48"
    />
    <BaseButton
      type="submit"
      variant="primary"
      size="field"
      :loading="saving"
      :disabled="!city.trim() || props.disabled"
    >
      {{ saving ? "adding…" : "add" }}
    </BaseButton>
  </form>
  <p v-if="props.helperText" class="text-xs text-surface-mid mt-2">{{ props.helperText }}</p>
</template>
