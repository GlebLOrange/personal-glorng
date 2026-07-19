import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  convertCurrency,
  EXPENSE_DEFAULT_CURRENCY,
  fetchExchangeRates,
  formatMoney,
} from "@/composables/useExpenseCurrency";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import type { ExchangeRates } from "@/types";

export type ExpenseCalculatorMode = "convert" | "sum" | "budget" | "whatif";

export const EXPENSE_CALCULATOR_MODES: ExpenseCalculatorMode[] = [
  "convert",
  "sum",
  "budget",
  "whatif",
];

export function isCalculatorMode(value: string): value is ExpenseCalculatorMode {
  return EXPENSE_CALCULATOR_MODES.includes(value as ExpenseCalculatorMode);
}

export function normalizeCalculatorMode(value: string): ExpenseCalculatorMode {
  if (value === "converter") return "convert";
  return isCalculatorMode(value) ? value : "convert";
}

export interface ExpenseCalculatorLineItem {
  id: string;
  label: string;
  amount: string;
  currency: CurrencyCode;
}

export interface ExpenseCalculatorBudgetRow {
  id: string;
  name: string;
  budget: string;
  spent: string;
}

export interface ExpenseCalculatorStatePayload {
  display_currency: CurrencyCode;
  line_items: Array<{ label: string; amount: string; currency?: CurrencyCode | null }>;
  budget_rows: Array<{ name: string; budget: string; spent: string }>;
}

function newId(): string {
  return crypto.randomUUID();
}

function emptyLineItem(currency: CurrencyCode): ExpenseCalculatorLineItem {
  return { id: newId(), label: "", amount: "", currency };
}

function emptyBudgetRow(): ExpenseCalculatorBudgetRow {
  return { id: newId(), name: "", budget: "", spent: "0" };
}

function parseAmount(value: string): number {
  const num = parseFloat(value);
  return Number.isFinite(num) ? num : 0;
}

