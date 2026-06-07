<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import {
  crossRate,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
  type CurrencyCode,
} from "@/composables/useExpenseFilters";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import type { ExchangeRates } from "@/types";

interface ConvertResult {
  amount: string;
  from_currency: CurrencyCode;
  to_currency: CurrencyCode;
  converted: string;
  rates_updated_at: string | null;
}

const props = defineProps<{
  exchangeRates: ExchangeRates | null;
}>();

const amount = ref("100");
const fromCurrency = ref<CurrencyCode>("EUR");
const toCurrency = ref<CurrencyCode>(EXPENSE_DEFAULT_CURRENCY);
const result = ref<ConvertResult | null>(null);
const { loading, run } = useApiAction();

const canConvert = computed(() => {
  const value = parseFloat(amount.value);
  return Number.isFinite(value) && value > 0 && fromCurrency.value && toCurrency.value;
});

function formatMoney(value: string | number, currency: string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(num);
}

async function convert(): Promise<void> {
  if (!canConvert.value) return;
  const data = await run(
    async () => {
      const response = await api.post<ConvertResult>("/tools/expenses/convert", {
        amount: parseFloat(amount.value).toFixed(2),
        from_currency: fromCurrency.value,
        to_currency: toCurrency.value,
      });
      return response.data;
    },
    { errorMessage: "Conversion failed" },
  );
  if (data) result.value = data;
}

function swapCurrencies(): void {
  const prevFrom = fromCurrency.value;
  fromCurrency.value = toCurrency.value;
  toCurrency.value = prevFrom;
  result.value = null;
}

const selectClass =
  "w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm " +
  "focus:outline-none focus:border-accent-blue transition-colors h-[42px]";
</script>

<template>
  <BaseCard class="space-y-4">
    <p class="text-xs text-surface-mid">
      Convert between EUR, USD, PLN, and BYN using live rates.
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
      <BaseButton variant="primary" :disabled="!canConvert || loading" @click="convert">
        {{ loading ? "Converting..." : "Convert" }}
      </BaseButton>
      <BaseButton variant="ghost" size="sm" aria-label="Swap currencies" @click="swapCurrencies">
        <svg
          class="w-4 h-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M8 3 4 7l4 4" />
          <path d="M4 7h16" />
          <path d="m16 21 4-4-4-4" />
          <path d="M20 17H4" />
        </svg>
      </BaseButton>
    </div>

    <div v-if="result" class="border-t border-surface-border pt-4">
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-2">Result</p>
      <p class="text-2xl font-bold text-surface-light">
        {{ formatMoney(result.converted, result.to_currency) }}
      </p>
      <p class="text-sm text-surface-mid mt-1">
        {{ formatMoney(result.amount, result.from_currency) }}
        →
        {{ result.to_currency }}
      </p>
      <p v-if="result.rates_updated_at" class="text-[10px] text-surface-mid mt-2">
        Rates updated {{ result.rates_updated_at }}
      </p>
    </div>

    <div
      v-if="props.exchangeRates"
      class="flex flex-wrap gap-3 text-xs text-surface-mid border-t border-surface-border pt-3"
    >
      <span class="text-surface-light">1 {{ EXPENSE_DEFAULT_CURRENCY }} =</span>
      <span v-for="c in EXPENSE_EXCHANGE_RATE_TARGETS" :key="c">
        {{ crossRate(props.exchangeRates.rates, EXPENSE_DEFAULT_CURRENCY, c).toFixed(4) }} {{ c }}
      </span>
    </div>
  </BaseCard>
</template>
