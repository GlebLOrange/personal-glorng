<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import PageShell from "@/components/layout/PageShell.vue";
import RecipeCard from "@/components/recipes/RecipeCard.vue";
import RecipeCookMode from "@/components/recipes/RecipeCookMode.vue";
import RecipeDetailDrawer from "@/components/recipes/RecipeDetailDrawer.vue";
import RecipeFilters from "@/components/recipes/RecipeFilters.vue";
import RecipeFormDrawer from "@/components/recipes/RecipeFormDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { usePermissions } from "@/composables/usePermissions";
import { useRecipes } from "@/composables/useRecipes";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type { Recipe } from "@/types";

const RECIPE_TABS = [{ id: "all", label: "all" }] as const;
const activeTab = ref("all");

const { can } = usePermissions();
const canWrite = computed(() => can("recipes", "write"));

const {
  recipes,
  search,
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
  openDetail,
  closeDetail,
  openCookMode,
  closeCookMode,
  goToPage,
  openCreate,
  openEdit,
  saveRecipe,
  requestDelete,
  cancelDelete,
  confirmDelete,
  tryOpenFromQuery,
} = useRecipes();

useScrollListFingerprint(() => `${search.value}:${recipes.value.length}`);

onMounted(async () => {
  await loadRecipes();
  await tryOpenFromQuery();
});

function clearFilters(): void {
  search.value = "";
}

function openRecipeFromCard(recipeId: number): void {
  void openDetail(recipeId);
}

function openRecipeEdit(recipe: Recipe): void {
  closeDetail();
  openEdit(recipe);
}

function editRecipeFromCard(recipe: Recipe): void {
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
    <div class="mb-3 flex min-w-0 flex-wrap items-center gap-2">
      <AdminTabBar
        v-model="activeTab"
        flush
        panel-id-prefix="recipes-tab"
        :tabs="[...RECIPE_TABS]"
      />
      <ToolbarPillButton
        v-if="canWrite"
        family="2xx"
        class="ml-auto"
        :disabled="listLoading"
        @click="openCreate"
      >
        + recipe
      </ToolbarPillButton>
    </div>

    <RecipeFilters v-model:search="search">
      <div
        v-if="listLoading"
        class="flex flex-col divide-y divide-surface-border/40"
        aria-busy="true"
        aria-label="Loading recipes"
      >
        <div v-for="i in 6" :key="i" class="w-full px-2 py-1.5">
          <div class="flex items-center gap-2">
            <div class="size-10 shrink-0 animate-pulse rounded-md bg-surface-border/40" />
            <div class="min-w-0 flex-1 space-y-2">
              <div class="h-4 w-2/3 animate-pulse rounded bg-surface-border/40" />
              <div class="h-3 w-1/3 animate-pulse rounded bg-surface-border/30" />
            </div>
          </div>
        </div>
      </div>

      <ErrorState v-else-if="listError" :message="listError" show-retry @retry="loadRecipes" />

      <div v-else-if="recipes.length" class="flex flex-col divide-y divide-surface-border/40">
        <RecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
          :can-write="canWrite"
          @select="openRecipeFromCard"
          @edit="editRecipeFromCard"
          @delete="requestDelete"
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
          <BaseButton v-else-if="canWrite" variant="success" size="sm" @click="openCreate">
            + your first recipe
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
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </RecipeFilters>

    <RecipeFormDrawer
      v-if="canWrite"
      :open="showForm"
      :form="form"
      :form-title="formTitle"
      :loading="saving"
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
      confirm-label="delete"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </PageShell>
</template>
