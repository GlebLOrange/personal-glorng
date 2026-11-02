<script setup lang="ts">
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates, Expense } from "@/types";
import { expenseSourceLabel } from "@/utils/expenseSource";

const props = defineProps<{
  expense: Expense;
  displayCurrency: CurrencyCode;
  exchangeRates: ExchangeRates | null;
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
}>();

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

/** Hide default web source; surface Telegram (and others) as secondary meta. */
function secondarySource(): string | null {
  if (props.expense.source === "web_admin") return null;
  return expenseSourceLabel(props.expense.source);
}
</script>

<template>
  <tr :class="ADMIN_TR_CLASS">
    <td :class="ADMIN_TD_MUTED_CLASS">
      {{ formatExpenseDate(expense.expense_date) }}
    </td>
    <td :class="ADMIN_TD_CLASS">
      <span
        class="inline-flex max-w-[9rem] truncate rounded-md bg-surface-dark/60 px-1.5 py-0.5 text-xs text-surface-mid"
        :title="expense.category ?? 'Uncategorized'"
      >
        {{ expense.category ?? "—" }}
      </span>
    </td>
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <p class="truncate text-sm text-surface-light" :title="expense.tool_name">
        {{ expense.tool_name }}
      </p>
      <p
        v-if="expense.notes || secondarySource()"
        class="mt-0.5 truncate text-xs text-surface-mid"
        :title="[expense.notes, secondarySource()].filter(Boolean).join(' · ')"
      >
        <span v-if="expense.notes">{{ expense.notes }}</span>
        <span v-if="expense.notes && secondarySource()"> · </span>
        <span v-if="secondarySource()">{{ secondarySource() }}</span>
      </p>
    </th>
    <td :class="[ADMIN_TD_CLASS, 'whitespace-nowrap text-right leading-tight']">
      <div class="text-sm">{{ formatMoney(expense.amount, expense.currency) }}</div>
      <div v-if="convertedLabel()" class="text-xs text-surface-mid">≈ {{ convertedLabel() }}</div>
    </td>
    <td :class="ADMIN_TD_ACTIONS_CLASS">
      <div :class="ADMIN_ACTIONS_CLASS">
        <IconCopyButton
          :aria-label="`duplicate ${expense.tool_name || 'expense'}`"
          :quiet="false"
          @click="emit('duplicate', expense)"
        />
        <IconEditButton
          :aria-label="`edit ${expense.tool_name || 'expense'}`"
          @click="emit('edit', expense)"
        />
        <IconCloseButton
          :aria-label="`delete ${expense.tool_name || 'expense'}`"
          @click="emit('delete', expense.id)"
        />
      </div>
    </td>
  </tr>
</template>
