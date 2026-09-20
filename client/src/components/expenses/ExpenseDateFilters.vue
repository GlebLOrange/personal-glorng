<script setup lang="ts">
import { computed } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import type { DateFilterMode, MonthPreset } from "@/composables/useExpenseFilters";

const props = defineProps<{
  hasActiveFilters: boolean;
}>();

const monthPreset = defineModel<MonthPreset>("monthPreset", { required: true });
const dateFilterMode = defineModel<DateFilterMode>("dateFilterMode", { required: true });
const selectedMonth = defineModel<string>("selectedMonth", { required: true });
const dateFrom = defineModel<string>("dateFrom", { required: true });
const dateTo = defineModel<string>("dateTo", { required: true });

const emit = defineEmits<{
  applyPreset: [preset: MonthPreset];
  clearFilters: [];
}>();

/** Presets shown in the period dropdown — no dedicated “month” (custom) picker. */
const PERIOD_PRESETS: Array<{ id: MonthPreset; label: string }> = [
  { id: "this_month", label: "this month" },
  { id: "last_month", label: "last month" },
  { id: "range", label: "range" },
];

const activeLabel = computed(() => {
  if (monthPreset.value === "last_month") return "last month";
  if (monthPreset.value === "range") return "range";
  if (monthPreset.value === "this_month") return "this month";
  // legacy custom → treat as this month for the trigger label
  return "this month";
});

function selectPreset(preset: MonthPreset): void {
  emit("applyPreset", preset);
}
</script>

<template>
  <AdminFilterDropdown
    label="period"
    :has-active-filters="props.hasActiveFilters || monthPreset !== 'this_month'"
    :active-label="activeLabel"
    :option-labels="PERIOD_PRESETS.map((p) => p.label)"
    :match-trigger-width="false"
    @clear="emit('clearFilters')"
  >
    <template #chips>
      <BaseButton
        v-for="preset in PERIOD_PRESETS"
        :key="preset.id"
        size="sm"
        class="w-full justify-start"
        :variant="monthPreset === preset.id ? 'primary' : 'ghost'"
        @click="selectPreset(preset.id)"
      >
        {{ preset.label }}
      </BaseButton>
    </template>

    <div v-if="dateFilterMode === 'range'" class="flex flex-col gap-2">
      <BaseInput v-model="dateFrom" type="date" label="from" />
      <BaseInput v-model="dateTo" type="date" label="to" />
    </div>
  </AdminFilterDropdown>
</template>
