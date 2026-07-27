<script setup lang="ts">
import ExpenseRow from "@/components/expenses/ExpenseRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSortKey } from "@/composables/useExpenseSort";
import type { ExchangeRates, Expense } from "@/types";

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
  "inline-flex h-10 items-center text-left text-xs tracking-wider transition-colors hover:text-surface-light";
</script>

<template>
  <AdminListSkeleton v-if="loading" :rows="5" label="Loading expenses" />

  <template v-else>
    <!-- Mobile cards -->
    <div class="flex flex-col gap-3 md:hidden">
      <Card v-for="expense in expenses" :key="expense.id" variant="compact">
        <ExpenseRow
          :expense="expense"
          layout="card"
          :display-currency="displayCurrency"
          :exchange-rates="exchangeRates"
          :format-money="formatMoney"
          :format-expense-date="formatExpenseDate"
          :convert-amount="convertAmount"
          @edit="emit('edit', $event)"
          @delete="emit('delete', $event)"
          @duplicate="emit('duplicate', $event)"
        />
      </Card>
    </div>

    <!-- Desktop table -->
    <div class="hidden min-w-0 overflow-x-auto rounded-lg border border-surface-border md:block">
      <table class="w-full min-w-0 font-data text-sm" :aria-label="`Expenses for ${monthLabel}`">
        <thead>
          <tr class="border-b border-surface-border bg-surface-card/80 text-left text-surface-mid">
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
              <span class="inline-flex h-10 items-center text-xs tracking-wider">source</span>
            </th>
            <th class="px-3">
              <span class="inline-flex h-10 items-center text-xs tracking-wider">notes</span>
            </th>
            <th class="px-3 text-right">
              <span class="inline-flex h-10 items-center text-xs tracking-wider">actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <ExpenseRow
            v-for="expense in expenses"
            :key="expense.id"
            :expense="expense"
            layout="table"
            :display-currency="displayCurrency"
            :exchange-rates="exchangeRates"
            :format-money="formatMoney"
            :format-expense-date="formatExpenseDate"
            :convert-amount="convertAmount"
            @edit="emit('edit', $event)"
            @delete="emit('delete', $event)"
            @duplicate="emit('duplicate', $event)"
          />
        </tbody>
      </table>
    </div>

    <EmptyState
      v-if="expenses.length === 0"
      :title="`No expenses in ${monthLabel || 'this period'}`"
      description="Add above, or use smart text (20 coffee). Telegram: /spend 20 coffee"
    >
      <template #action>
        <BaseButton variant="primary" size="sm" @click="emit('smartText')">
          use smart text
        </BaseButton>
      </template>
    </EmptyState>
  </template>
</template>
