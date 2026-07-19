<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
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

onUnmounted(() => {
  if (convertTimer) clearTimeout(convertTimer);
});

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
      type="number"
      step="0.01"
      min="0.01"
      placeholder="amount (100.00)"
      aria-label="amount (100.00)"
    />

    <div class="flex items-end gap-3">
      <BaseSelect v-model="fromCurrency" label="From" class="min-w-0 flex-1">
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
      <BaseButton
        variant="ghost"
        size="sm"
        class="mb-0.5 shrink-0 px-2"
        aria-label="swap currencies"
        @click="swapCurrencies"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="size-5"
          aria-hidden="true"
        >
          <path d="M8 8 4 12l4 4" />
          <path d="M4 12h16" />
          <path d="M16 8l4 4-4 4" />
        </svg>
      </BaseButton>
      <BaseSelect v-model="toCurrency" label="To" class="min-w-0 flex-1">
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
    </div>

    <div
      class="border-t border-surface-border pt-4"
      role="status"
      aria-live="polite"
      :aria-busy="converting || ratesLoading"
    >
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-2">result</p>
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
