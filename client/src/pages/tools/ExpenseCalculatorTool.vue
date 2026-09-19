<script setup lang="ts">
import ExpenseCalculatorShell from "@/components/expense-calculator/ExpenseCalculatorShell.vue";
import PageShell from "@/components/layout/PageShell.vue";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";

const { exchangeRates, ratesLoading } = useExpenseCalculator();
</script>

<template>
  <PageShell
    title="expense calculator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'expense' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <ExpenseCalculatorShell :exchange-rates="exchangeRates" :rates-loading="ratesLoading" />
  </PageShell>
</template>
