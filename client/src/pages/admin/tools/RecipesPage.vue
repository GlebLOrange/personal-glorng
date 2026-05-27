<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import type { Recipe } from "@/types";

const recipes = ref<Recipe[]>([]);
const allTags = ref<string[]>([]);
const search = ref("");
const activeTag = ref<string | null>(null);
const loading = ref(false);
const showForm = ref(false);
const editingId = ref<number | null>(null);
const expandedId = ref<number | null>(null);

const form = ref({
  title: "",
  ingredients: [""],
  steps: [""],
  notes: "",
  tags: "",
  image_url: "",
  prep_time: null as number | null,
  cook_time: null as number | null,
  servings: null as number | null,
});

const { toast } = useNotify();

const formTitle = computed(() => (editingId.value ? "edit recipe" : "new recipe"));

function resetForm(): void {
  form.value = {
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
  editingId.value = null;
}

async function loadRecipes(): Promise<void> {
  try {
    const params: Record<string, string> = {};
    if (search.value) params.search = search.value;
    if (activeTag.value) params.tag = activeTag.value;
    const { data } = await api.get<Recipe[]>("/tools/recipes", { params });
    recipes.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load recipes", "error");
  }
}

async function loadTags(): Promise<void> {
  try {
    const { data } = await api.get<string[]>("/tools/recipes/tags");
    allTags.value = data;
  } catch (err) {
    console.error(err);
    /* tags are non-critical */
  }
}

async function saveRecipe(): Promise<void> {
  if (!form.value.title.trim()) return;
  loading.value = true;

  const payload = {
    title: form.value.title,
    ingredients: form.value.ingredients.filter((i) => i.trim()),
    steps: form.value.steps.filter((s) => s.trim()),
    notes: form.value.notes || null,
    tags: form.value.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean),
    image_url: form.value.image_url || null,
    prep_time: form.value.prep_time,
    cook_time: form.value.cook_time,
    servings: form.value.servings,
  };

  try {
    if (editingId.value) {
      await api.put(`/tools/recipes/${editingId.value}`, payload);
      toast("Recipe updated", "success");
    } else {
      await api.post("/tools/recipes", payload);
      toast("Recipe created", "success");
    }
    showForm.value = false;
    resetForm();
    await Promise.all([loadRecipes(), loadTags()]);
  } catch (err) {
    console.error(err);
    toast("Failed to save recipe", "error");
  } finally {
    loading.value = false;
  }
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

function openCreate(): void {
  resetForm();
  showForm.value = true;
}

async function deleteRecipe(id: number): Promise<void> {
  try {
    await api.delete(`/tools/recipes/${id}`);
    toast("Recipe deleted", "success");
    if (expandedId.value === id) expandedId.value = null;
    await Promise.all([loadRecipes(), loadTags()]);
  } catch (err) {
    console.error(err);
    toast("Failed to delete recipe", "error");
  }
}

function toggleExpand(id: number): void {
  expandedId.value = expandedId.value === id ? null : id;
}

function addListItem(list: string[]): void {
  list.push("");
}

function removeListItem(list: string[], index: number): void {
  if (list.length > 1) list.splice(index, 1);
}

function formatTime(minutes: number | null): string {
  if (!minutes) return "";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}

let debounceTimer: ReturnType<typeof setTimeout>;
watch(search, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadRecipes, 300);
});

watch(activeTag, loadRecipes);
onMounted(() => Promise.all([loadRecipes(), loadTags()]));
</script>

