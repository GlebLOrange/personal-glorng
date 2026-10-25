<script setup lang="ts">
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import ExpenseRow from "@/components/expenses/ExpenseRow.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { ADMIN_TH_CLASS } from "@/constants/adminDataTable";
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
    <AdminDataTable :table-label="`expenses for ${monthLabel}`">
      <template #header>
        <th :class="ADMIN_TH_CLASS" scope="col" :aria-sort="sortAriaSort('date')">
          <button type="button" :class="sortButtonClass" @click="emit('sort', 'date')">
            date{{ sortIndicator("date") }}
          </button>
        </th>
        <th :class="ADMIN_TH_CLASS" scope="col" :aria-sort="sortAriaSort('category')">
          <button type="button" :class="sortButtonClass" @click="emit('sort', 'category')">
            category{{ sortIndicator("category") }}
          </button>
        </th>
        <th :class="ADMIN_TH_CLASS" scope="col" :aria-sort="sortAriaSort('product')">
          <button type="button" :class="sortButtonClass" @click="emit('sort', 'product')">
            name{{ sortIndicator("product") }}
          </button>
        </th>
        <th :class="[ADMIN_TH_CLASS, 'text-right']" scope="col" :aria-sort="sortAriaSort('amount')">
          <button
            type="button"
            :class="[sortButtonClass, 'w-full justify-end text-right']"
            @click="emit('sort', 'amount')"
          >
            amount{{ sortIndicator("amount") }}
          </button>
        </th>
        <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
      </template>

      <ExpenseRow
        v-for="expense in expenses"
        :key="expense.id"
        :expense="expense"
        :display-currency="displayCurrency"
        :exchange-rates="exchangeRates"
        :format-money="formatMoney"
        :format-expense-date="formatExpenseDate"
        :convert-amount="convertAmount"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @duplicate="emit('duplicate', $event)"
      />
    </AdminDataTable>

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
