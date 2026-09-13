<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
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

const timezone = defineModel<string>("timezone", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

defineProps<{
  permissions: string[];
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
      <CardHeader class="!mb-2">
        <CardTitle>preferences</CardTitle>
      </CardHeader>
      <form class="space-y-2" @submit.prevent="emit('save')">
        <div class="flex flex-wrap items-end gap-2">
          <BaseSelect
            v-model="timezone"
            compact
            aria-label="timezone"
            class="w-auto min-w-[11rem] max-w-[16rem]"
          >
            <option v-for="zone in timezoneOptions" :key="zone.value" :value="zone.value">
              {{ zone.label }}
            </option>
          </BaseSelect>
          <BaseSelect
            v-model="displayCurrency"
            compact
            aria-label="display currency"
            class="w-auto min-w-[5.5rem] max-w-[7.5rem]"
          >
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </BaseSelect>
          <BaseButton
            type="submit"
            variant="success"
            size="sm"
            :loading="saving"
            :disabled="!canSave"
          >
            {{ saving ? "saving…" : "save" }}
          </BaseButton>
        </div>
        <div>
          <p class="mb-1.5 text-xs text-surface-mid">permissions</p>
          <div v-if="permissions.length" class="flex flex-wrap gap-1.5">
            <span
              v-for="perm in permissions"
              :key="perm"
              class="break-words rounded-full border border-surface-border px-2 py-0.5 text-xs text-surface-muted"
            >
              {{ perm }}
            </span>
          </div>
          <p v-else class="text-xs text-surface-mid">No tool permissions — contact an admin.</p>
        </div>
      </form>
    </CardBody>
  </Card>
</template>
