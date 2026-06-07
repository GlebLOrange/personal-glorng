import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useApiAction } from "@/composables/useApiAction";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import type { PaginatedRecipes, Recipe, RecipeSort } from "@/types";

const PER_PAGE = 24;

export interface RecipeFormData {
  title: string;
  ingredients: string[];
  steps: string[];
  notes: string;
  tags: string;
  image_url: string;
  prep_time: number | null;
  cook_time: number | null;
  servings: number | null;
}

function emptyForm(): RecipeFormData {
  return {
    title: "",
    ingredients: [""],
    steps: [""],
    notes: "",
    tags: "",
    image_url: "",
    prep_time: null,
    cook_time: null,
    servings: null,
  };
}

function isValidOptionalMinutes(value: number | null): boolean {
  return value === null || (Number.isFinite(value) && value >= 0);
}

function isValidOptionalServings(value: number | null): boolean {
  return value === null || (Number.isFinite(value) && value >= 1);
}

export function useRecipes() {
  const route = useRoute();
  const router = useRouter();
  const { toast } = useNotify();

  const recipes = ref<Recipe[]>([]);
  const allTags = ref<string[]>([]);
  const total = ref(0);
  const totalPages = ref(0);
  const search = ref("");
  const activeTag = ref<string | null>(null);
  const sort = ref<RecipeSort>("updated_desc");
  const page = ref(1);
  const selectedRecipe = ref<Recipe | null>(null);
  const selectedRecipeId = ref<number | null>(null);
  const showForm = ref(false);
  const showCookMode = ref(false);
  const showDeleteConfirm = ref(false);
  const editingId = ref<number | null>(null);
  const form = ref<RecipeFormData>(emptyForm());
  let loadGeneration = 0;

  const {
    loading: listLoading,
    lastError: listError,
    run: runList,
  } = useApiAction();
  const { loading: detailLoading, run: runDetail } = useApiAction();
  const { loading: saving, run: runSave } = useApiAction();
  const { loading: deleting, run: runDelete } = useApiAction();
  const { run: runTags } = useApiAction();

  const drawerOpen = computed(
    () => selectedRecipeId.value !== null || selectedRecipe.value !== null,
  );
  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasFilters = computed(
    () => Boolean(search.value.trim() || activeTag.value),
  );
  const recipeCountLabel = computed(() => {
    const n = total.value;
    const parts = [`${n} recipe${n === 1 ? "" : "s"}`];
    if (activeTag.value) parts.push(`tag: ${activeTag.value}`);
    if (totalPages.value > 0) {
      parts.push(`page ${page.value} of ${totalPages.value}`);
    }
    return parts.join(" · ");
  });
  const formTitle = computed(() => (editingId.value ? "edit recipe" : "new recipe"));
  const deleteConfirmMessage = computed(() =>
    selectedRecipe.value
      ? `Delete "${selectedRecipe.value.title}"? This cannot be undone.`
      : "Delete this recipe? This cannot be undone.",
  );

  function recipeQueryId(): number | null {
    const raw = route.query.recipe;
    const value = Array.isArray(raw) ? raw[0] : raw;
    if (!value) return null;
    const id = Number(value);
    return Number.isFinite(id) && id > 0 ? id : null;
  }

  function setRecipeQuery(id: number | null): void {
    const nextQuery = { ...route.query };
    if (id) {
      nextQuery.recipe = String(id);
    } else {
      delete nextQuery.recipe;
    }
    void router.replace({ query: nextQuery });
  }

  async function loadRecipes(): Promise<void> {
    const generation = ++loadGeneration;
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: PER_PAGE,
      sort: sort.value,
    };
    if (search.value.trim()) params.search = search.value.trim();
    if (activeTag.value) params.tag = activeTag.value;

    const data = await runList(
      async () => {
        const response = await api.get<PaginatedRecipes>("/tools/recipes", { params });
        return response.data;
      },
      { errorFallback: "Failed to load recipes", logContext: "recipes.loadList" },
    );
    if (generation !== loadGeneration) return;
    if (data) {
      recipes.value = data.items;
      total.value = data.total;
      totalPages.value = data.pages;
    }
  }

  async function loadTags(): Promise<void> {
    const data = await runTags(
      async () => {
        const response = await api.get<string[]>("/tools/recipes/tags");
        return response.data;
      },
      { errorFallback: "Failed to load tags", silent: true, logContext: "recipes.loadTags" },
    );
    if (data) {
      allTags.value = data;
    }
  }

  async function openDetail(recipeId: number): Promise<void> {
    selectedRecipeId.value = recipeId;
    setRecipeQuery(recipeId);
    const data = await runDetail(
      async () => {
        const response = await api.get<Recipe>(`/tools/recipes/${recipeId}`);
        return response.data;
      },
      { errorFallback: "Failed to load recipe", logContext: "recipes.openDetail" },
    );
    if (data) {
      selectedRecipe.value = data;
      return;
    }
    selectedRecipeId.value = null;
    selectedRecipe.value = null;
    setRecipeQuery(null);
  }

  function closeDetail(): void {
    selectedRecipe.value = null;
    selectedRecipeId.value = null;
    showCookMode.value = false;
    setRecipeQuery(null);
  }

  function openCookMode(): void {
    if (!selectedRecipe.value) return;
    showCookMode.value = true;
  }

  function closeCookMode(): void {
    showCookMode.value = false;
  }

  function setTag(tag: string | null): void {
    activeTag.value = tag;
    page.value = 1;
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
  }

  function resetForm(): void {
    form.value = emptyForm();
    editingId.value = null;
  }

  function openCreate(): void {
    resetForm();
    showForm.value = true;
  }

  function openEdit(recipe: Recipe): void {
    editingId.value = recipe.id;
    form.value = {
      title: recipe.title,
      ingredients: recipe.ingredients.length ? [...recipe.ingredients] : [""],
      steps: recipe.steps.length ? [...recipe.steps] : [""],
      notes: recipe.notes ?? "",
      tags: recipe.tags.join(", "),
      image_url: recipe.image_url ?? "",
      prep_time: recipe.prep_time,
      cook_time: recipe.cook_time,
      servings: recipe.servings,
    };
    showForm.value = true;
  }

  function buildPayload() {
    return {
      title: form.value.title.trim(),
      ingredients: form.value.ingredients.filter((i) => i.trim()),
      steps: form.value.steps.filter((s) => s.trim()),
      notes: form.value.notes.trim() || null,
      tags: form.value.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
      image_url: form.value.image_url.trim() || null,
      prep_time: form.value.prep_time,
      cook_time: form.value.cook_time,
      servings: form.value.servings,
    };
  }

  async function saveRecipe(): Promise<void> {
    if (!form.value.title.trim()) {
      toast("Title is required", "error");
      return;
    }
    if (!isValidOptionalMinutes(form.value.prep_time)) {
      toast("Prep time must be a valid number of minutes", "error");
      return;
    }
    if (!isValidOptionalMinutes(form.value.cook_time)) {
      toast("Cook time must be a valid number of minutes", "error");
      return;
    }
    if (!isValidOptionalServings(form.value.servings)) {
      toast("Servings must be at least 1", "error");
      return;
    }
    const payload = buildPayload();
    if (!payload.ingredients.length || !payload.steps.length) {
      toast("At least one ingredient and one step are required", "error");
      return;
    }

    const result = await runSave(
      async () => {
        if (editingId.value) {
          await api.put(`/tools/recipes/${editingId.value}`, payload);
        } else {
          await api.post("/tools/recipes", payload);
        }
      },
      {
        successMessage: editingId.value ? "Recipe updated" : "Recipe created",
        errorFallback: "Failed to save recipe",
        logContext: "recipes.save",
      },
    );
    if (result === null) return;

    showForm.value = false;
    const savedId = editingId.value;
    resetForm();
    await Promise.all([loadRecipes(), loadTags()]);

    if (savedId && selectedRecipe.value?.id === savedId) {
      await openDetail(savedId);
    }
  }

  function requestDelete(): void {
    if (!selectedRecipe.value) return;
    showDeleteConfirm.value = true;
  }

  function cancelDelete(): void {
    showDeleteConfirm.value = false;
  }

  async function confirmDelete(): Promise<void> {
    if (!selectedRecipe.value) return;
    const recipeId = selectedRecipe.value.id;
    const result = await runDelete(
      async () => {
        await api.delete(`/tools/recipes/${recipeId}`);
      },
      {
        successMessage: "Recipe deleted",
        errorFallback: "Failed to delete recipe",
        logContext: "recipes.delete",
      },
    );
    if (result === null) return;

    showDeleteConfirm.value = false;
    closeDetail();
    await Promise.all([loadRecipes(), loadTags()]);
  }

  async function tryOpenFromQuery(): Promise<void> {
    const id = recipeQueryId();
    if (!id) return;
    if (selectedRecipe.value?.id === id) return;
    await openDetail(id);
  }

  let debounceTimer: ReturnType<typeof setTimeout>;
  watch(search, () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      page.value = 1;
      void loadRecipes();
    }, 300);
  });

  watch([activeTag, sort], () => {
    if (page.value !== 1) {
      page.value = 1;
      return;
    }
    void loadRecipes();
  });

  watch(page, () => {
    void loadRecipes();
  });

  watch(
    () => route.query.recipe,
    () => {
      const id = recipeQueryId();
      if (!id) {
        if (selectedRecipe.value || selectedRecipeId.value) {
          selectedRecipe.value = null;
          selectedRecipeId.value = null;
        }
        return;
      }
      if (selectedRecipe.value?.id !== id && selectedRecipeId.value !== id) {
        void openDetail(id);
      }
    },
  );

  return {
    recipes,
    allTags,
    total,
    totalPages,
    search,
    activeTag,
    sort,
    page,
    selectedRecipe,
    selectedRecipeId,
    drawerOpen,
    showForm,
    showCookMode,
    showDeleteConfirm,
    editingId,
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
  };
}
