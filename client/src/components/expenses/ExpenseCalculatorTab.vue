<script setup lang="ts">
import ExpenseCalculatorPanel from "@/components/expenses/ExpenseCalculatorPanel.vue";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";

/** Owns calculator rates so ExpensesTool does not boot them on other tabs. */
const { exchangeRates, ratesLoading } = useExpenseCalculator();
</script>

<template>
  <ExpenseCalculatorPanel :exchange-rates="exchangeRates" :rates-loading="ratesLoading" />
</template>
