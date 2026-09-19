<script setup lang="ts">
import ExpenseCalculatorShell from "@/components/expense-calculator/ExpenseCalculatorShell.vue";
import type { ExchangeRates } from "@/types";

defineProps<{
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
}>();
</script>

<template>
  <ExpenseCalculatorShell
    tabpanel-id="expenses-tab-panel-converter"
    tabpanel-labelled-by="expenses-tab-tab-converter"
    :exchange-rates="exchangeRates"
    :rates-loading="ratesLoading"
  />
</template>
