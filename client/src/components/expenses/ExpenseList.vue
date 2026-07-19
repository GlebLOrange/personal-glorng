<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import type { ExchangeRates, Expense } from "@/types";
import { expenseSourceLabel } from "@/utils/expenseSource";

import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSortKey } from "@/composables/useExpenseSort";

defineProps<{
  expenses: Expense[];
  loading: boolean;
  monthLabel: string;
  displayCurrency: CurrencyCode;
  exchangeRates: ExchangeRates | null;
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
  sortIndicator: (key: ExpenseSortKey) => string;
  sortAriaSort: (key: ExpenseSortKey) => "ascending" | "descending" | "none";
}>();

const emit = defineEmits<{
  edit: [expense: Expense];
  delete: [id: number];
  duplicate: [expense: Expense];
  sort: [key: ExpenseSortKey];
  smartText: [];
}>();

const sortButtonClass =
  "inline-flex h-11 items-center text-left hover:text-surface-light transition-colors tracking-wider text-xs";

const skeletonRows = 5;
</script>

<template>
  <!-- Loading skeleton -->
  <div v-if="loading" class="flex flex-col gap-2" aria-busy="true" aria-label="Loading expenses">
    <Card v-for="n in skeletonRows" :key="n" variant="compact" class="animate-pulse">
      <div class="h-3 w-24 bg-surface-border rounded mb-2" />
      <div class="h-4 w-40 bg-surface-border rounded mb-3" />
      <div class="h-3 w-20 bg-surface-border rounded" />
    </Card>
  </div>

  <template v-else>
    <!-- Mobile cards -->
    <div class="flex flex-col gap-3 md:hidden">
      <Card
        v-for="expense in expenses"
        :key="expense.id"
        variant="compact"
        interactive
        hoverable
        role="button"
        tabindex="0"
        class="cursor-pointer"
        @click="emit('edit', expense)"
        @keydown.enter.prevent="emit('edit', expense)"
      >
        <div class="flex justify-between items-start gap-3">
          <div class="min-w-0">
            <p class="text-surface-light text-sm font-semibold truncate">{{ expense.tool_name }}</p>
            <p class="text-xs text-surface-mid mt-1">
              {{ expense.category ?? "Uncategorized" }} ·
              {{ formatExpenseDate(expense.expense_date) }}
            </p>
          </div>
          <div class="text-right text-sm text-surface-light font-data shrink-0">
            <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
            <div
              v-if="expense.currency !== displayCurrency && exchangeRates"
              class="text-xs text-surface-mid"
            >
              ≈
              {{
                formatMoney(
                  convertAmount(expense.amount, expense.currency as CurrencyCode, displayCurrency),
                  displayCurrency,
                )
              }}
            </div>
          </div>
        </div>
        <div class="flex justify-between items-center mt-3 gap-2">
          <span class="text-xs px-1.5 py-0.5 rounded bg-surface-border text-surface-mid">
            {{ expenseSourceLabel(expense.source) }}
          </span>
          <p v-if="expense.notes" class="text-xs text-surface-mid truncate min-w-0">
            {{ expense.notes }}
          </p>
        </div>
        <div class="flex gap-2 justify-end flex-wrap mt-3" @click.stop @keydown.stop>
          <BaseButton
            variant="ghost"
            size="sm"
            :aria-label="`Duplicate ${expense.tool_name || 'expense'}`"
            @click="emit('duplicate', expense)"
          >
            duplicate
          </BaseButton>
          <BaseButton variant="ghost" size="sm" @click="emit('edit', expense)">edit</BaseButton>
          <BaseButton variant="ghost" danger size="sm" @click="emit('delete', expense.id)">
            delete
          </BaseButton>
        </div>
      </Card>
    </div>

    <!-- Desktop table -->
    <div class="hidden md:block overflow-x-auto rounded-lg border border-surface-border">
      <table class="w-full text-sm font-data" :aria-label="`Expenses for ${monthLabel}`">
        <thead>
          <tr class="text-left text-surface-mid border-b border-surface-border bg-surface-card/80">
            <th class="px-3" :aria-sort="sortAriaSort('date')">
              <button type="button" :class="sortButtonClass" @click="emit('sort', 'date')">
                date{{ sortIndicator("date") }}
              </button>
            </th>
            <th class="px-3" :aria-sort="sortAriaSort('category')">
              <button type="button" :class="sortButtonClass" @click="emit('sort', 'category')">
                category{{ sortIndicator("category") }}
              </button>
            </th>
            <th class="px-3" :aria-sort="sortAriaSort('product')">
              <button type="button" :class="sortButtonClass" @click="emit('sort', 'product')">
                product{{ sortIndicator("product") }}
              </button>
            </th>
            <th class="px-3 text-right" :aria-sort="sortAriaSort('amount')">
              <button
                type="button"
                :class="[sortButtonClass, 'w-full justify-end text-right']"
                @click="emit('sort', 'amount')"
              >
                price{{ sortIndicator("amount") }}
              </button>
            </th>
            <th class="px-3">
              <span class="inline-flex h-11 items-center text-xs tracking-wider">source</span>
            </th>
            <th class="px-3">
              <span class="inline-flex h-11 items-center text-xs tracking-wider">notes</span>
            </th>
            <th class="px-3 text-right">
              <span class="inline-flex h-11 items-center text-xs tracking-wider">actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="expense in expenses"
            :key="expense.id"
            class="border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50 cursor-pointer"
            role="button"
            tabindex="0"
            @click="emit('edit', expense)"
            @keydown.enter.prevent="emit('edit', expense)"
          >
            <td class="px-3 py-2 whitespace-nowrap">
              {{ formatExpenseDate(expense.expense_date) }}
            </td>
            <td class="px-3 py-2 text-surface-mid">{{ expense.category ?? "—" }}</td>
            <td class="px-3 py-2 font-sans max-w-[220px] truncate">{{ expense.tool_name }}</td>
            <td class="px-3 py-2 text-right whitespace-nowrap">
              <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
              <div
                v-if="expense.currency !== displayCurrency && exchangeRates"
                class="text-xs text-surface-mid"
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
            <td class="px-3 py-2 text-surface-mid text-xs font-sans">
              {{ expenseSourceLabel(expense.source) }}
            </td>
            <td class="px-3 py-2 text-surface-mid max-w-[200px] truncate font-sans">
              {{ expense.notes ?? "—" }}
            </td>
            <td class="px-3 py-2 text-right whitespace-nowrap" @click.stop @keydown.stop>
              <BaseButton
                variant="ghost"
                size="sm"
                :aria-label="`Duplicate ${expense.tool_name || 'expense'}`"
                @click="emit('duplicate', expense)"
              >
                duplicate
              </BaseButton>
              <BaseButton variant="ghost" size="sm" @click="emit('edit', expense)">
                edit
              </BaseButton>
              <BaseButton variant="ghost" danger size="sm" @click="emit('delete', expense.id)">
                delete
              </BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EmptyState
      v-if="expenses.length === 0"
      :title="`No expenses in ${monthLabel || 'this period'}`"
      description="Add one above, paste smart text, or log from Telegram: /spend 20 coffee"
    >
      <template #action>
        <BaseButton variant="primary" size="sm" @click="emit('smartText')">
          paste smart text
        </BaseButton>
      </template>
    </EmptyState>
  </template>
</template>
