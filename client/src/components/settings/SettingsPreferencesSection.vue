<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";

interface TimezoneOption {
  value: string;
  label: string;
}

/** Curated IANA presets for settings — not a full zone list. */
const TIMEZONE_PRESETS: readonly TimezoneOption[] = [
  { value: "UTC", label: "UTC" },
  { value: "Europe/Warsaw", label: "Warsaw (EU)" },
  { value: "Europe/Berlin", label: "Berlin (EU)" },
  { value: "Europe/London", label: "London (UK)" },
  { value: "Europe/Paris", label: "Paris (EU)" },
  { value: "Europe/Kyiv", label: "Kyiv (EU)" },
  { value: "America/New_York", label: "New York (US)" },
  { value: "America/Chicago", label: "Chicago (US)" },
  { value: "America/Denver", label: "Denver (US)" },
  { value: "America/Los_Angeles", label: "Los Angeles (US)" },
  { value: "Asia/Dubai", label: "Dubai" },
  { value: "Asia/Singapore", label: "Singapore" },
  { value: "Asia/Tokyo", label: "Tokyo" },
  { value: "Australia/Sydney", label: "Sydney" },
];

const displayName = defineModel<string>("displayName", { required: true });
const timezone = defineModel<string>("timezone", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

defineProps<{
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();

const timezoneOptions = computed((): TimezoneOption[] => {
  const current = timezone.value.trim();
  if (!current || TIMEZONE_PRESETS.some((z) => z.value === current)) {
    return [...TIMEZONE_PRESETS];
  }
  // Preserve legacy / unusual IANA values not in the curated list.
  return [{ value: current, label: current }, ...TIMEZONE_PRESETS];
});
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <form class="space-y-3" @submit.prevent="emit('save')">
        <BaseInput
          v-model="displayName"
          name="display-name"
          autocomplete="name"
          placeholder="display name"
          aria-label="display name"
        />
        <div class="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_auto]">
          <BaseSelect
            v-model="timezone"
            compact
            aria-label="timezone"
            class="min-w-0 w-full"
          >
            <option v-for="zone in timezoneOptions" :key="zone.value" :value="zone.value">
              {{ zone.label }}
            </option>
          </BaseSelect>
          <BaseSelect
            v-model="displayCurrency"
            compact
            aria-label="display currency"
            class="w-full sm:w-auto sm:shrink-0"
          >
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </BaseSelect>
        </div>
        <div class="flex justify-end">
          <BaseButton type="submit" variant="save" size="sm" :loading="saving" :disabled="!canSave">
            {{ saving ? "saving…" : "save" }}
          </BaseButton>
        </div>
      </form>
    </CardBody>
  </Card>
</template>
