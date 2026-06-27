<script setup lang="ts">
import { computed, onMounted } from "vue";

import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import RecipeCard from "@/components/recipes/RecipeCard.vue";
import RecipeCookMode from "@/components/recipes/RecipeCookMode.vue";
import RecipeDetailDrawer from "@/components/recipes/RecipeDetailDrawer.vue";
import RecipeFilters from "@/components/recipes/RecipeFilters.vue";
import RecipeFormModal from "@/components/recipes/RecipeFormModal.vue";
import TaskPagination from "@/components/tasks/TaskPagination.vue";
import { usePermissions } from "@/composables/usePermissions";
import { useRecipes } from "@/composables/useRecipes";

const { can } = usePermissions();
const canWrite = computed(() => can("recipes", "write"));

const {
  recipes,
  allTags,
  search,
  activeTags,
  sort,
  page,
  selectedRecipe,
  drawerOpen,
  showForm,
  showCookMode,
  showDeleteConfirm,
  form,
  listLoading,
  listError,
  detailLoading,
  saving,
  deleting,
  hasNextPage,
  hasFilters,
  recipeCountLabel,
  formTitle,
  deleteConfirmMessage,
  loadRecipes,
  loadTags,
  openDetail,
  closeDetail,
  openCookMode,
  closeCookMode,
  setTag,
  goToPage,
  openCreate,
  openEdit,
  saveRecipe,
  requestDelete,
  cancelDelete,
  confirmDelete,
  tryOpenFromQuery,
} = useRecipes();

onMounted(async () => {
  await Promise.all([loadRecipes(), loadTags()]);
  await tryOpenFromQuery();
});

function clearFilters(): void {
  search.value = "";
  setTag(null);
}
</script>

<template>
  <AdminPageLayout title="recipes" max-width="xl" back-to="/tools">
    <RecipeFilters
      v-model:search="search"
      v-model:sort="sort"
      :active-tags="activeTags"
      :all-tags="allTags"
      :recipe-count-label="recipeCountLabel"
      :can-write="canWrite"
      @set-tag="setTag"
      @create="openCreate"
      @clear-filters="clearFilters"
    >
      <div v-if="listLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="i in 6"
          :key="i"
          class="h-64 rounded-lg border border-surface-border bg-surface-card animate-pulse"
        />
      </div>

      <div
        v-else-if="listError"
        class="text-center py-12 border border-surface-border rounded-lg bg-surface-card"
      >
        <p class="text-surface-mid text-sm mb-4">{{ listError }}</p>
        <BaseButton variant="ghost" size="sm" @click="loadRecipes">Retry</BaseButton>
      </div>

      <div v-else-if="recipes.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <RecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
          :active-tags="activeTags"
          @select="openDetail"
          @tag-click="setTag"
        />
      </div>

      <div v-else class="text-center py-12">
        <p class="text-surface-mid text-sm mb-4">
          {{
            hasFilters
              ? "No recipes match your filters."
              : "No recipes yet. Add your first one to get started."
          }}
        </p>
        <BaseButton v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters">
          Clear filters
        </BaseButton>
        <button
          v-else-if="canWrite"
          type="button"
          class="text-accent-blue text-sm hover:underline"
          @click="openCreate"
        >
          + Add your first recipe
        </button>
      </div>

      <TaskPagination
        v-if="!listLoading && !listError && (recipes.length > 0 || page > 1)"
        :page="page"
        :has-next-page="hasNextPage"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </RecipeFilters>

    <RecipeFormModal
      v-if="canWrite"
      :open="showForm"
      :form="form"
      :form-title="formTitle"
      :loading="saving"
      :all-tags="allTags"
      @update:form="form = $event"
      @close="showForm = false"
      @save="saveRecipe"
    />

    <RecipeDetailDrawer
      :open="drawerOpen"
      :recipe="selectedRecipe"
      :loading="detailLoading"
      @close="closeDetail"
      @edit="openEdit"
      @delete="requestDelete"
      @cook="openCookMode"
    />

    <RecipeCookMode :recipe="selectedRecipe" :open="showCookMode" @close="closeCookMode" />

    <ExpenseConfirmDialog
      v-if="canWrite"
      :open="showDeleteConfirm"
      title="Delete recipe"
      :message="deleteConfirmMessage"
      confirm-label="Delete"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </AdminPageLayout>
</template>
