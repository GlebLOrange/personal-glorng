<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { FIELD_INPUT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";
import type { ExpenseParseResult } from "@/types";

const props = defineProps<{
  loading: boolean;
  parsing: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  currencyLabel: string;
  parsed: ExpenseParseResult | null;
}>();

const smartText = defineModel<string>("smartText", { required: true });
const category = defineModel<string>("category", { required: true });
const product = defineModel<string>("product", { required: true });
const price = defineModel<string>("price", { required: true });

const emit = defineEmits<{ submit: [] }>();

const parsedPreview = computed(() => {
  if (!props.parsed?.valid) return null;
  const parts = [
    props.parsed.currency,
    props.parsed.amount,
    props.parsed.category,
    props.parsed.tool_name,
    "today",
  ].filter(Boolean);
  return parts.join(" · ");
});

const smartError = computed(() => {
  if (!smartText.value.trim() || props.parsing) return null;
  if (props.parsed?.valid) return null;
  return props.parsed?.error ?? null;
});

const smartInputRef = ref<HTMLInputElement | null>(null);

function focusEntry(): void {
  smartInputRef.value?.focus();
}

defineExpose({ focusEntry });
</script>

<template>
  <Card>
    <div class="flex items-center justify-between gap-3 mb-3">
      <div>
        <p class="text-xs text-surface-mid">quick add</p>
        <p class="text-xs text-surface-muted mt-1">smart text first; fields stay ready below.</p>
      </div>
      <span class="text-xs text-surface-mid font-data">{{ currencyLabel }}</span>
    </div>

    <form class="flex flex-col gap-4" @submit.prevent="emit('submit')">
      <div class="flex flex-col md:flex-row md:items-end gap-3">
        <div class="flex-1">
          <input
            ref="smartInputRef"
            v-model="smartText"
            placeholder="transaction (89.50 biedronka or 12 lunch)"
            aria-label="transaction (89.50 biedronka or 12 lunch)"
            :class="FIELD_INPUT_CLASS"
          />
        </div>
        <BaseButton variant="primary" type="submit" size="field" :disabled="loading">
          {{ loading ? "saving..." : "save" }}
        </BaseButton>
      </div>

      <p v-if="parsing" class="text-xs text-surface-mid">parsing...</p>
      <p v-else-if="parsedPreview" class="text-xs text-accent-blue font-data">
        {{ parsedPreview }}
      </p>
      <p v-else-if="smartError" class="text-xs text-status-error">{{ smartError }}</p>

      <div class="rounded-lg border border-surface-border bg-surface-dark/40 p-3">
        <div class="grid grid-cols-1 md:grid-cols-[180px_1fr_120px] md:items-end gap-3">
          <select v-model="category" :class="SELECT_CLASS_COMPACT" aria-label="category">
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <input
            v-model="product"
            list="expense-product-suggestions"
            placeholder="product (milk, fuel, rent...)"
            aria-label="product (milk, fuel, rent...)"
            :class="FIELD_INPUT_CLASS"
          />
          <BaseInput
            v-model="price"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="price (0.00)"
            aria-label="price (0.00)"
          />
        </div>
        <datalist id="expense-product-suggestions">
          <option v-for="name in productSuggestions" :key="name" :value="name" />
        </datalist>
        <p class="text-xs text-surface-mid mt-2">
          today by default. use add for date, currency, and notes.
        </p>
      </div>
    </form>
  </Card>
</template>