<template>
  <AdminPageLayout title="recipes" max-width="xl">
    <!-- Search & filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="flex-1">
        <BaseInput v-model="search" placeholder="Search recipes..." />
      </div>
      <div class="flex gap-2 items-end">
        <select
          v-model="activeTag"
          class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                 focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
        >
          <option :value="null">All tags</option>
          <option v-for="tag in allTags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
        <BaseButton variant="primary" @click="openCreate">+ Add</BaseButton>
      </div>
    </div>

    <!-- Form modal overlay -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="showForm"
          class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/60"
          @click.self="showForm = false"
        >
          <div class="bg-surface-card border border-surface-border rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h2 class="text-lg font-bold text-surface-light mb-6">
              <span class="accent-gradient">€ {{ formTitle }}</span>
            </h2>

            <form class="space-y-4" @submit.prevent="saveRecipe">
              <BaseInput v-model="form.title" label="Title" placeholder="Recipe title" />

              <BaseInput v-model="form.image_url" label="Image URL" placeholder="https://..." />

              <div class="grid grid-cols-3 gap-3">
                <BaseInput
                  v-model.number="form.prep_time"
                  label="Prep (min)"
                  type="number"
                  placeholder="15"
                />
                <BaseInput
                  v-model.number="form.cook_time"
                  label="Cook (min)"
                  type="number"
                  placeholder="30"
                />
                <BaseInput
                  v-model.number="form.servings"
                  label="Servings"
                  type="number"
                  placeholder="4"
                />
              </div>

              <BaseInput v-model="form.tags" label="Tags" placeholder="dinner, pasta, quick" />

              <!-- Ingredients -->
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Ingredients</label>
                <div class="space-y-2">
                  <div v-for="(_, idx) in form.ingredients" :key="idx" class="flex gap-2">
                    <input
                      v-model="form.ingredients[idx]"
                      class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                             focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50"
                      :placeholder="`Ingredient ${idx + 1}`"
                    />
                    <BaseButton
                      v-if="form.ingredients.length > 1"
                      variant="ghost"
                      size="sm"
                      type="button"
                      @click="removeListItem(form.ingredients, idx)"
                    >
                      &times;
                    </BaseButton>
                  </div>
                  <BaseButton variant="ghost" size="sm" type="button" @click="addListItem(form.ingredients)">
                    + ingredient
                  </BaseButton>
                </div>
              </div>

              <!-- Steps -->
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Steps</label>
                <div class="space-y-2">
                  <div v-for="(_, idx) in form.steps" :key="idx" class="flex gap-2">
                    <div class="text-surface-mid text-sm font-mono pt-2 w-6 text-right shrink-0">{{ idx + 1 }}.</div>
                    <textarea
                      v-model="form.steps[idx]"
                      rows="2"
                      class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                             focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
                      :placeholder="`Step ${idx + 1}`"
                    />
                    <BaseButton
                      v-if="form.steps.length > 1"
                      variant="ghost"
                      size="sm"
                      type="button"
                      @click="removeListItem(form.steps, idx)"
                    >
                      &times;
                    </BaseButton>
                  </div>
                  <BaseButton variant="ghost" size="sm" type="button" @click="addListItem(form.steps)">
                    + step
                  </BaseButton>
                </div>
              </div>

              <!-- Notes -->
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Notes</label>
                <textarea
                  v-model="form.notes"
                  rows="3"
                  placeholder="Tips, variations, source link..."
                  class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                         focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
                />
              </div>

              <div class="flex gap-3 pt-2">
                <BaseButton variant="primary" :disabled="loading">
                  {{ loading ? "Saving..." : "Save" }}
                </BaseButton>
                <BaseButton variant="ghost" type="button" @click="showForm = false">
                  Cancel
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Recipe grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <BaseCard
        v-for="recipe in recipes"
        :key="recipe.id"
        hoverable
        class="cursor-pointer flex flex-col"
        @click="toggleExpand(recipe.id)"
      >
        <!-- Image -->
        <BaseImage
          :src="recipe.image_url"
          :alt="recipe.title"
          class="w-full h-40 rounded-md mb-3 -mt-1"
        />

        <!-- Title -->
        <h3 class="text-surface-light font-bold text-sm mb-2">{{ recipe.title }}</h3>

        <!-- Tags -->
        <div v-if="recipe.tags.length" class="flex flex-wrap gap-1.5 mb-3">
          <span
            v-for="tag in recipe.tags"
            :key="tag"
            class="text-[10px] font-mono px-2 py-0.5 rounded-full border border-accent-blue/40 text-accent-blue"
          >
            {{ tag }}
          </span>
        </div>

        <!-- Meta -->
        <div class="flex gap-3 text-xs text-surface-mid mt-auto">
          <span v-if="recipe.prep_time || recipe.cook_time">
            {{ formatTime((recipe.prep_time ?? 0) + (recipe.cook_time ?? 0)) }} total
          </span>
          <span v-if="recipe.servings">{{ recipe.servings }} servings</span>
        </div>

        <!-- Expanded detail -->
        <div v-if="expandedId === recipe.id" class="mt-4 pt-4 border-t border-surface-border" @click.stop>
          <div class="mb-3">
            <h4 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-1">Ingredients</h4>
            <ul class="text-sm text-surface-light space-y-0.5">
              <li v-for="(ing, i) in recipe.ingredients" :key="i" class="before:content-['·_'] before:text-accent-blue">
                {{ ing }}
              </li>
            </ul>
          </div>

          <div class="mb-3">
            <h4 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-1">Steps</h4>
            <ol class="text-sm text-surface-light space-y-1">
              <li v-for="(step, i) in recipe.steps" :key="i">
                <span class="text-accent-blue mr-1">{{ i + 1 }}.</span> {{ step }}
              </li>
            </ol>
          </div>

          <div v-if="recipe.notes" class="mb-3">
            <h4 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-1">Notes</h4>
            <p class="text-sm text-surface-light whitespace-pre-line">{{ recipe.notes }}</p>
          </div>

          <div class="flex gap-2 pt-2">
            <BaseButton variant="ghost" size="sm" @click="openEdit(recipe)">Edit</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="deleteRecipe(recipe.id)">Delete</BaseButton>
          </div>
        </div>
      </BaseCard>
    </div>

    <p v-if="recipes.length === 0" class="text-surface-mid text-sm text-center py-8">
      No recipes yet. Add your first one above.
    </p>
  </AdminPageLayout>
</template>
