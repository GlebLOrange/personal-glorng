<script setup lang="ts">
import ExpenseCalculatorConvert from "@/components/expense-calculator/ExpenseCalculatorConvert.vue";
import type { ExchangeRates } from "@/types";

defineProps<{
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
  /** When set, wraps content in a tabpanel for the ledger converter tab. */
  tabpanelId?: string;
  tabpanelLabelledBy?: string;
}>();
</script>

<template>
  <component
    :is="tabpanelId ? 'section' : 'div'"
    :id="tabpanelId"
    :role="tabpanelId ? 'tabpanel' : undefined"
    :aria-labelledby="tabpanelLabelledBy"
    :tabindex="tabpanelId ? 0 : undefined"
    class="flex min-w-0 flex-col gap-4 outline-none"
  >
    <ExpenseCalculatorConvert :exchange-rates="exchangeRates" :rates-loading="ratesLoading" />
  </component>
</template>
