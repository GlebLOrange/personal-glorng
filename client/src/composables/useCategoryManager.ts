import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { DEFAULT_EXPENSE_CATEGORY } from "@/constants/expenseCategories";
import { useNotify } from "@/composables/useNotify";
import type { ExpenseCategory } from "@/types";

/** Match server normalize: trim + collapse whitespace. */
export function normalizeCategoryName(name: string): string {
  return name.trim().split(/\s+/).join(" ");
}

export function categoryNameExists(
  categories: Pick<ExpenseCategory, "id" | "name">[],
  name: string,
  excludeId: number | null = null,
): boolean {
  const key = normalizeCategoryName(name).toLowerCase();
  if (!key) return false;
  return categories.some(
    (category) =>
      category.id !== excludeId && normalizeCategoryName(category.name).toLowerCase() === key,
  );
}

/** Case-insensitive unique names; keeps first occurrence (API sort order). */
export function uniqueCategoryNames(categories: Pick<ExpenseCategory, "name">[]): string[] {
  const seen = new Set<string>();
  const names: string[] = [];
  for (const category of categories) {
    const key = category.name.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    names.push(category.name);
  }
  return names;
}

export function useCategoryManager(onCategoriesChanged: () => void | Promise<void>) {
  const expenseCategories = ref<ExpenseCategory[]>([]);
  const newCategoryName = ref("");
  const editingCategoryId = ref<number | null>(null);
  const editingCategoryName = ref("");
  const editingCategoryBudget = ref("");
  const { toast } = useNotify();
  const { run: runApi } = useApiAction();

  const categoryOptions = computed(() => uniqueCategoryNames(expenseCategories.value));

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
    const name = normalizeCategoryName(newCategoryName.value);
    if (!name) {
      toast("Category name is required", "error");
      return;
    }
    if (categoryNameExists(expenseCategories.value, name)) {
      toast("Category already exists", "error");
      return;
    }

    const ok = await runApi(
      async () => {
        await api.post("/tools/expenses/categories", { name });
        return true;
      },
      { successMessage: "Category added", errorMessage: "Failed to add category" },
    );
    if (!ok) return;
    newCategoryName.value = "";
    await loadCategories();
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
    const name = normalizeCategoryName(editingCategoryName.value);
    if (!name) {
      toast("Category name is required", "error");
      return;
    }
    if (categoryNameExists(expenseCategories.value, name, editingCategoryId.value)) {
      toast("Category already exists", "error");
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

    const categoryId = editingCategoryId.value;
    const ok = await runApi(
      async () => {
        await api.put(`/tools/expenses/categories/${categoryId}`, {
          name,
          monthly_budget,
        });
        return true;
      },
      { successMessage: "Category updated", errorMessage: "Failed to update category" },
    );
    if (!ok) return;
    cancelEditCategory();
    await Promise.all([loadCategories(), onCategoriesChanged()]);
  }

  async function removeCategory(category: ExpenseCategory): Promise<void> {
    const ok = await runApi(
      async () => {
        await api.delete(`/tools/expenses/categories/${category.id}`);
        return true;
      },
      {
        successMessage: "Category deleted",
        errorMessage: "Cannot delete a category that is used by expenses",
      },
    );
    if (!ok) return;
    await loadCategories();
  }

  return {
    expenseCategories,
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
