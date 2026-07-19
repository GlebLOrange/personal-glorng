<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { SELECT_CLASS_COMPACT } from "@/constants/formClasses";
import type { ExpenseCalculatorLineItem } from "@/composables/useExpenseCalculator";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import { EXPENSE_CURRENCIES } from "@/composables/useExpenseCurrency";

defineProps<{
  lineItems: ExpenseCalculatorLineItem[];
  displayCurrency: CurrencyCode;
  sumTotal: number;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  add: [];
  remove: [id: string];
  applyToBudget: [];
}>();

function onAmountEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter") return;
  event.preventDefault();
  emit("add");
  requestAnimationFrame(() => {
    const inputs = document.querySelectorAll<HTMLInputElement>("[data-line-label]");
    inputs[index + 1]?.focus();
  });
}

function onAddItem(): void {
  emit("add");
  requestAnimationFrame(() => {
    const inputs = document.querySelectorAll<HTMLInputElement>("[data-line-label]");
    inputs[inputs.length - 1]?.focus();
  });
}
</script>

<template>
  <div class="flex flex-col gap-4 pb-24 md:pb-0">
    <Card class="space-y-4">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-xs text-surface-mid uppercase tracking-wider">Itemized sum</p>
          <p class="text-xs text-surface-muted mt-1">Add line items and see a running total.</p>
        </div>
        <BaseButton variant="primary" size="sm" @click="onAddItem">+ add item</BaseButton>
      </div>

      <div v-if="lineItems.length === 0" class="text-center py-8">
        <p class="text-sm text-surface-mid">no items yet.</p>
        <BaseButton class="mt-3" variant="primary" @click="onAddItem">add your first item</BaseButton>
      </div>

      <ul v-else role="list" class="space-y-3">
        <li
          v-for="(item, index) in lineItems"
          :key="item.id"
          class="grid grid-cols-1 md:grid-cols-[1fr_120px_100px_auto] gap-3 items-end"
        >
          <BaseInput
            v-model="item.label"
            placeholder="label (coffee, taxi...)"
            aria-label="label (coffee, taxi...)"
            data-line-label
          />
          <BaseInput
            v-model="item.amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="amount (0.00)"
            aria-label="amount (0.00)"
            @keydown="onAmountEnter($event, index)"
          />
          <select v-model="item.currency" :class="SELECT_CLASS_COMPACT" aria-label="currency">
              <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
            </select>
          <BaseButton
            variant="ghost"
            danger
            size="sm"
            :aria-label="`Remove ${item.label || 'item'}`"
            class="md:mb-0.5"
            @click="emit('remove', item.id)"
          >
            remove
          </BaseButton>
        </li>
      </ul>

      <div class="flex flex-wrap gap-2 border-t border-surface-border pt-4">
        <BaseButton variant="ghost" size="sm" :disabled="sumTotal <= 0" @click="emit('applyToBudget')">
          use total as budget spent
        </BaseButton>
      </div>
    </Card>

    <div
      class="fixed bottom-0 inset-x-0 z-10 border-t border-surface-border bg-surface-card/95 backdrop-blur px-4 py-3 md:static md:border-0 md:bg-transparent md:backdrop-blur-none md:p-0"
      role="status"
      aria-live="polite"
    >
      <Card variant="compact" class="flex items-center justify-between gap-3">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Total</p>
        <p class="text-2xl font-bold font-data text-surface-light">
          {{ formatMoney(sumTotal, displayCurrency) }}
        </p>
      </Card>
    </div>
  </div>
</template>
