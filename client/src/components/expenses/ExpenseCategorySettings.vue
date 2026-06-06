<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { EXPENSE_CURRENCIES } from "@/composables/useExpenseFilters";
import type { ExchangeRates, ExpenseCategory } from "@/types";

defineProps<{
  expenseCategories: ExpenseCategory[];
  editingCategoryId: number | null;
  exchangeRates: ExchangeRates | null;
}>();

const displayCurrency = defineModel<string>("displayCurrency", { required: true });
const newCategoryName = defineModel<string>("newCategoryName", { required: true });
const editingCategoryName = defineModel<string>("editingCategoryName", { required: true });
const editingCategoryBudget = defineModel<string>("editingCategoryBudget", { required: true });

const emit = defineEmits<{
  addCategory: [];
  startEditCategory: [category: ExpenseCategory];
  cancelEditCategory: [];
  saveCategoryRename: [];
  removeCategory: [category: ExpenseCategory];
}>();

const selectClass =
  "bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm " +
  "focus:outline-none focus:border-accent-blue transition-colors h-[42px]";
</script>

<template>
  <div class="flex flex-col gap-6">
    <BaseCard>
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-3">Display</p>
      <label class="text-sm text-surface-mid block mb-1">Show totals in</label>
      <select v-model="displayCurrency" :class="selectClass">
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </select>
    </BaseCard>

    <BaseCard v-if="exchangeRates">
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-3">Exchange rates</p>
      <div class="flex flex-wrap gap-3 text-xs text-surface-mid">
        <span class="text-surface-light">1 USD =</span>
        <span v-for="c in EXPENSE_CURRENCIES.filter((code) => code !== 'USD')" :key="c">
          {{ parseFloat(exchangeRates.rates[c]).toFixed(4) }} {{ c }}
        </span>
      </div>
    </BaseCard>

    <BaseCard>
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-3">Categories</p>

      <ul class="divide-y divide-surface-border rounded-lg border border-surface-border mb-3">
        <li
          v-for="category in expenseCategories"
          :key="category.id"
          class="flex flex-wrap items-center gap-2 px-3 py-2"
        >
          <template v-if="editingCategoryId === category.id">
            <input
              v-model="editingCategoryName"
              class="flex-1 min-w-[8rem] bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5 text-surface-light text-sm focus:outline-none focus:border-accent-blue"
              @keyup.enter="emit('saveCategoryRename')"
            />
            <input
              v-model="editingCategoryBudget"
              type="number"
              min="0"
              step="0.01"
              placeholder="Budget"
              class="w-28 bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5 text-surface-light text-sm focus:outline-none focus:border-accent-blue"
            />
            <BaseButton variant="primary" size="sm" @click="emit('saveCategoryRename')">
              Save
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="emit('cancelEditCategory')">
              Cancel
            </BaseButton>
          </template>
          <template v-else>
            <span class="flex-1 text-surface-light text-sm">
              {{ category.name }}
              <span v-if="category.monthly_budget" class="text-surface-mid text-xs ml-2">
                budget {{ category.monthly_budget }}
              </span>
            </span>
            <BaseButton variant="ghost" size="sm" @click="emit('startEditCategory', category)">
              Rename
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="emit('removeCategory', category)">
              Delete
            </BaseButton>
          </template>
        </li>
      </ul>

      <form class="flex flex-col sm:flex-row gap-2" @submit.prevent="emit('addCategory')">
        <input
          v-model="newCategoryName"
          placeholder="New category name"
          class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-3 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue h-[42px]"
        />
        <BaseButton variant="primary" type="submit">Add category</BaseButton>
      </form>
      <p class="text-xs text-surface-mid mt-3">
        Renaming updates all expenses in that category. Optional monthly budget uses display
        currency. Delete only works when unused.
      </p>
    </BaseCard>
  </div>
</template>
