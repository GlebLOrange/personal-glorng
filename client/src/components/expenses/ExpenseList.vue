<script setup lang="ts">
import ExpenseRow from "@/components/expenses/ExpenseRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
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
  "inline-flex h-8 items-center text-left text-xs tracking-wider transition-colors hover:text-surface-light";
</script>

<template>
  <AdminListSkeleton v-if="loading" :rows="5" label="Loading expenses" />

  <template v-else>
    <!-- Mobile rows: hairlines only — outer Card in transactions panel is the surface -->
    <div class="flex flex-col md:hidden">
      <div
        v-for="expense in expenses"
        :key="expense.id"
        class="border-b border-surface-border/60 py-2 last:border-b-0"
      >
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
      </div>
    </div>

    <!-- Desktop table: name carries notes + non-web source; actions are icon-only -->
    <div class="hidden min-w-0 overflow-x-auto rounded-lg border border-surface-border md:block">
      <table class="w-full min-w-0 font-data text-sm" :aria-label="`expenses for ${monthLabel}`">
        <thead class="sticky top-0 z-10">
          <tr class="border-b border-surface-border bg-surface-card text-left text-surface-mid">
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
                name{{ sortIndicator("product") }}
              </button>
            </th>
            <th class="px-3 text-right" :aria-sort="sortAriaSort('amount')">
              <button
                type="button"
                :class="[sortButtonClass, 'w-full justify-end text-right']"
                @click="emit('sort', 'amount')"
              >
                amount{{ sortIndicator("amount") }}
              </button>
            </th>
            <th class="w-px px-2 text-right">
              <span class="sr-only">actions</span>
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
      :title="`no expenses in ${monthLabel || 'this period'}`"
      description="add from the expenses tab, or smart text like 20 coffee"
    >
      <template #action>
        <BaseButton variant="primary" size="sm" @click="emit('smartText')">
          try smart text
        </BaseButton>
      </template>
    </EmptyState>
  </template>
</template>
