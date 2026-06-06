<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";

const props = defineProps<{
  addLocation: (label: string, query: string) => Promise<void>;
}>();

const city = ref("");
const label = ref("");
const error = ref<string | null>(null);
const saving = ref(false);

async function submit(): Promise<void> {
  const trimmed = city.value.trim();
  if (!trimmed) {
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
  <form class="flex flex-col sm:flex-row gap-3" @submit.prevent="submit">
    <BaseInput v-model="city" placeholder="City name (e.g. Wroclaw)" class="flex-1" required />
    <BaseInput v-model="label" placeholder="Label (optional)" class="sm:max-w-48" />
    <BaseButton type="submit" variant="primary" :disabled="saving || !city.trim()">
      {{ saving ? "..." : "Add" }}
    </BaseButton>
  </form>
  <p v-if="error" class="text-xs text-accent-golden mt-2">{{ error }}</p>
</template>
