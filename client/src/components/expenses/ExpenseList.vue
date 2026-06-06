<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import type { ExchangeRates, ToolExpense } from "@/types";

import type { CurrencyCode } from "@/composables/useExpenseFilters";

defineProps<{
  expenses: ToolExpense[];
  loading: boolean;
  monthLabel: string;
  displayCurrency: CurrencyCode;
  exchangeRates: ExchangeRates | null;
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
}>();

const emit = defineEmits<{
  edit: [expense: ToolExpense];
  delete: [id: number];
}>();

const skeletonRows = 5;
</script>

<template>
  <!-- Loading skeleton -->
  <div v-if="loading" class="flex flex-col gap-3">
    <div
      v-for="n in skeletonRows"
      :key="n"
      class="rounded-lg border border-surface-border bg-surface-card p-4 animate-pulse"
    >
      <div class="h-3 w-24 bg-surface-border rounded mb-2" />
      <div class="h-4 w-40 bg-surface-border rounded mb-3" />
      <div class="h-3 w-20 bg-surface-border rounded" />
    </div>
  </div>

  <template v-else>
    <!-- Mobile cards -->
    <div class="flex flex-col gap-3 md:hidden">
      <div
        v-for="expense in expenses"
        :key="expense.id"
        class="rounded-lg border border-surface-border bg-surface-card p-4"
      >
        <div class="flex justify-between items-start gap-2 mb-1">
          <span class="text-xs font-mono text-surface-mid">
            {{ expense.category ?? "Uncategorized" }} · {{ formatExpenseDate(expense.expense_date) }}
          </span>
        </div>
        <p class="text-surface-light font-mono text-sm mb-2">{{ expense.tool_name }}</p>
        <div class="text-right font-mono text-sm text-surface-light mb-3">
          <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
          <div
            v-if="expense.currency !== displayCurrency && exchangeRates"
            class="text-[10px] text-surface-mid"
          >
            ≈
            {{
              formatMoney(
                convertAmount(
                  expense.amount,
                  expense.currency as CurrencyCode,
                  displayCurrency,
                ),
                displayCurrency,
              )
            }}
          </div>
        </div>
        <p v-if="expense.notes" class="text-xs text-surface-mid font-mono mb-3 truncate">
          {{ expense.notes }}
        </p>
        <div class="flex gap-2 justify-end">
          <BaseButton variant="ghost" size="sm" @click="emit('edit', expense)">Edit</BaseButton>
          <BaseButton variant="ghost" size="sm" @click="emit('delete', expense.id)">
            Delete
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Desktop table -->
    <div class="hidden md:block overflow-x-auto rounded-lg border border-surface-border">
      <table class="w-full text-sm font-mono">
        <thead>
          <tr class="text-left text-surface-mid border-b border-surface-border bg-surface-card">
            <th class="px-4 py-3">Date</th>
            <th class="px-4 py-3">Category</th>
            <th class="px-4 py-3">Product</th>
            <th class="px-4 py-3 text-right">Price</th>
            <th class="px-4 py-3">Notes</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="expense in expenses"
            :key="expense.id"
            class="border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50"
          >
            <td class="px-4 py-3 whitespace-nowrap">
              {{ formatExpenseDate(expense.expense_date) }}
            </td>
            <td class="px-4 py-3 text-surface-mid">{{ expense.category ?? "—" }}</td>
            <td class="px-4 py-3">{{ expense.tool_name }}</td>
            <td class="px-4 py-3 text-right whitespace-nowrap">
              <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
              <div
                v-if="expense.currency !== displayCurrency && exchangeRates"
                class="text-[10px] text-surface-mid"
              >
                ≈
                {{
                  formatMoney(
                    convertAmount(
                      expense.amount,
                      expense.currency as CurrencyCode,
                      displayCurrency,
                    ),
                    displayCurrency,
                  )
                }}
              </div>
            </td>
            <td class="px-4 py-3 text-surface-mid max-w-[200px] truncate">
              {{ expense.notes ?? "—" }}
            </td>
            <td class="px-4 py-3 text-right whitespace-nowrap">
              <BaseButton variant="ghost" size="sm" @click="emit('edit', expense)">
                Edit
              </BaseButton>
              <BaseButton variant="ghost" size="sm" @click="emit('delete', expense.id)">
                Delete
              </BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="expenses.length === 0" class="text-surface-mid text-sm text-center py-8 font-mono">
      No expenses in {{ monthLabel || "this period" }}.
      <span class="block mt-1 text-xs">Add one above, or log from Telegram: /spend 20 coffee</span>
    </p>
  </template>
</template>
