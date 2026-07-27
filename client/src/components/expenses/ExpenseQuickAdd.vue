<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { useExpenseParse } from "@/composables/useExpenseParse";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";
import { isoDateLocal } from "@/utils/dates";

const props = defineProps<{
  loading: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
}>();

const category = defineModel<string>("category", { required: true });
const product = defineModel<string>("product", { required: true });
const price = defineModel<string>("price", { required: true });
const currency = defineModel<CurrencyCode>("currency", { required: true });
const smartTextOpen = defineModel<boolean>("smartTextOpen", { default: false });

const emit = defineEmits<{
  submit: [];
  smartSubmit: [
    payload: {
      tool_name: string;
      amount: string;
      currency: CurrencyCode;
      expense_date: string;
      category: string | null;
    },
  ];
}>();

const productInputRef = ref<{ focus: () => void } | null>(null);
const smartTextInputRef = ref<{ focus: () => void } | null>(null);
const smartText = ref("");

const { parsed, parsing } = useExpenseParse(smartText, currency);

const previewLabel = computed(() => {
  const result = parsed.value;
  if (!result?.valid) return null;
  const parts = [
    result.amount && result.currency ? `${result.amount} ${result.currency}` : null,
    result.category ?? null,
    result.tool_name ?? null,
    result.expense_date ?? null,
  ].filter(Boolean);
  return parts.join(" · ");
});

const canConfirmSmart = computed(() => {
  if (parsing.value) return false;
  const result = parsed.value;
  if (!result?.valid || !result.amount || !result.tool_name) return false;
  const amount = parseFloat(result.amount);
  return Number.isFinite(amount) && amount > 0;
});

function focusEntry(): void {
  productInputRef.value?.focus();
}

async function focusSmartText(): Promise<void> {
  smartTextOpen.value = true;
  await nextTick();
  smartTextInputRef.value?.focus();
}

async function confirmSmart(): Promise<void> {
  if (parsing.value || props.loading) return;
  const result = parsed.value;
  if (!result?.valid || !canConfirmSmart.value) return;

  const resolvedCurrency =
    result.currency && EXPENSE_CURRENCIES.includes(result.currency as CurrencyCode)
      ? (result.currency as CurrencyCode)
      : currency.value;

  emit("smartSubmit", {
    tool_name: result.tool_name!.trim(),
    amount: parseFloat(result.amount!).toFixed(2),
    currency: resolvedCurrency,
    expense_date: result.expense_date || isoDateLocal(),
    category: result.category?.trim() || null,
  });
}

function clearSmartText(): void {
  smartText.value = "";
}

watch(smartTextOpen, (open) => {
  if (!open) smartText.value = "";
});

defineExpose({ focusEntry, focusSmartText, clearSmartText });
</script>

<template>
  <Card variant="compact" class="flex flex-col gap-3">
    <div class="flex flex-wrap items-end justify-between gap-2">
      <p class="text-xs font-medium text-surface-mid">quick add</p>
      <BaseButton
        variant="ghost"
        size="sm"
        :aria-expanded="smartTextOpen"
        aria-controls="expense-smart-text"
        @click="smartTextOpen = !smartTextOpen"
      >
        {{ smartTextOpen ? "hide smart text" : "smart text" }}
      </BaseButton>
    </div>

    <form
      class="grid grid-cols-1 gap-3 sm:grid-cols-[minmax(8rem,12rem)_1fr_minmax(5.5rem,7rem)_auto] sm:items-end"
      @submit.prevent="emit('submit')"
    >
      <BaseSelect v-model="category" class="w-full" label="category">
        <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
      </BaseSelect>
      <BaseInput
        id="expense-quick-product"
        ref="productInputRef"
        v-model="product"
        label="product"
        list="expense-product-suggestions"
        placeholder="qty and product name"
        autocomplete="off"
      />
      <BaseInput
        v-model="price"
        type="number"
        step="0.01"
        min="0.01"
        label="price"
        placeholder="0.00"
        inputmode="decimal"
      />
      <BaseButton variant="success" type="submit" :disabled="loading">
        {{ loading ? "saving…" : "save" }}
      </BaseButton>
      <datalist id="expense-product-suggestions">
        <option v-for="name in productSuggestions" :key="name" :value="name" />
      </datalist>
    </form>

    <div
      v-if="smartTextOpen"
      id="expense-smart-text"
      class="flex flex-col gap-3 border-t border-surface-border pt-3"
    >
      <BaseInput
        ref="smartTextInputRef"
        v-model="smartText"
        label="smart text"
        placeholder="20 coffee"
        hint="amount first — 20 coffee or 50 EUR lunch"
        autocomplete="off"
      />
      <p v-if="parsing" class="text-xs text-surface-mid" role="status">parsing…</p>
      <p
        v-else-if="parsed && !parsed.valid && smartText.trim()"
        class="text-xs text-status-error"
        role="alert"
      >
        {{ parsed.error || "Could not parse expense" }}
      </p>
      <p v-else-if="previewLabel" class="rounded-md bg-surface-dark/60 px-3 py-2 text-sm text-surface-light" role="status">
        <span class="text-xs text-surface-mid">Will add · </span>{{ previewLabel }}
      </p>
      <BaseButton
        variant="success"
        size="sm"
        class="self-start"
        :disabled="loading || parsing || !canConfirmSmart"
        @click="confirmSmart"
      >
        {{ loading ? "saving…" : parsing ? "parsing…" : "+ parsed expense" }}
      </BaseButton>
    </div>
  </Card>
</template>
