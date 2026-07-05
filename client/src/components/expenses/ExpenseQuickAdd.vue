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
        <p class="text-xs text-surface-mid uppercase tracking-wider">Quick add</p>
        <p class="text-xs text-surface-muted mt-1">Smart text first; fields stay ready below.</p>
      </div>
      <span class="text-xs text-surface-mid font-data">{{ currencyLabel }}</span>
    </div>

    <form class="flex flex-col gap-4" @submit.prevent="emit('submit')">
      <div class="flex flex-col md:flex-row md:items-end gap-3">
        <div class="flex-1">
          <label class="text-sm text-surface-mid block mb-1">Transaction</label>
          <input
            ref="smartInputRef"
            v-model="smartText"
            placeholder="89.50 biedronka or 12 lunch"
            :class="FIELD_INPUT_CLASS"
          />
        </div>
        <BaseButton variant="primary" type="submit" :disabled="loading" class="md:mb-0.5">
          {{ loading ? "Saving..." : "Save" }}
        </BaseButton>
      </div>

      <p v-if="parsing" class="text-xs text-surface-mid">Parsing...</p>
      <p v-else-if="parsedPreview" class="text-xs text-accent-blue font-data">
        {{ parsedPreview }}
      </p>
      <p v-else-if="smartError" class="text-xs text-red-400">{{ smartError }}</p>

      <div class="rounded-lg border border-surface-border bg-surface-dark/40 p-3">
        <div class="grid grid-cols-1 md:grid-cols-[180px_1fr_120px] md:items-end gap-3">
          <div>
            <label class="text-xs text-surface-mid uppercase tracking-wider block mb-1">
              Category
            </label>
            <select v-model="category" :class="SELECT_CLASS_COMPACT">
              <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="text-sm text-surface-mid block mb-1">Product</label>
            <input
              v-model="product"
              list="expense-product-suggestions"
              placeholder="Milk, fuel, rent..."
              :class="FIELD_INPUT_CLASS"
            />
            <datalist id="expense-product-suggestions">
              <option v-for="name in productSuggestions" :key="name" :value="name" />
            </datalist>
          </div>
          <div>
            <BaseInput
              v-model="price"
              label="Price"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
            />
          </div>
        </div>
        <p class="text-xs text-surface-mid mt-2">
          Today by default. Use Add for date, currency, and notes.
        </p>
      </div>
    </form>
  </Card>
</template>
