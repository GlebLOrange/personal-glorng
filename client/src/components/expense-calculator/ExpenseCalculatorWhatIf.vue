<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { SELECT_CLASS_COMPACT } from "@/constants/formClasses";
import { EXPENSE_CURRENCIES } from "@/composables/useExpenseCurrency";
import type { CurrencyCode } from "@/composables/useExpenseFilters";

interface BudgetOption {
  id: string;
  name: string;
}

const props = defineProps<{
  budgetOptions: BudgetOption[];
  displayCurrency: CurrencyCode;
  projection: {
    amount: number;
    budget: number;
    spent: number;
    projected: number;
    remaining: number;
    overBudget: boolean;
    overBy: number;
    withinBudget: boolean;
  };
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  goToBudget: [];
}>();

const categoryId = defineModel<string | "overall">("whatIfCategoryId", { required: true });
const amount = defineModel<string>("whatIfAmount", { required: true });
const currency = defineModel<CurrencyCode>("whatIfCurrency", { required: true });
</script>

<template>
  <Card class="space-y-4">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <p class="text-xs text-surface-mid">
        Simulate a purchase against your budget rows. Set categories on the Budget tab first.
      </p>
      <BaseButton
        v-if="props.budgetOptions.length === 0"
        variant="ghost"
        size="sm"
        class="self-start"
        @click="emit('goToBudget')"
      >
        go to budget
      </BaseButton>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <select v-model="categoryId" :class="SELECT_CLASS_COMPACT" aria-label="category">
        <option value="overall">overall</option>
        <option v-for="option in budgetOptions" :key="option.id" :value="option.id">
          {{ option.name }}
        </option>
      </select>
      <div class="grid grid-cols-[1fr_100px] gap-2 items-end">
        <BaseInput
          v-model="amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="purchase amount"
          aria-label="purchase amount"
        />
        <select v-model="currency" :class="SELECT_CLASS_COMPACT" aria-label="currency">
          <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
    </div>

    <div
      class="border-t border-surface-border pt-4 space-y-3"
      role="status"
      aria-live="polite"
    >
      <div class="flex items-center justify-between gap-3">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Projection</p>
        <StatusBadge
          :label="projection.overBudget ? 'over budget' : 'within budget'"
          :class-name="
            projection.overBudget
              ? 'border-status-error text-status-error'
              : 'border-status-success text-status-success'
          "
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <p class="text-xs text-surface-mid">Projected spent</p>
          <p class="text-xl font-bold font-data text-surface-light">
            {{ formatMoney(projection.projected, displayCurrency) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-surface-mid">Remaining</p>
          <p
            class="text-xl font-bold font-data"
            :class="projection.overBudget ? 'text-status-error' : 'text-accent-blue'"
          >
            {{ formatMoney(projection.remaining, displayCurrency) }}
          </p>
        </div>
        <div v-if="projection.overBudget">
          <p class="text-xs text-surface-mid">Over by</p>
          <p class="text-xl font-bold font-data text-status-error">
            {{ formatMoney(projection.overBy, displayCurrency) }}
          </p>
        </div>
      </div>
    </div>
  </Card>
</template>
