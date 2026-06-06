<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
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

const monthInputClass =
  "bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5 text-surface-light text-sm focus:outline-none focus:border-accent-blue h-[34px]";
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap gap-2 items-center">
      <BaseButton
        v-for="preset in ['this_month', 'last_month', 'custom', 'range'] as MonthPreset[]"
        :key="preset"
        :variant="monthPreset === preset ? 'primary' : 'ghost'"
        size="sm"
        @click="emit('applyPreset', preset)"
      >
        {{
          preset === "this_month"
            ? "This month"
            : preset === "last_month"
              ? "Last month"
              : preset === "custom"
                ? "Month"
                : "Range"
        }}
      </BaseButton>

      <input
        v-if="dateFilterMode === 'month'"
        v-model="selectedMonth"
        type="month"
        :class="monthInputClass"
        @change="monthPreset = 'custom'"
      />

      <template v-else>
        <input v-model="dateFrom" type="date" :class="monthInputClass" aria-label="From date" />
        <span class="text-surface-mid text-xs">to</span>
        <input v-model="dateTo" type="date" :class="monthInputClass" aria-label="To date" />
      </template>

      <BaseButton v-if="hasActiveFilters" variant="ghost" size="sm" @click="emit('clearFilters')">
        Clear filters
      </BaseButton>
    </div>
  </div>
</template>
