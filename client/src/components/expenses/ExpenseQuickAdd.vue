<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";

defineProps<{
  loading: boolean;
  categoryOptions: string[];
  currencyLabel: string;
}>();

const category = defineModel<string>("category", { required: true });
const product = defineModel<string>("product", { required: true });
const price = defineModel<string>("price", { required: true });

const emit = defineEmits<{ submit: [] }>();

const selectClassCompact =
  "bg-surface-dark border border-surface-border rounded-lg px-2 py-1.5 text-surface-light font-mono text-xs " +
  "focus:outline-none focus:border-accent-blue transition-colors h-[34px] min-w-[7.5rem]";
</script>

<template>
  <BaseCard class="sticky top-4 z-10">
    <p class="text-xs text-surface-mid font-mono uppercase tracking-wider mb-3">Quick add</p>
    <form class="flex flex-col gap-2" @submit.prevent="emit('submit')">
      <div class="flex flex-col sm:flex-row sm:items-end gap-3">
        <div>
          <label
            class="text-[10px] text-surface-mid font-mono uppercase tracking-wider block mb-1"
          >
            Category
          </label>
          <select v-model="category" :class="selectClassCompact">
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div class="flex-1">
          <BaseInput v-model="product" label="Product" placeholder="Milk, fuel, rent..." />
        </div>
        <div class="sm:w-28">
          <BaseInput
            v-model="price"
            label="Price"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
          />
        </div>
        <BaseButton variant="primary" type="submit" :disabled="loading" class="sm:mb-0.5">
          {{ loading ? "Saving..." : "Save" }}
        </BaseButton>
      </div>
      <p class="text-[10px] text-surface-mid font-mono">
        {{ currencyLabel }} · today · full form for date, currency, notes
      </p>
    </form>
  </BaseCard>
</template>
