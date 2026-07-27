<script setup lang="ts">
import { nextTick, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import {
  crossRate,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
} from "@/composables/useExpenseFilters";
import type { ExchangeRates, ExpenseCategory } from "@/types";

const props = defineProps<{
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

watch(
  () => props.editingCategoryId,
  async (id) => {
    if (id == null) return;
    await nextTick();
    document.querySelector<HTMLInputElement>(`[data-category-edit="${id}"]`)?.focus();
  },
);

function onCategoryRowClick(category: ExpenseCategory): void {
  if (props.editingCategoryId === category.id) return;
  emit("startEditCategory", category);
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <Card class="flex flex-col gap-3">
      <BaseSelect v-model="displayCurrency" label="ledger totals currency">
        <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </BaseSelect>
      <p class="text-xs text-surface-mid">
        Totals and conversions on the ledger use this currency.
      </p>
    </Card>

    <Card v-if="exchangeRates">
      <p class="mb-3 text-xs text-surface-mid">exchange rates</p>
      <div class="flex flex-wrap gap-3 text-xs text-surface-mid">
        <span class="text-surface-light">1 {{ EXPENSE_DEFAULT_CURRENCY }} =</span>
        <span v-for="c in EXPENSE_EXCHANGE_RATE_TARGETS" :key="c">
          {{ crossRate(exchangeRates.rates, EXPENSE_DEFAULT_CURRENCY, c).toFixed(4) }} {{ c }}
        </span>
      </div>
    </Card>

    <Card>
      <p class="mb-3 text-xs text-surface-mid">categories</p>

      <ul class="mb-4 divide-y divide-surface-border rounded-lg border border-surface-border">
        <li
          v-for="category in expenseCategories"
          :key="category.id"
          class="flex flex-wrap items-center gap-2 px-3 py-2"
          :class="editingCategoryId === category.id ? undefined : 'cursor-pointer'"
          @click="onCategoryRowClick(category)"
        >
          <template v-if="editingCategoryId === category.id">
            <div class="flex min-w-[8rem] flex-1 flex-col gap-1" @click.stop>
              <label class="text-label text-surface-sage" :for="`cat-name-${category.id}`">
                name
              </label>
              <input
                :id="`cat-name-${category.id}`"
                v-model="editingCategoryName"
                :data-category-edit="category.id"
                class="h-10 w-full rounded-lg border border-surface-border bg-surface-dark px-3 text-sm text-surface-light outline-none focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/50"
                @keyup.enter="emit('saveCategoryRename')"
              />
            </div>
            <div class="flex w-36 flex-col gap-1" @click.stop>
              <label class="text-label text-surface-sage" :for="`cat-budget-${category.id}`">
                monthly budget
              </label>
              <input
                :id="`cat-budget-${category.id}`"
                v-model="editingCategoryBudget"
                type="number"
                min="0"
                step="0.01"
                inputmode="decimal"
                placeholder="0.00"
                class="h-10 w-full rounded-lg border border-surface-border bg-surface-dark px-3 font-data text-sm text-surface-light outline-none focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/50"
                @keyup.enter="emit('saveCategoryRename')"
              />
            </div>
            <ToolbarPillButton family="2xx" @click.stop="emit('saveCategoryRename')">
              save
            </ToolbarPillButton>
            <BaseButton
              variant="secondary"
              size="sm"
              @click.stop="emit('cancelEditCategory')"
            >
              cancel
            </BaseButton>
          </template>
          <template v-else>
            <span class="flex-1 text-sm text-surface-light">
              {{ category.name }}
              <span v-if="category.monthly_budget" class="ml-2 text-xs text-surface-mid">
                budget {{ category.monthly_budget }}
              </span>
            </span>
            <IconEditButton
              :aria-label="`Rename ${category.name}`"
              @click.stop="emit('startEditCategory', category)"
            />
            <IconCloseButton
              :aria-label="`Delete ${category.name}`"
              @click.stop="emit('removeCategory', category)"
            />
          </template>
        </li>
      </ul>

      <form
        class="flex flex-col gap-2 sm:flex-row sm:items-end"
        @submit.prevent="emit('addCategory')"
      >
        <BaseInput
          v-model="newCategoryName"
          label="new category"
          placeholder="category name"
          class="w-full min-w-0 flex-1"
        />
        <ToolbarPillButton type="submit" family="2xx" class="shrink-0">
          + category
        </ToolbarPillButton>
      </form>
    </Card>
  </div>
</template>