export function useExpenseCalculator() {
  const route = useRoute();
  const router = useRouter();
  const { isSuperuser } = usePermissions();
  const { loading: saving, run: runSave } = useApiAction();
  const { loading: loadingState, run: runLoad } = useApiAction({ silent: true });

  const exchangeRates = ref<ExchangeRates | null>(null);
  const ratesLoading = ref(false);
  const displayCurrency = ref<CurrencyCode>(EXPENSE_DEFAULT_CURRENCY);
  const lineItems = ref<ExpenseCalculatorLineItem[]>([emptyLineItem(EXPENSE_DEFAULT_CURRENCY)]);
  const budgetRows = ref<ExpenseCalculatorBudgetRow[]>([emptyBudgetRow()]);
  const whatIfCategoryId = ref<string | "overall">("overall");
  const whatIfAmount = ref("");
  const whatIfCurrency = ref<CurrencyCode>(EXPENSE_DEFAULT_CURRENCY);
  const stateDirty = ref(false);
  const lastSavedAt = ref<string | null>(null);
  const initialized = ref(false);

  const activeMode = computed<ExpenseCalculatorMode>(() => {
    const tab = route.query.tab;
    const mode = route.query.mode;
    if (
      tab === "calculator" &&
      typeof mode === "string" &&
      isCalculatorMode(mode)
    ) {
      return mode;
    }
    if (typeof tab === "string" && isCalculatorMode(tab)) {
      return tab;
    }
    if (typeof mode === "string" && isCalculatorMode(mode)) {
      return mode;
    }
    return "convert";
  });

  const modeTabs = computed(() =>
    EXPENSE_CALCULATOR_MODES.map((mode) => ({
      id: mode,
      label: mode === "whatif" ? "what-if" : mode,
    })),
  );

  function switchMode(mode: ExpenseCalculatorMode): void {
    if (route.name === "tool-expenses") {
      void router.replace({ query: { ...route.query, tab: "calculator", mode } });
      return;
    }
    const { mode: _legacyMode, ...rest } = route.query;
    void router.replace({ query: { ...rest, tab: mode } });
  }

  async function loadRates(): Promise<void> {
    ratesLoading.value = true;
    try {
      exchangeRates.value = await fetchExchangeRates();
    } finally {
      ratesLoading.value = false;
    }
  }

  const sumTotal = computed(() =>
    lineItems.value.reduce((total, item) => total + parseAmount(item.amount), 0),
  );

  const budgetSummary = computed(() => {
    const rows = budgetRows.value.filter((row) => row.name.trim());
    const totalBudget = rows.reduce((sum, row) => sum + parseAmount(row.budget), 0);
    const totalSpent = rows.reduce((sum, row) => sum + parseAmount(row.spent), 0);
    const remaining = totalBudget - totalSpent;
    const percent = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0;
    return {
      rows: rows.map((row) => {
        const budget = parseAmount(row.budget);
        const spent = parseAmount(row.spent);
        const rowRemaining = budget - spent;
        const rowPercent = budget > 0 ? Math.round((spent / budget) * 100) : 0;
        return {
          ...row,
          budget,
          spent,
          remaining: rowRemaining,
          percent: rowPercent,
          overBudget: budget > 0 && spent > budget,
        };
      }),
      totalBudget,
      totalSpent,
      remaining,
      percent,
      overBudget: totalBudget > 0 && totalSpent > totalBudget,
    };
  });

  const whatIfProjection = computed(() => {
    const amount = parseAmount(whatIfAmount.value);
    const summary = budgetSummary.value;
    let budget = summary.totalBudget;
    let spent = summary.totalSpent;

    if (whatIfCategoryId.value !== "overall") {
      const row = summary.rows.find((item) => item.id === whatIfCategoryId.value);
      if (row) {
        budget = row.budget;
        spent = row.spent;
      }
    }

    const projected = spent + amount;
    const remaining = budget - projected;
    const overBy = remaining < 0 ? Math.abs(remaining) : 0;
    return {
      amount,
      budget,
      spent,
      projected,
      remaining,
      overBudget: budget > 0 && projected > budget,
      overBy,
      withinBudget: budget <= 0 || projected <= budget,
    };
  });

  function addLineItem(): void {
    lineItems.value.push(emptyLineItem(displayCurrency.value));
    stateDirty.value = true;
  }

  function removeLineItem(id: string): void {
    if (lineItems.value.length <= 1) {
      lineItems.value = [emptyLineItem(displayCurrency.value)];
    } else {
      lineItems.value = lineItems.value.filter((item) => item.id !== id);
    }
    stateDirty.value = true;
  }

  function addBudgetRow(): void {
    budgetRows.value.push(emptyBudgetRow());
    stateDirty.value = true;
  }

  function removeBudgetRow(id: string): void {
    if (budgetRows.value.length <= 1) {
      budgetRows.value = [emptyBudgetRow()];
    } else {
      budgetRows.value = budgetRows.value.filter((row) => row.id !== id);
    }
    stateDirty.value = true;
  }

  function applySumToBudget(): void {
    const total = sumTotal.value;
    if (total <= 0) return;
    const first = budgetRows.value[0];
    if (first) {
      first.spent = total.toFixed(2);
    }
    stateDirty.value = true;
    switchMode("budget");
  }

  function toPayload(): ExpenseCalculatorStatePayload {
    return {
      display_currency: displayCurrency.value,
      line_items: lineItems.value
        .filter((item) => item.label.trim() || parseAmount(item.amount) > 0)
        .map((item) => ({
          label: item.label,
          amount: parseAmount(item.amount).toFixed(2),
          currency: item.currency,
        })),
      budget_rows: budgetRows.value
        .filter((row) => row.name.trim())
        .map((row) => ({
          name: row.name.trim(),
          budget: parseAmount(row.budget).toFixed(2),
          spent: parseAmount(row.spent).toFixed(2),
        })),
    };
  }

  function applyPayload(payload: ExpenseCalculatorStatePayload): void {
    displayCurrency.value = payload.display_currency ?? EXPENSE_DEFAULT_CURRENCY;
    lineItems.value =
      payload.line_items.length > 0
        ? payload.line_items.map((item) => ({
            id: newId(),
            label: item.label,
            amount: item.amount,
            currency: item.currency ?? displayCurrency.value,
          }))
        : [emptyLineItem(displayCurrency.value)];
    budgetRows.value =
      payload.budget_rows.length > 0
        ? payload.budget_rows.map((row) => ({
            id: newId(),
            name: row.name,
            budget: row.budget,
            spent: row.spent,
          }))
        : [emptyBudgetRow()];
    stateDirty.value = false;
  }

  async function saveState(): Promise<void> {
    if (!isSuperuser.value) return;
    const data = await runSave(
      async () => {
        const response = await api.put<ExpenseCalculatorStatePayload & { saved_at: string }>(
          "/tools/expense-calculator/state",
          toPayload(),
        );
        return response.data;
      },
      { successMessage: "Calculator saved", errorMessage: "Save failed" },
    );
    if (data) {
      lastSavedAt.value = data.saved_at ?? null;
      stateDirty.value = false;
    }
  }

  async function loadState(): Promise<void> {
    if (!isSuperuser.value) return;
    const data = await runLoad(async () => {
      const response = await api.get<ExpenseCalculatorStatePayload & { saved_at: string | null }>(
        "/tools/expense-calculator/state",
      );
      return response.data;
    });
    if (data) {
      applyPayload(data);
      lastSavedAt.value = data.saved_at ?? null;
    }
  }

  watch([displayCurrency, lineItems, budgetRows], () => {
    if (!initialized.value) return;
    stateDirty.value = true;
  }, { deep: true });

  onMounted(async () => {
    // Public calculator only: normalize ?mode=X → ?tab=X. Admin uses tab=calculator&mode=X.
    if (route.name !== "tool-expenses") {
      const legacyMode = route.query.mode;
      if (
        typeof legacyMode === "string" &&
        isCalculatorMode(legacyMode) &&
        route.query.tab !== legacyMode
      ) {
        const { mode: _m, ...rest } = route.query;
        void router.replace({ query: { ...rest, tab: legacyMode } });
      }
    }
    await loadRates();
    if (isSuperuser.value) {
      await loadState();
    }
    initialized.value = true;
  });

  return {
    activeMode,
    modeTabs,
    switchMode,
    exchangeRates,
    ratesLoading,
    displayCurrency,
    lineItems,
    budgetRows,
    whatIfCategoryId,
    whatIfAmount,
    whatIfCurrency,
    sumTotal,
    budgetSummary,
    whatIfProjection,
    isSuperuser,
    stateDirty,
    lastSavedAt,
    saving,
    loadingState,
    formatMoney,
    convertCurrency,
    loadRates,
    addLineItem,
    removeLineItem,
    addBudgetRow,
    removeBudgetRow,
    applySumToBudget,
    saveState,
    loadState,
  };
}
