<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import type { DateFilterMode, MonthPreset } from "@/composables/useExpenseFilters";

defineProps<{
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
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap gap-2 items-end">
      <BaseButton
        v-for="preset in ['this_month', 'last_month', 'custom', 'range'] as MonthPreset[]"
        :key="preset"
        :variant="monthPreset === preset ? 'primary' : 'ghost'"
        size="sm"
        @click="emit('applyPreset', preset)"
      >
        {{
          preset === "this_month"
            ? "this month"
            : preset === "last_month"
              ? "last month"
              : preset === "custom"
                ? "month"
                : "range"
        }}
      </BaseButton>

      <BaseInput
        v-if="dateFilterMode === 'month'"
        v-model="selectedMonth"
        type="month"
        compact
        aria-label="month"
        @change="monthPreset = 'custom'"
      />

      <template v-else>
        <BaseInput v-model="dateFrom" type="date" compact aria-label="from date" />
        <span class="text-surface-mid text-xs pb-2">to</span>
        <BaseInput v-model="dateTo" type="date" compact aria-label="to date" />
      </template>

      <BaseButton v-if="hasActiveFilters" variant="ghost" size="sm" @click="emit('clearFilters')">
        clear filters
      </BaseButton>
    </div>
  </div>
</template>
