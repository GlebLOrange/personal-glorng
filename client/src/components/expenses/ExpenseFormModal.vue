<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";

defineProps<{
  open: boolean;
  loading: boolean;
  title: string;
  categoryOptions: string[];
}>();

const category = defineModel<string>("category", { required: true });
const toolName = defineModel<string>("toolName", { required: true });
const amount = defineModel<string>("amount", { required: true });
const currency = defineModel<CurrencyCode>("currency", { required: true });
const expenseDate = defineModel<string>("expenseDate", { required: true });
const notes = defineModel<string>("notes", { required: true });

const emit = defineEmits<{ submit: []; close: [] }>();

const selectClass =
  "bg-surface-dark border border-surface-border rounded-lg px-3 py-2 text-surface-light text-sm " +
  "focus:outline-none focus:border-accent-blue transition-colors h-[42px]";
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/60"
        @click.self="emit('close')"
      >
        <div
          class="bg-surface-card border border-surface-border rounded-lg p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto"
        >
          <h2 class="text-lg font-bold text-surface-light mb-6">
            <span class="accent-gradient">€ {{ title }}</span>
          </h2>

          <form class="space-y-4" @submit.prevent="emit('submit')">
            <div>
              <label class="text-sm text-surface-mid block mb-1">Category</label>
              <select v-model="category" :class="[selectClass, 'w-full']">
                <option value="">—</option>
                <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <BaseInput v-model="toolName" label="Product" placeholder="Milk, dinner, Shell..." />
              <BaseInput
                v-model="amount"
                label="Price"
                type="number"
                step="0.01"
                min="0.01"
                placeholder="20.00"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <BaseInput v-model="expenseDate" label="Date" type="date" />
              <div>
                <label class="text-sm text-surface-mid block mb-1">Currency</label>
                <select v-model="currency" :class="[selectClass, 'w-full']">
                  <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="text-sm text-surface-mid block mb-1">Notes</label>
              <textarea
                v-model="notes"
                rows="3"
                placeholder="Invoice ref, billing period..."
                class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
              />
            </div>

            <div class="flex gap-3 pt-2">
              <BaseButton variant="primary" :disabled="loading">
                {{ loading ? "Saving..." : "Save" }}
              </BaseButton>
              <BaseButton variant="ghost" type="button" @click="emit('close')">Cancel</BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
