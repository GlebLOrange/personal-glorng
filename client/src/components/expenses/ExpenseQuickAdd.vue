<script setup lang="ts">
import { computed, nextTick, ref, toRef, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { FIELD_INPUT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";
import { useExpenseParse } from "@/composables/useExpenseParse";
import {
  EXPENSE_CURRENCIES,
  type CurrencyCode,
} from "@/composables/useExpenseFilters";
import { isoDateLocal } from "@/utils/dates";

const props = defineProps<{
  loading: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  currencyLabel: CurrencyCode;
}>();

const category = defineModel<string>("category", { required: true });
const product = defineModel<string>("product", { required: true });
const price = defineModel<string>("price", { required: true });
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

const productInputRef = ref<HTMLInputElement | null>(null);
const smartTextInputRef = ref<{ focus: () => void } | null>(null);
const smartText = ref("");

const currencyRef = toRef(props, "currencyLabel");
const { parsed, parsing } = useExpenseParse(smartText, currencyRef);

const previewLabel = computed(() => {
  const result = parsed.value;
  if (!result?.valid) return null;
  const parts = [
    result.amount && result.currency ? `${result.amount} ${result.currency}` : null,
    result.tool_name ?? null,
    result.category ?? null,
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

  const currency =
    result.currency && EXPENSE_CURRENCIES.includes(result.currency as CurrencyCode)
      ? (result.currency as CurrencyCode)
      : props.currencyLabel;

  emit("smartSubmit", {
    tool_name: result.tool_name!.trim(),
    amount: parseFloat(result.amount!).toFixed(2),
    currency,
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
  <Card>
    <div class="flex items-center justify-between gap-3 mb-3">
      <p class="text-xs text-surface-mid">quick add</p>
      <div class="flex items-center gap-2">
        <span class="text-xs text-surface-light font-data" title="Entries use this currency">
          currency: {{ currencyLabel }}
        </span>
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
    </div>

    <form
      class="grid grid-cols-1 gap-3 sm:grid-cols-[minmax(7rem,10rem)_1fr_minmax(5.5rem,7rem)_auto] sm:items-end"
      @submit.prevent="emit('submit')"
    >
      <select v-model="category" :class="SELECT_CLASS_COMPACT" aria-label="category">
        <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      <input
        ref="productInputRef"
        v-model="product"
        list="expense-product-suggestions"
        placeholder="qty and product name"
        aria-label="quantity and product name"
        :class="FIELD_INPUT_CLASS"
      />
      <BaseInput
        v-model="price"
        type="number"
        step="0.01"
        min="0.01"
        placeholder="price"
        aria-label="price"
      />
      <BaseButton variant="primary" type="submit" size="field" :disabled="loading">
        {{ loading ? "saving..." : "save" }}
      </BaseButton>
      <datalist id="expense-product-suggestions">
        <option v-for="name in productSuggestions" :key="name" :value="name" />
      </datalist>
    </form>

    <div
      v-if="smartTextOpen"
      id="expense-smart-text"
      class="mt-4 flex flex-col gap-3 border-t border-surface-border pt-4"
    >
      <BaseInput
        ref="smartTextInputRef"
        v-model="smartText"
        label="smart text"
        placeholder="20 coffee · 15 EUR lunch"
        aria-label="smart text expense"
      />
      <p v-if="parsing" class="text-xs text-surface-mid" role="status">parsing…</p>
      <p
        v-else-if="parsed && !parsed.valid && smartText.trim()"
        class="text-xs text-status-error"
        role="alert"
      >
        {{ parsed.error || "Could not parse expense" }}
      </p>
      <p v-else-if="previewLabel" class="text-xs text-surface-mid" role="status">
        {{ previewLabel }}
      </p>
      <BaseButton
        variant="primary"
        size="sm"
        class="self-start"
        :disabled="loading || parsing || !canConfirmSmart"
        @click="confirmSmart"
      >
        {{ loading ? "saving..." : "add parsed expense" }}
      </BaseButton>
    </div>
  </Card>
</template>
