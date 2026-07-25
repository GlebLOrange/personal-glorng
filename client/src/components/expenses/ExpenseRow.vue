<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates, Expense } from "@/types";
import { expenseSourceLabel } from "@/utils/expenseSource";

const props = withDefaults(
  defineProps<{
    expense: Expense;
    displayCurrency: CurrencyCode;
    exchangeRates: ExchangeRates | null;
    formatMoney: (amount: string | number, currency: string) => string;
    formatExpenseDate: (iso: string) => string;
    convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
    /** Compact table-row layout vs mobile card body. */
    layout?: "card" | "table";
  }>(),
  { layout: "card" },
);

const emit = defineEmits<{
  edit: [expense: Expense];
  delete: [id: number];
  duplicate: [expense: Expense];
}>();

function convertedLabel(): string | null {
  if (props.expense.currency === props.displayCurrency || !props.exchangeRates) return null;
  return props.formatMoney(
    props.convertAmount(
      props.expense.amount,
      props.expense.currency as CurrencyCode,
      props.displayCurrency,
    ),
    props.displayCurrency,
  );
}
</script>

<template>
  <tr
    v-if="layout === 'table'"
    class="border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50"
  >
    <td class="whitespace-nowrap px-3 py-2">
      {{ formatExpenseDate(expense.expense_date) }}
    </td>
    <td class="px-3 py-2 text-surface-mid">{{ expense.category ?? "—" }}</td>
    <td class="max-w-[220px] truncate px-3 py-2 font-sans">{{ expense.tool_name }}</td>
    <td class="whitespace-nowrap px-3 py-2 text-right">
      <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
      <div v-if="convertedLabel()" class="text-xs text-surface-mid">≈ {{ convertedLabel() }}</div>
    </td>
    <td class="px-3 py-2 font-sans text-xs text-surface-mid">
      {{ expenseSourceLabel(expense.source) }}
    </td>
    <td class="max-w-[200px] truncate px-3 py-2 font-sans text-surface-mid">
      {{ expense.notes ?? "—" }}
    </td>
    <td class="whitespace-nowrap px-3 py-2 text-right">
      <div class="inline-flex items-center justify-end gap-1">
        <BaseButton
          variant="ghost"
          size="sm"
          class="min-h-11"
          :aria-label="`Duplicate ${expense.tool_name || 'expense'}`"
          @click="emit('duplicate', expense)"
        >
          duplicate
        </BaseButton>
        <IconEditButton
          :aria-label="`Edit ${expense.tool_name || 'expense'}`"
          @click="emit('edit', expense)"
        />
        <IconCloseButton
          :aria-label="`Delete ${expense.tool_name || 'expense'}`"
          @click="emit('delete', expense.id)"
        />
      </div>
    </td>
  </tr>

  <div v-else class="flex flex-col gap-3">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="truncate text-sm font-semibold text-surface-light">{{ expense.tool_name }}</p>
        <p class="mt-1 text-xs text-surface-mid">
          {{ expense.category ?? "Uncategorized" }} ·
          {{ formatExpenseDate(expense.expense_date) }}
        </p>
      </div>
      <div class="shrink-0 text-right font-data text-sm text-surface-light">
        <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
        <div v-if="convertedLabel()" class="text-xs text-surface-mid">≈ {{ convertedLabel() }}</div>
      </div>
    </div>
    <div class="flex items-center justify-between gap-2">
      <span class="rounded bg-surface-border px-1.5 py-0.5 text-xs text-surface-mid">
        {{ expenseSourceLabel(expense.source) }}
      </span>
      <p v-if="expense.notes" class="min-w-0 truncate text-xs text-surface-mid">
        {{ expense.notes }}
      </p>
    </div>
    <div class="flex flex-wrap justify-end gap-1">
      <BaseButton
        variant="ghost"
        size="sm"
        class="min-h-11"
        :aria-label="`Duplicate ${expense.tool_name || 'expense'}`"
        @click="emit('duplicate', expense)"
      >
        duplicate
      </BaseButton>
      <IconEditButton
        :aria-label="`Edit ${expense.tool_name || 'expense'}`"
        @click="emit('edit', expense)"
      />
      <IconCloseButton
        :aria-label="`Delete ${expense.tool_name || 'expense'}`"
        @click="emit('delete', expense.id)"
      />
    </div>
  </div>
</template>
