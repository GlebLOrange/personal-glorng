import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { DEFAULT_EXPENSE_CATEGORY } from "@/constants/expenseCategories";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { ExpenseCategory } from "@/types";

export function useCategoryManager(onCategoriesChanged: () => void | Promise<void>) {
  const expenseCategories = ref<ExpenseCategory[]>([]);
  const showCategoryManager = ref(false);
  const newCategoryName = ref("");
  const editingCategoryId = ref<number | null>(null);
  const editingCategoryName = ref("");
  const editingCategoryBudget = ref("");
  const { toast } = useNotify();
  const { run: runApi } = useApiAction({ logErrors: false });

  const categoryOptions = computed(() => expenseCategories.value.map((category) => category.name));

  const defaultCategoryName = computed(
    () =>
      categoryOptions.value.find((name) => name === DEFAULT_EXPENSE_CATEGORY) ??
      categoryOptions.value[0] ??
      DEFAULT_EXPENSE_CATEGORY,
  );

  async function loadCategories(): Promise<void> {
    const data = await runApi(
      async () => {
        const response = await api.get<ExpenseCategory[]>("/tools/expenses/categories");
        return response.data;
      },
      { errorMessage: "Failed to load categories" },
    );
    if (data) expenseCategories.value = data;
  }

  async function addCategory(): Promise<void> {
    const name = newCategoryName.value.trim();
    if (!name) {
      toast("Category name is required", "error");
      return;
    }

    try {
      await api.post("/tools/expenses/categories", { name });
      newCategoryName.value = "";
      toast("Category added", "success");
      await loadCategories();
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Failed to add category"), "error");
    }
  }

  function startEditCategory(category: ExpenseCategory): void {
    editingCategoryId.value = category.id;
    editingCategoryName.value = category.name;
    editingCategoryBudget.value = category.monthly_budget ?? "";
  }

  function cancelEditCategory(): void {
    editingCategoryId.value = null;
    editingCategoryName.value = "";
    editingCategoryBudget.value = "";
  }

  async function saveCategoryRename(): Promise<void> {
    if (editingCategoryId.value === null) return;
    const name = editingCategoryName.value.trim();
    if (!name) {
      toast("Category name is required", "error");
      return;
    }

    const budgetRaw = editingCategoryBudget.value.trim();
    let monthly_budget: string | null = null;
    if (budgetRaw) {
      const budgetValue = parseFloat(budgetRaw);
      if (Number.isNaN(budgetValue) || budgetValue < 0) {
        toast("Budget must be zero or greater", "error");
        return;
      }
      monthly_budget = budgetValue.toFixed(2);
    }

    try {
      await api.put(`/tools/expenses/categories/${editingCategoryId.value}`, {
        name,
        monthly_budget,
      });
      cancelEditCategory();
      toast("Category updated", "success");
      await Promise.all([loadCategories(), onCategoriesChanged()]);
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Failed to update category"), "error");
    }
  }

  async function removeCategory(category: ExpenseCategory): Promise<void> {
    try {
      await api.delete(`/tools/expenses/categories/${category.id}`);
      toast("Category deleted", "success");
      await loadCategories();
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Cannot delete a category that is used by expenses"), "error");
    }
  }

  return {
    expenseCategories,
    showCategoryManager,
    newCategoryName,
    editingCategoryId,
    editingCategoryName,
    editingCategoryBudget,
    categoryOptions,
    defaultCategoryName,
    loadCategories,
    addCategory,
    startEditCategory,
    cancelEditCategory,
    saveCategoryRename,
    removeCategory,
  };
}
