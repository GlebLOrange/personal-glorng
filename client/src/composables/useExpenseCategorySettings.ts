import { ref } from "vue";

import { useCategoryManager } from "@/composables/useCategoryManager";

/**
 * Settings-tab category concerns: useCategoryManager plus delete-confirm dialog state.
 */
export function useExpenseCategorySettings(onCategoriesChanged: () => void | Promise<void>) {
  const deletingCategory = ref(false);
  const deleteCategoryTarget = ref<{ id: number; name: string } | null>(null);

  const categoryManager = useCategoryManager(onCategoriesChanged);

  const {
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
    removeCategory: removeCategoryRaw,
  } = categoryManager;

  function requestDeleteCategory(category: { id: number; name: string }): void {
    deleteCategoryTarget.value = category;
  }

  async function confirmDeleteCategory(): Promise<void> {
    if (!deleteCategoryTarget.value) return;
    const category = expenseCategories.value.find((c) => c.id === deleteCategoryTarget.value!.id);
    if (!category) {
      deleteCategoryTarget.value = null;
      return;
    }

    deletingCategory.value = true;
    try {
      await removeCategoryRaw(category);
      deleteCategoryTarget.value = null;
    } finally {
      deletingCategory.value = false;
    }
  }

  return {
    deletingCategory,
    deleteCategoryTarget,
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
    requestDeleteCategory,
    confirmDeleteCategory,
  };
}
