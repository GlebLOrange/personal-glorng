<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { FIELD_INPUT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";

defineProps<{
  loading: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  currencyLabel: string;
}>();

const category = defineModel<string>("category", { required: true });
const product = defineModel<string>("product", { required: true });
const price = defineModel<string>("price", { required: true });

const emit = defineEmits<{ submit: [] }>();

const productInputRef = ref<HTMLInputElement | null>(null);

function focusEntry(): void {
  productInputRef.value?.focus();
}

defineExpose({ focusEntry });
</script>

<template>
  <Card>
    <div class="flex items-center justify-between gap-3 mb-3">
      <p class="text-xs text-surface-mid">quick add</p>
      <span class="text-xs text-surface-mid font-data">{{ currencyLabel }}</span>
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
  </Card>
</template>
