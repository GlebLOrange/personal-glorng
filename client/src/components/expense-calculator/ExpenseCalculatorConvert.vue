<script setup lang="ts">
import { computed, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
import {
  convertCurrency,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
  formatMoney,
  formatRate,
} from "@/composables/useExpenseCurrency";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates } from "@/types";

const props = defineProps<{
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
}>();

const amount = ref("100");
const fromCurrency = ref<CurrencyCode>("EUR");
const toCurrency = ref<CurrencyCode>(EXPENSE_DEFAULT_CURRENCY);
const converted = ref<string | null>(null);
const converting = ref(false);
const ratesUpdatedAt = ref<string | null>(null);

const selectClass =
  "w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm " +
  "focus:outline-none focus:border-accent-blue transition-colors h-[42px]";

const canConvert = computed(() => {
  const value = parseFloat(amount.value);
  return Number.isFinite(value) && value > 0;
});

let convertTimer: ReturnType<typeof setTimeout> | null = null;

async function runConvert(): Promise<void> {
  if (!canConvert.value) {
    converted.value = null;
    return;
  }
  converting.value = true;
  try {
    const result = await convertCurrency(
      parseFloat(amount.value),
      fromCurrency.value,
      toCurrency.value,
    );
    if (result) {
      converted.value = result.converted;
      ratesUpdatedAt.value = result.rates_updated_at;
    }
  } finally {
    converting.value = false;
  }
}

function scheduleConvert(): void {
  if (convertTimer) clearTimeout(convertTimer);
  convertTimer = setTimeout(() => {
    void runConvert();
  }, 300);
}

function swapCurrencies(): void {
  const prev = fromCurrency.value;
  fromCurrency.value = toCurrency.value;
  toCurrency.value = prev;
  converted.value = null;
  scheduleConvert();
}

watch([amount, fromCurrency, toCurrency], scheduleConvert, { immediate: true });
</script>

<template>
  <Card class="space-y-4">
    <p class="text-xs text-surface-mid">
      Convert between EUR, USD, PLN, and BYN using live rates. Results update as you type.
    </p>

    <BaseInput
      v-model="amount"
      label="Amount"
      type="number"
      step="0.01"
      min="0.01"
      placeholder="100.00"
    />

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="text-sm text-surface-mid block mb-1">From</label>
        <select v-model="fromCurrency" :class="selectClass">
          <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <div>
        <label class="text-sm text-surface-mid block mb-1">To</label>
        <select v-model="toCurrency" :class="selectClass">
          <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
    </div>

    <div class="flex gap-2">
      <BaseButton variant="ghost" size="sm" aria-label="Swap currencies" @click="swapCurrencies">
        Swap
      </BaseButton>
    </div>

    <div
      class="border-t border-surface-border pt-4"
      role="status"
      aria-live="polite"
      :aria-busy="converting || ratesLoading"
    >
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-2">Result</p>
      <p v-if="converted" class="text-3xl font-bold font-data text-surface-light">
        {{ formatMoney(converted, toCurrency) }}
      </p>
      <p v-else-if="converting || ratesLoading" class="text-3xl font-bold text-surface-border animate-pulse">
        —
      </p>
      <p v-else class="text-sm text-surface-mid">Enter an amount to convert.</p>
      <p v-if="converted && canConvert" class="text-sm text-surface-mid mt-1">
        {{ formatMoney(amount, fromCurrency) }} → {{ toCurrency }}
      </p>
      <p v-if="ratesUpdatedAt" class="text-[10px] text-surface-mid mt-2">
        Rates updated {{ ratesUpdatedAt }}
      </p>
    </div>

    <div
      v-if="props.exchangeRates"
      class="flex flex-wrap gap-3 text-xs text-surface-mid border-t border-surface-border pt-3"
    >
      <span class="text-surface-light">1 {{ EXPENSE_DEFAULT_CURRENCY }} =</span>
      <span v-for="c in EXPENSE_EXCHANGE_RATE_TARGETS" :key="c">
        {{ formatRate(props.exchangeRates.rates, EXPENSE_DEFAULT_CURRENCY, c) }} {{ c }}
      </span>
    </div>
  </Card>
</template>
