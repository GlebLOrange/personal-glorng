<script setup lang="ts">
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
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

/** Hide default web source; surface Telegram (and others) as secondary meta. */
function secondarySource(): string | null {
  if (props.expense.source === "web_admin") return null;
  return expenseSourceLabel(props.expense.source);
}
</script>

<template>
  <tr
    v-if="layout === 'table'"
    class="border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50"
  >
    <td class="whitespace-nowrap px-3 py-1.5 align-middle text-xs text-surface-mid">
      {{ formatExpenseDate(expense.expense_date) }}
    </td>
    <td class="px-3 py-1.5 align-middle">
      <span
        class="inline-flex max-w-[9rem] truncate rounded-md bg-surface-dark/60 px-1.5 py-0.5 text-xs text-surface-mid"
        :title="expense.category ?? 'Uncategorized'"
      >
        {{ expense.category ?? "—" }}
      </span>
    </td>
    <td class="max-w-[16rem] px-3 py-1.5 align-middle font-sans">
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
    </td>
    <td class="whitespace-nowrap px-3 py-1.5 align-middle text-right leading-tight">
      <div class="text-sm">{{ formatMoney(expense.amount, expense.currency) }}</div>
      <div v-if="convertedLabel()" class="text-[11px] text-surface-mid">
        ≈ {{ convertedLabel() }}
      </div>
    </td>
    <td class="whitespace-nowrap px-2 py-1.5 align-middle text-right">
      <div class="inline-flex items-center justify-end gap-0.5">
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

  <div v-else class="flex flex-col gap-2">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="truncate text-sm font-semibold text-surface-light">{{ expense.tool_name }}</p>
        <p class="mt-0.5 text-xs text-surface-mid">
          {{ expense.category ?? "Uncategorized" }} ·
          {{ formatExpenseDate(expense.expense_date) }}
          <span v-if="secondarySource()" class="text-surface-mid/80">
            · {{ secondarySource() }}
          </span>
        </p>
        <p v-if="expense.notes" class="mt-1 truncate text-xs text-surface-mid">
          {{ expense.notes }}
        </p>
      </div>
      <div class="shrink-0 text-right font-data text-sm leading-tight text-surface-light">
        <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
        <div v-if="convertedLabel()" class="text-xs text-surface-mid">≈ {{ convertedLabel() }}</div>
      </div>
    </div>
    <div class="flex flex-wrap items-center justify-end gap-0.5 border-t border-surface-border/40 pt-2">
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
  </div>
</template>
