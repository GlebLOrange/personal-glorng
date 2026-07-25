<script setup lang="ts">
import ExpenseCalculatorBudget from "@/components/expense-calculator/ExpenseCalculatorBudget.vue";
import ExpenseCalculatorConvert from "@/components/expense-calculator/ExpenseCalculatorConvert.vue";
import ExpenseCalculatorLineItems from "@/components/expense-calculator/ExpenseCalculatorLineItems.vue";
import ExpenseCalculatorModeTabs from "@/components/expense-calculator/ExpenseCalculatorModeTabs.vue";
import ExpenseCalculatorWhatIf from "@/components/expense-calculator/ExpenseCalculatorWhatIf.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { Card } from "@/components/ui/card";
import type {
  ExpenseCalculatorBudgetRow,
  ExpenseCalculatorLineItem,
  ExpenseCalculatorMode,
} from "@/composables/useExpenseCalculator";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates } from "@/types";

const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });
const whatIfCategoryId = defineModel<string>("whatIfCategoryId", { required: true });
const whatIfAmount = defineModel<string>("whatIfAmount", { required: true });
const whatIfCurrency = defineModel<CurrencyCode>("whatIfCurrency", { required: true });

defineProps<{
  persistenceHint: string;
  isSuperuser: boolean;
  loadingState: boolean;
  saving: boolean;
  stateDirty: boolean;
  activeMode: ExpenseCalculatorMode;
  modeTabs: { id: ExpenseCalculatorMode; label: string }[];
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
  lineItems: ExpenseCalculatorLineItem[];
  sumTotal: number;
  budgetRows: ExpenseCalculatorBudgetRow[];
  budgetSummary: {
    totalBudget: number;
    totalSpent: number;
    remaining: number;
    percent: number;
    overBudget: boolean;
    rows: Array<{
      id: string;
      name: string;
      budget: number;
      spent: number;
      remaining: number;
      percent: number;
      overBudget: boolean;
    }>;
  };
  budgetOptions: { id: string; name: string }[];
  whatIfProjection: {
    amount: number;
    budget: number;
    spent: number;
    projected: number;
    remaining: number;
    overBudget: boolean;
    overBy: number;
    withinBudget: boolean;
  };
  formatMoney: (amount: string | number, currency: string) => string;
  /** When set, wraps content in a tabpanel for the ledger calculator tab. */
  tabpanelId?: string;
  tabpanelLabelledBy?: string;
}>();

const emit = defineEmits<{
  loadState: [];
  saveState: [];
  changeMode: [mode: ExpenseCalculatorMode];
  addLineItem: [];
  removeLineItem: [id: string];
  applySumToBudget: [];
  addBudgetRow: [];
  removeBudgetRow: [id: string];
  goToBudget: [];
}>();
</script>

<template>
  <component
    :is="tabpanelId ? 'section' : 'div'"
    :id="tabpanelId"
    :role="tabpanelId ? 'tabpanel' : undefined"
    :aria-labelledby="tabpanelLabelledBy"
    :tabindex="tabpanelId ? 0 : undefined"
    class="flex min-w-0 flex-col gap-4 outline-none"
  >
    <Card
      variant="compact"
      class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
    >
      <p class="text-sm text-surface-mid">{{ persistenceHint }}</p>
      <div v-if="isSuperuser" class="flex flex-wrap gap-2">
        <BaseButton
          variant="ghost"
          class="min-h-11"
          :disabled="loadingState"
          @click="emit('loadState')"
        >
          {{ loadingState ? "loading..." : "load" }}
        </BaseButton>
        <BaseButton
          variant="success"
          class="min-h-11"
          :disabled="saving || !stateDirty"
          @click="emit('saveState')"
        >
          {{ saving ? "saving..." : "save" }}
        </BaseButton>
      </div>
    </Card>

    <div class="flex flex-col gap-3 md:flex-row md:items-end">
      <ExpenseCalculatorModeTabs
        class="flex-1"
        :active-mode="activeMode"
        :tabs="modeTabs"
        @change="emit('changeMode', $event)"
      />
      <div class="md:w-36">
        <BaseSelect
          id="expense-calculator-currency"
          v-model="displayCurrency"
          label="currency"
        >
          <option value="PLN">PLN</option>
          <option value="EUR">EUR</option>
          <option value="USD">USD</option>
          <option value="BYN">BYN</option>
        </BaseSelect>
      </div>
    </div>

    <section
      :id="`expense-calc-panel-${activeMode}`"
      role="tabpanel"
      :aria-labelledby="`expense-calc-tab-${activeMode}`"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCalculatorConvert
        v-if="activeMode === 'convert'"
        :exchange-rates="exchangeRates"
        :rates-loading="ratesLoading"
      />
      <ExpenseCalculatorLineItems
        v-else-if="activeMode === 'sum'"
        :line-items="lineItems"
        :display-currency="displayCurrency"
        :sum-total="sumTotal"
        :format-money="formatMoney"
        @add="emit('addLineItem')"
        @remove="emit('removeLineItem', $event)"
        @apply-to-budget="emit('applySumToBudget')"
      />
      <ExpenseCalculatorBudget
        v-else-if="activeMode === 'budget'"
        :budget-rows="budgetRows"
        :budget-summary="budgetSummary"
        :display-currency="displayCurrency"
        :format-money="formatMoney"
        @add="emit('addBudgetRow')"
        @remove="emit('removeBudgetRow', $event)"
      />
      <ExpenseCalculatorWhatIf
        v-else-if="activeMode === 'whatif'"
        v-model:what-if-category-id="whatIfCategoryId"
        v-model:what-if-amount="whatIfAmount"
        v-model:what-if-currency="whatIfCurrency"
        :budget-options="budgetOptions"
        :display-currency="displayCurrency"
        :projection="whatIfProjection"
        :format-money="formatMoney"
        @go-to-budget="emit('goToBudget')"
      />
    </section>
  </component>
</template>
