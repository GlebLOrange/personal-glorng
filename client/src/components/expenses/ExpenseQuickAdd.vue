<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
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
const expenseDate = defineModel<string>("expenseDate", { required: true });
const currency = defineModel<CurrencyCode>("currency", { required: true });
const smartTextOpen = defineModel<boolean>("smartTextOpen", { default: false });

const nameError = defineModel<string | null>("nameError", { default: null });
const amountError = defineModel<string | null>("amountError", { default: null });

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

function selectQuickAdd(): void {
  smartTextOpen.value = false;
}

function selectSmartText(): void {
  smartTextOpen.value = true;
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
  <div class="flex flex-col gap-3">
    <div
      class="flex flex-wrap gap-1.5"
      role="tablist"
      aria-label="add expense mode"
    >
      <ToolbarPillButton
        family="1xx"
        :selected="!smartTextOpen"
        aria-controls="expense-quick-add-panel"
        @click="selectQuickAdd"
      >
        quick add
      </ToolbarPillButton>
      <ToolbarPillButton
        family="1xx"
        :selected="smartTextOpen"
        aria-controls="expense-smart-text"
        @click="selectSmartText"
      >
        smart text
      </ToolbarPillButton>
    </div>

    <form
      v-show="!smartTextOpen"
      id="expense-quick-add-panel"
      role="tabpanel"
      class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(0,1.4fr)_minmax(7rem,9rem)_minmax(8rem,10rem)_minmax(9rem,11rem)_auto] lg:items-end"
      @submit.prevent="emit('submit')"
    >
      <BaseInput
        id="expense-quick-name"
        ref="productInputRef"
        v-model="product"
        label="goods or services?"
        list="expense-product-suggestions"
        placeholder="e.g. groceries"
        autocomplete="off"
        class="min-w-0 sm:col-span-2 lg:col-span-1"
        :error="nameError ?? undefined"
      />
      <BaseInput
        v-model="price"
        type="number"
        step="any"
        min="0.01"
        label="amount"
        placeholder="1"
        inputmode="decimal"
        class="min-w-0"
        :error="amountError ?? undefined"
      />
      <BaseSelect v-model="category" class="min-w-0 w-full" label="category">
        <option value="">—</option>
        <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
      </BaseSelect>
      <BaseInput
        v-model="expenseDate"
        type="date"
        label="date"
        class="min-w-0 w-full"
      />
      <ToolbarPillButton
        type="submit"
        family="2xx"
        class="w-full shrink-0 sm:w-auto lg:mb-0.5"
        :disabled="loading"
      >
        {{ loading ? "saving…" : "save" }}
      </ToolbarPillButton>
      <datalist id="expense-product-suggestions">
        <option v-for="name in productSuggestions" :key="name" :value="name" />
      </datalist>
    </form>

    <div
      v-show="smartTextOpen"
      id="expense-smart-text"
      role="tabpanel"
      class="flex flex-col gap-3"
    >
      <div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-end">
        <BaseInput
          ref="smartTextInputRef"
          v-model="smartText"
          label="smart text"
          placeholder="amount (important!) of goods or services?"
          hint="e.g. 20 coffee or 50 EUR lunch"
          autocomplete="off"
          class="min-w-0 flex-1"
        />
        <ToolbarPillButton
          family="2xx"
          class="w-full shrink-0 sm:mb-0.5 sm:w-auto"
          :disabled="loading || parsing || !canConfirmSmart"
          @click="confirmSmart"
        >
          {{ loading ? "saving…" : parsing ? "parsing…" : "save" }}
        </ToolbarPillButton>
      </div>
      <p v-if="parsing" class="text-xs text-surface-mid" role="status">parsing…</p>
      <p
        v-else-if="parsed && !parsed.valid && smartText.trim()"
        class="text-xs text-status-error"
        role="alert"
      >
        {{ parsed.error || "Could not parse expense" }}
      </p>
      <p
        v-else-if="previewLabel"
        class="rounded-md bg-surface-dark/60 px-3 py-2 text-sm text-surface-light"
        role="status"
      >
        <span class="text-xs text-surface-mid">Will add · </span>{{ previewLabel }}
      </p>
    </div>
  </div>
</template>
