import { ref } from "vue";

import { useCategoryManager } from "@/composables/useCategoryManager";

/**
 * Category admin: useCategoryManager plus delete-confirm dialog state with reassignment.
 */
export function useExpenseCategorySettings(onCategoriesChanged: () => void | Promise<void>) {
  const deletingCategory = ref(false);
  const deleteCategoryTarget = ref<{ id: number; name: string } | null>(null);
  /** null = Uncategorized; undefined = unused category (no body). */
  const deleteCategoryReplacementId = ref<number | null | undefined>(undefined);

  const categoryManager = useCategoryManager(onCategoriesChanged);

  const {
    expenseCategories,
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
    removeCategory: removeCategoryRaw,
  } = categoryManager;

  function requestDeleteCategory(category: { id: number; name: string }): void {
    deleteCategoryTarget.value = category;
    // Default destination: Uncategorized (null).
    deleteCategoryReplacementId.value = null;
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
      // Always send reassignment payload so in-use deletes succeed atomically.
      const replacement =
        deleteCategoryReplacementId.value === undefined
          ? null
          : deleteCategoryReplacementId.value;
      const ok = await removeCategoryRaw(category, replacement);
      if (ok) {
        deleteCategoryTarget.value = null;
        deleteCategoryReplacementId.value = undefined;
      }
    } finally {
      deletingCategory.value = false;
    }
  }

  return {
    deletingCategory,
    deleteCategoryTarget,
    deleteCategoryReplacementId,
    expenseCategories,
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
    requestDeleteCategory,
    confirmDeleteCategory,
  };
}
