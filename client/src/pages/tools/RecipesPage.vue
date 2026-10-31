<script setup lang="ts">
import { computed, onMounted } from "vue";
import { storeToRefs } from "pinia";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
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
import { useAuthStore } from "@/stores/auth";
import type { Recipe } from "@/types";

const auth = useAuthStore();
const { isAuthenticated } = storeToRefs(auth);
const { can } = usePermissions();
const canWrite = computed(() => can("recipes", "write"));

/** Guest demo cards — static samples; no list API. */
const SAMPLE_RECIPES: Recipe[] = [
  {
    id: -1,
    title: "Weeknight pasta",
    ingredients: ["spaghetti", "garlic", "olive oil", "chili flakes"],
    steps: ["Boil pasta", "Sauté garlic", "Toss and serve"],
    notes: "Sample recipe for guests.",
    tags: ["demo", "pasta"],
    image_url: null,
    prep_time: 10,
    cook_time: 15,
    servings: 2,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: -2,
    title: "Citrus salad",
    ingredients: ["oranges", "fennel", "olive oil", "salt"],
    steps: ["Segment citrus", "Slice fennel", "Dress lightly"],
    notes: null,
    tags: ["demo", "salad"],
    image_url: null,
    prep_time: 15,
    cook_time: null,
    servings: 4,
    created_at: "2026-01-02T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
  },
];

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
  if (!isAuthenticated.value) return;
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
    max-width="5xl"
    :narrow="false"
    description="Personal recipe list with cook mode."
    tool
  >
    <div v-if="!isAuthenticated" class="min-w-0 space-y-3" aria-label="sample recipes">
      <p class="text-sm text-surface-mid">sample recipes</p>
      <ul class="space-y-2">
        <li
          v-for="recipe in SAMPLE_RECIPES"
          :key="recipe.id"
          class="rounded-lg border border-transparent bg-surface-card px-3 py-3"
        >
          <p class="text-sm font-medium text-surface-light">{{ recipe.title }}</p>
          <p class="mt-0.5 text-xs text-surface-mid">
            {{ recipe.tags.join(", ") }}
            <span v-if="recipe.prep_time"> · {{ recipe.prep_time }}m prep</span>
          </p>
        </li>
      </ul>
    </div>
    <RecipeFilters v-else v-model:search="search">
      <template v-if="canWrite" #actions>
        <ToolbarPillButton
          action="create"
          class="w-auto"
          :disabled="listLoading"
          @click="openCreate"
        >
          + recipe
        </ToolbarPillButton>
      </template>

      <div
        v-if="listLoading"
        class="flex flex-col gap-1"
        aria-busy="true"
        aria-label="loading recipes"
      >
        <div
          v-for="i in 6"
          :key="i"
          class="box-border w-full rounded-lg border border-transparent bg-surface-card px-2"
        >
          <div class="flex h-10 items-center gap-2">
            <div class="size-6 shrink-0 animate-pulse rounded bg-surface-border/40" />
            <div class="h-3 w-2/3 animate-pulse rounded bg-surface-border/40" />
          </div>
          <div class="mb-1.5 h-3 w-1/2 animate-pulse rounded bg-surface-border/30" />
        </div>
      </div>

      <ErrorState v-else-if="listError" :message="listError" show-retry @retry="loadRecipes" />

      <div v-else-if="recipes.length" class="mt-1 min-w-0">
        <AdminDataTable table-label="recipes">
          <template #header>
            <th class="px-3 py-1.5 text-xs tracking-wider" scope="col">thumb</th>
            <th class="px-3 py-1.5 text-xs tracking-wider" scope="col">title</th>
            <th class="px-3 py-1.5 text-xs tracking-wider" scope="col">meta</th>
            <th class="w-px px-2 text-right text-xs tracking-wider" scope="col">actions</th>
          </template>
          <RecipeCard
            v-for="recipe in recipes"
            :key="recipe.id"
            :recipe="recipe"
            :can-write="canWrite"
            @select="openRecipeFromCard"
            @edit="editRecipeFromCard"
            @delete="requestDelete"
          />
        </AdminDataTable>
      </div>

      <EmptyState
        v-else
        :description="
          hasFilters
            ? 'no recipes match your filters'
            : 'no recipes yet — add your first one to get cooking.'
        "
      >
        <template v-if="hasFilters || canWrite" #action>
          <BaseButton v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters">
            clear filters
          </BaseButton>
          <BaseButton v-else-if="canWrite" variant="create" size="sm" @click="openCreate">
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
        aria-label="recipes pagination"
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

    <ConfirmDialog
      v-if="canWrite"
      :open="showDeleteConfirm"
      title="delete recipe"
      :message="deleteConfirmMessage"
      confirm-label="delete"
      loading-label="deleting recipe…"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </PageShell>
</template>
