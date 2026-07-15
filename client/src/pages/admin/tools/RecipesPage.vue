<script setup lang="ts">
import { computed, onMounted } from "vue";

import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
import RecipeCard from "@/components/recipes/RecipeCard.vue";
import RecipeCookMode from "@/components/recipes/RecipeCookMode.vue";
import RecipeDetailDrawer from "@/components/recipes/RecipeDetailDrawer.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import RecipeFilters from "@/components/recipes/RecipeFilters.vue";
import RecipeFormDrawer from "@/components/recipes/RecipeFormDrawer.vue";
import { usePermissions } from "@/composables/usePermissions";
import { useRecipes } from "@/composables/useRecipes";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";

const { can } = usePermissions();
const canWrite = computed(() => can("recipes", "write"));

const {
  recipes,
  allTags,
  search,
  activeTags,
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
  total,
  totalPages,
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

useScrollListFingerprint(
  () => `${activeTags.value.join(",")}:${recipes.value.length}`,
);

onMounted(async () => {
  await Promise.all([loadRecipes(), loadTags()]);
  await tryOpenFromQuery();
});

function clearFilters(): void {
  search.value = "";
  setTag(null);
}

function openRecipeFromCard(recipeId: number): void {
  const recipe = recipes.value.find((item) => item.id === recipeId);
  if (canWrite.value && recipe) {
    openEdit(recipe);
    return;
  }
  void openDetail(recipeId);
}

function openRecipeEdit(recipe: NonNullable<typeof selectedRecipe.value>): void {
  closeDetail();
  openEdit(recipe);
}
</script>

<template>
  <PageShell
    title="recipes"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'recipes' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <header class="page-intro">
      <div v-if="canWrite" class="flex flex-wrap gap-2">
        <BaseButton variant="primary" @click="openCreate">+ New recipe</BaseButton>
      </div>
    </header>

    <RecipeFilters
      v-model:search="search"
      :active-tags="activeTags"
      :all-tags="allTags"
      @set-tag="setTag"
      @clear-filters="clearFilters"
    >
      <div
        v-if="listLoading"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        aria-busy="true"
        aria-label="Loading recipes"
      >
        <Card v-for="i in 6" :key="i" class="h-64 animate-pulse" />
      </div>

      <ErrorState
        v-else-if="listError"
        :message="listError"
        show-retry
        @retry="loadRecipes"
      />

      <div v-else-if="recipes.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <RecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
          :active-tags="activeTags"
          @select="openRecipeFromCard"
          @tag-click="setTag"
        />
      </div>

      <EmptyState
        v-else
        :description="
          hasFilters
            ? 'No recipes match your filters.'
            : 'No recipes yet. Add your first one to get started.'
        "
      >
        <template v-if="hasFilters || canWrite" #action>
          <BaseButton v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters">
            clear filters
          </BaseButton>
          <BaseButton v-else-if="canWrite" variant="ghost" size="sm" @click="openCreate">
            + Add your first recipe
          </BaseButton>
        </template>
      </EmptyState>

      <AdminListFooter
        v-if="!listLoading && !listError && (recipes.length > 0 || page > 1)"
        :count-label="recipeCountLabel"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="page > 1"
        ariaLabel="Recipes pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </RecipeFilters>

    <RecipeFormDrawer
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
      @edit="openRecipeEdit"
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
  </PageShell>
</template>
