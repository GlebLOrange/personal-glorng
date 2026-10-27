<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";

import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import { Card } from "@/components/ui/card";
import { convertCurrency, EXPENSE_CURRENCIES, formatRate } from "@/composables/useExpenseCurrency";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates } from "@/types";
import { readConverterSnapshot, writeConverterSnapshot } from "@/utils/expenseConverterStorage";
import { formatDate } from "@/utils/format";

const props = defineProps<{
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
}>();

const restored = readConverterSnapshot();
const amount = ref(restored.amount);
const fromCurrency = ref<CurrencyCode>(restored.fromCurrency);
const toCurrency = ref<CurrencyCode>(restored.toCurrency);
const converted = ref<string | null>(null);
const converting = ref(false);
const ratesUpdatedAt = ref<string | null>(null);

/** Numbers only — currency sits in the adjacent select. */
function formatResult(value: string): string {
  const num = parseFloat(value);
  if (!Number.isFinite(num)) return "N/A";
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

const canConvert = computed(() => {
  const value = parseFloat(amount.value);
  return Number.isFinite(value) && value > 0;
});

const forwardRateLabel = computed(() => {
  if (!props.exchangeRates) return null;
  const rate = formatRate(props.exchangeRates.rates, fromCurrency.value, toCurrency.value);
  if (rate === "N/A") return null;
  return `1 ${fromCurrency.value} = ${rate} ${toCurrency.value}`;
});

const inverseRateLabel = computed(() => {
  if (!props.exchangeRates) return null;
  const rate = formatRate(props.exchangeRates.rates, toCurrency.value, fromCurrency.value);
  if (rate === "N/A") return null;
  return `1 ${toCurrency.value} = ${rate} ${fromCurrency.value}`;
});

/** Pair rates for FieldHelp tip (hidden behind ?). */
const ratesHelpText = computed(() => {
  const lines: string[] = [];
  if (ratesUpdatedAt.value) lines.push(formatDate(ratesUpdatedAt.value));
  if (forwardRateLabel.value) lines.push(forwardRateLabel.value);
  if (inverseRateLabel.value) lines.push(inverseRateLabel.value);
  return lines.join("\n");
});

let convertTimer: ReturnType<typeof setTimeout> | null = null;
let persistTimer: ReturnType<typeof setTimeout> | null = null;

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

function schedulePersist(): void {
  if (persistTimer) clearTimeout(persistTimer);
  persistTimer = setTimeout(() => {
    writeConverterSnapshot({
      amount: String(amount.value),
      fromCurrency: fromCurrency.value,
      toCurrency: toCurrency.value,
    });
  }, 300);
}

onUnmounted(() => {
  if (convertTimer) clearTimeout(convertTimer);
  if (persistTimer) clearTimeout(persistTimer);
});

function swapCurrencies(): void {
  const prev = fromCurrency.value;
  fromCurrency.value = toCurrency.value;
  toCurrency.value = prev;
  converted.value = null;
  scheduleConvert();
  schedulePersist();
}

watch(
  [amount, fromCurrency, toCurrency],
  () => {
    scheduleConvert();
    schedulePersist();
  },
  { immediate: true },
);
</script>

<template>
  <Card variant="compact" class="space-y-3">
    <div class="flex items-start justify-end gap-1">
      <p class="text-xs text-surface-mid text-right">
        Live EUR, USD, PLN, and BYN rates. Amount and pair stay on this device.
      </p>
      <FieldHelp v-if="ratesHelpText" align="end" :text="ratesHelpText" />
    </div>

    <div class="flex flex-wrap items-end justify-center gap-2">
      <BaseInput
        v-model="amount"
        type="number"
        step="0.01"
        min="0.01"
        label="amount"
        placeholder="100.00"
        inputmode="decimal"
        class="w-[3cm] max-w-[3cm] shrink-0"
      />
      <BaseSelect
        v-model="fromCurrency"
        label="from"
        class="w-[3cm] max-w-[3cm] shrink-0 [&_select]:!px-2 [&_select]:!pr-7"
      >
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
      <div class="flex shrink-0 items-center self-stretch pb-0.5">
        <IconActionButton action="create" aria-label="swap currencies" @click="swapCurrencies">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="size-4"
            aria-hidden="true"
          >
            <path d="M8 8 4 12l4 4" />
            <path d="M4 12h16" />
            <path d="M16 8l4 4-4 4" />
          </svg>
        </IconActionButton>
      </div>
      <BaseSelect
        v-model="toCurrency"
        label="to"
        class="w-[3cm] max-w-[3cm] shrink-0 [&_select]:!px-2 [&_select]:!pr-7"
      >
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
      <p
        class="min-w-0 shrink-0 self-center pb-0.5 font-data text-[40px] font-bold text-surface-mid"
        role="status"
        aria-live="polite"
        :aria-busy="converting || ratesLoading"
      >
        <span v-if="converted">{{ formatResult(converted) }}</span>
        <span v-else-if="converting || ratesLoading" class="animate-pulse">—</span>
        <span v-else>result</span>
      </p>
    </div>
  </Card>
</template>
