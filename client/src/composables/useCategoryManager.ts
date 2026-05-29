import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { ExpenseCategory } from "@/types";

export function useCategoryManager(onCategoriesChanged: () => void | Promise<void>) {
  const expenseCategories = ref<ExpenseCategory[]>([]);
  const showCategoryManager = ref(false);
  const newCategoryName = ref("");
  const editingCategoryId = ref<number | null>(null);
  const editingCategoryName = ref("");
  const { toast } = useNotify();

  const categoryOptions = computed(() =>
    expenseCategories.value.map((category) => category.name),
  );

  const defaultCategoryName = computed(
    () =>
      categoryOptions.value.find((name) => name === "Groceries")
      ?? categoryOptions.value[0]
      ?? "Groceries",
  );

  async function loadCategories(): Promise<void> {
    try {
      const { data } = await api.get<ExpenseCategory[]>("/tools/expenses/categories");
      expenseCategories.value = data;
    } catch (err) {
      console.error(err);
    }
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
  }

  function cancelEditCategory(): void {
    editingCategoryId.value = null;
    editingCategoryName.value = "";
  }

  async function saveCategoryRename(): Promise<void> {
    if (editingCategoryId.value === null) return;
    const name = editingCategoryName.value.trim();
    if (!name) {
      toast("Category name is required", "error");
      return;
    }

    try {
      await api.put(`/tools/expenses/categories/${editingCategoryId.value}`, { name });
      cancelEditCategory();
      toast("Category updated", "success");
      await Promise.all([loadCategories(), onCategoriesChanged()]);
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Failed to update category"), "error");
    }
  }

  async function removeCategory(category: ExpenseCategory): Promise<void> {
    if (!confirm(`Delete category "${category.name}"?`)) return;

    try {
      await api.delete(`/tools/expenses/categories/${category.id}`);
      toast("Category deleted", "success");
      await loadCategories();
    } catch (err) {
      console.error(err);
      toast(
        getApiErrorMessage(err, "Cannot delete a category that is used by expenses"),
        "error",
      );
    }
  }

  return {
    expenseCategories,
    showCategoryManager,
    newCategoryName,
    editingCategoryId,
    editingCategoryName,
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
