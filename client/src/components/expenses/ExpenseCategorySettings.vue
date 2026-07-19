<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { Card } from "@/components/ui/card";
import {
  crossRate,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
} from "@/composables/useExpenseFilters";
import { FIELD_INPUT_CLASS_COMPACT } from "@/constants/formClasses";
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
</script>

<template>
  <div class="flex flex-col gap-6">
    <Card>
      <BaseSelect v-model="displayCurrency" label="Ledger totals currency">
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
    </Card>

    <Card v-if="exchangeRates">
      <p class="text-xs text-surface-mid uppercase tracking-wider mb-3">Exchange rates</p>
      <div class="flex flex-wrap gap-3 text-xs text-surface-mid">
        <span class="text-surface-light">1 {{ EXPENSE_DEFAULT_CURRENCY }} =</span>
        <span v-for="c in EXPENSE_EXCHANGE_RATE_TARGETS" :key="c">
          {{ crossRate(exchangeRates.rates, EXPENSE_DEFAULT_CURRENCY, c).toFixed(4) }} {{ c }}
        </span>
      </div>
    </Card>

    <Card>
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
              :class="[FIELD_INPUT_CLASS_COMPACT, 'flex-1 min-w-[8rem]']"
              aria-label="Category name"
              @keyup.enter="emit('saveCategoryRename')"
            />
            <input
              v-model="editingCategoryBudget"
              type="number"
              min="0"
              step="0.01"
              placeholder="budget"
              aria-label="budget"
              :class="[FIELD_INPUT_CLASS_COMPACT, 'w-28']"
            />
            <BaseButton variant="primary" size="sm" @click="emit('saveCategoryRename')">
              save
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="emit('cancelEditCategory')">
              cancel
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
              rename
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="emit('removeCategory', category)">
              delete
            </BaseButton>
          </template>
        </li>
      </ul>

      <form class="flex flex-col sm:flex-row sm:items-end gap-2" @submit.prevent="emit('addCategory')">
        <BaseInput
          v-model="newCategoryName"
          label="New category"
          placeholder="name"
          class="flex-1"
        />
        <BaseButton variant="primary" type="submit">add category</BaseButton>
      </form>
      <p class="text-xs text-surface-mid mt-3">
        Renaming updates all expenses in that category. Optional monthly budget uses display
        currency. Delete only works when unused.
      </p>
    </Card>
  </div>
</template>
