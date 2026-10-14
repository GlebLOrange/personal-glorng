import { computed, nextTick, ref, watch, type ComputedRef, type Ref } from "vue";

import { DEFAULT_EXPENSE_CATEGORY } from "@/constants/expenseCategories";
import {
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  type CurrencyCode,
} from "@/composables/useExpenseFilters";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useNotify } from "@/composables/useNotify";
import { isoDateLocal } from "@/utils/dates";
import type { Expense } from "@/types";

/** Focus/clear hooks for the expenses quick-add entry (QuickAdd or a wrapping panel). */
export type ExpenseQuickAddTarget = {
  focusEntry: () => void;
  focusSmartText: () => void;
  clearSmartText: () => void;
};

export type UseExpenseFormMutationsOptions = {
  quickAddRef: Ref<ExpenseQuickAddTarget | null>;
  switchTab: (tab: string) => void;
  displayCurrency: Ref<CurrencyCode>;
  saveDisplayCurrency: (currency: CurrencyCode) => void | Promise<void>;
  categoryOptions: ComputedRef<string[]>;
  defaultCategoryName: ComputedRef<string>;
  reloadAfterMutation: () => Promise<void>;
};

/** Create/edit form, quick-add, smart-add, and expense delete mutations. */
export function useExpenseFormMutations(options: UseExpenseFormMutationsOptions) {
  const {
    quickAddRef,
    switchTab,
    displayCurrency,
    saveDisplayCurrency,
    categoryOptions,
    defaultCategoryName,
    reloadAfterMutation,
  } = options;

  const { run: runSaveExpense, loading: savingExpense } = useApiAction();
  const { run: runDeleteExpense, loading: deletingExpense } = useApiAction();
  const smartTextOpen = ref(false);
  const showForm = ref(false);
  const editingId = ref<number | null>(null);
  const deleteTargetId = ref<number | null>(null);

  const { value: lastCategory, set: setLastCategory } = useLocalStorageString(
    EXPENSE_LAST_CATEGORY_STORAGE_KEY,
    DEFAULT_EXPENSE_CATEGORY,
  );

  const quickAddCurrency = computed(() => displayCurrency.value as CurrencyCode);

  const quickAdd = ref({
    price: "",
    category: lastCategory.value,
    product: "",
    expense_date: isoDateLocal(),
  });

  const quickAddNameError = ref<string | null>(null);
  const quickAddAmountError = ref<string | null>(null);

  const form = ref({
    tool_name: "",
    amount: "",
    currency: EXPENSE_DEFAULT_CURRENCY as CurrencyCode,
    expense_date: isoDateLocal(),
    category: "",
    notes: "",
  });

  const { toast } = useNotify();

  const formTitle = computed(() => (editingId.value ? "edit expense" : "new expense"));

  function resolvedCategory(name: string): string {
    if (categoryOptions.value.includes(name)) return name;
    return defaultCategoryName.value;
  }

  function defaultCurrency(): CurrencyCode {
    const value = displayCurrency.value;
    return EXPENSE_CURRENCIES.includes(value as CurrencyCode)
      ? (value as CurrencyCode)
      : EXPENSE_DEFAULT_CURRENCY;
  }

  function focusQuickAdd(): void {
    quickAddRef.value?.focusEntry();
  }

  function openSmartText(): void {
    smartTextOpen.value = true;
    switchTab("expenses");
    void nextTick(() => {
      quickAddRef.value?.focusSmartText();
    });
  }

  function resetForm(): void {
    form.value = {
      tool_name: "",
      amount: "",
      currency: defaultCurrency(),
      expense_date: isoDateLocal(),
      category: resolvedCategory(lastCategory.value),
      notes: "",
    };
    editingId.value = null;
  }

  function resetQuickAdd(): void {
    quickAdd.value = {
      price: "",
      category: lastCategory.value,
      product: "",
      expense_date: isoDateLocal(),
    };
    quickAddNameError.value = null;
    quickAddAmountError.value = null;
  }

  async function postExpense(payload: {
    tool_name: string;
    amount: string;
    currency: CurrencyCode;
    expense_date: string;
    category: string | null;
    notes: string | null;
  }): Promise<void> {
    if (editingId.value) {
      await api.put(`/tools/expenses/${editingId.value}`, payload);
      toast("Expense updated", "success");
    } else {
      await api.post("/tools/expenses", payload);
      toast("Expense created", "success");
    }
    void saveDisplayCurrency(payload.currency);
    if (payload.category) {
      setLastCategory(payload.category);
    }
  }

  async function saveExpense(): Promise<void> {
    if (!form.value.tool_name.trim()) {
      toast("Name is required", "error");
      return;
    }
    if (!form.value.amount || !form.value.expense_date) {
      toast("Amount and date are required", "error");
      return;
    }
    const amount = parseFloat(form.value.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      toast("Amount must be greater than zero", "error");
      return;
    }

    const payload = {
      tool_name: form.value.tool_name.trim(),
      amount: amount.toFixed(2),
      currency: form.value.currency,
      expense_date: form.value.expense_date,
      category: form.value.category.trim() || null,
      notes: form.value.notes.trim() || null,
    };

    const ok = await runSaveExpense(
      async () => {
        await postExpense(payload);
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    showForm.value = false;
    resetForm();
    await reloadAfterMutation();
  }

  async function quickSaveExpense(): Promise<void> {
    const product = quickAdd.value.product.trim();
    const amount = parseFloat(quickAdd.value.price);
    let hasError = false;

    if (!product) {
      quickAddNameError.value = "Goods or services is required";
      hasError = true;
    } else {
      quickAddNameError.value = null;
    }

    if (Number.isNaN(amount) || amount <= 0) {
      quickAddAmountError.value = "Enter a valid amount";
      hasError = true;
    } else {
      quickAddAmountError.value = null;
    }

    if (!quickAdd.value.expense_date) {
      toast("Date is required", "error");
      hasError = true;
    }

    if (hasError) return;

    const categoryName = quickAdd.value.category.trim();
    const category = categoryName
      ? categoryOptions.value.includes(categoryName)
        ? categoryName
        : resolvedCategory(categoryName)
      : null;

    const ok = await runSaveExpense(
      async () => {
        await postExpense({
          tool_name: product,
          amount: amount.toFixed(2),
          currency: defaultCurrency(),
          expense_date: quickAdd.value.expense_date,
          category,
          notes: null,
        });
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    resetQuickAdd();
    await reloadAfterMutation();
    focusQuickAdd();
  }

  async function saveSmartExpense(payload: {
    tool_name: string;
    amount: string;
    currency: CurrencyCode;
    expense_date: string;
    category: string | null;
  }): Promise<void> {
    const ok = await runSaveExpense(
      async () => {
        await postExpense({
          ...payload,
          category: payload.category ? resolvedCategory(payload.category) : null,
          notes: null,
        });
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    quickAddRef.value?.clearSmartText();
    await reloadAfterMutation();
    focusQuickAdd();
  }

  function openEdit(expense: Expense): void {
    editingId.value = expense.id;
    form.value = {
      tool_name: expense.tool_name,
      amount: expense.amount,
      currency: expense.currency as CurrencyCode,
      expense_date: expense.expense_date,
      category: expense.category ?? "",
      notes: expense.notes ?? "",
    };
    showForm.value = true;
  }

  function openCreate(): void {
    resetForm();
    showForm.value = true;
  }

  async function duplicateExpense(expense: Expense): Promise<void> {
    quickAdd.value = {
      product: expense.tool_name,
      price: expense.amount,
      category: expense.category ?? "",
      expense_date: isoDateLocal(),
    };
    quickAddNameError.value = null;
    quickAddAmountError.value = null;
    switchTab("expenses");
    toast("Ready to add again — adjust if needed", "success");
    await nextTick();
    focusQuickAdd();
  }

  function requestDeleteExpense(id: number): void {
    deleteTargetId.value = id;
  }

  async function confirmDeleteExpense(): Promise<void> {
    if (deleteTargetId.value === null) return;

    const id = deleteTargetId.value;
    const ok = await runDeleteExpense(
      async () => {
        await api.delete(`/tools/expenses/${id}`);
        return true;
      },
      { successMessage: "Expense deleted", errorMessage: "Failed to delete expense" },
    );
    if (!ok) return;
    deleteTargetId.value = null;
    await reloadAfterMutation();
  }

  watch(defaultCategoryName, (name) => {
    if (quickAdd.value.category && !categoryOptions.value.includes(quickAdd.value.category)) {
      quickAdd.value.category = name;
    }
  });

  watch(
    () => quickAdd.value.category,
    (category) => {
      if (categoryOptions.value.includes(category)) {
        setLastCategory(category);
      }
    },
  );

  function bootstrapFormOnMount(): void {
    quickAdd.value.category = resolvedCategory(lastCategory.value);
  }

  return {
    savingExpense,
    deletingExpense,
    smartTextOpen,
    showForm,
    deleteTargetId,
    quickAddCurrency,
    quickAdd,
    quickAddNameError,
    quickAddAmountError,
    form,
    formTitle,
    openEdit,
    openCreate,
    openSmartText,
    duplicateExpense,
    requestDeleteExpense,
    confirmDeleteExpense,
    saveExpense,
    quickSaveExpense,
    saveSmartExpense,
    bootstrapFormOnMount,
  };
}
