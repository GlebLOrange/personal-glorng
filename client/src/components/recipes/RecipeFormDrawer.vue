<script setup lang="ts">
import { computed } from "vue";

import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { FIELD_INPUT_CLASS } from "@/constants/formClasses";
import type { RecipeFormData } from "@/composables/useRecipes";

const props = defineProps<{
  open: boolean;
  form: RecipeFormData;
  formTitle: string;
  loading: boolean;
  allTags: string[];
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:form": [value: RecipeFormData];
}>();

const parsedTags = computed(() =>
  props.form.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean),
);

const tagSuggestions = computed(() =>
  props.allTags.filter((tag) => !parsedTags.value.includes(tag)),
);

const showImagePreview = computed(() => Boolean(props.form.image_url.trim()));

function patch(patch: Partial<RecipeFormData>): void {
  emit("update:form", { ...props.form, ...patch });
}

function setTagsFromList(tags: string[]): void {
  patch({ tags: tags.join(", ") });
}

function removeTag(tag: string): void {
  setTagsFromList(parsedTags.value.filter((item) => item !== tag));
}

function addTag(tag: string): void {
  const trimmed = tag.trim();
  if (!trimmed || parsedTags.value.includes(trimmed)) return;
  setTagsFromList([...parsedTags.value, trimmed]);
}

function addIngredient(): void {
  patch({ ingredients: [...props.form.ingredients, ""] });
}

function removeIngredient(index: number): void {
  if (props.form.ingredients.length <= 1) return;
  patch({ ingredients: props.form.ingredients.filter((_, i) => i !== index) });
}

function updateIngredient(index: number, value: string): void {
  const ingredients = [...props.form.ingredients];
  ingredients[index] = value;
  patch({ ingredients });
}

function moveIngredient(index: number, direction: -1 | 1): void {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= props.form.ingredients.length) return;
  const ingredients = [...props.form.ingredients];
  [ingredients[index], ingredients[nextIndex]] = [ingredients[nextIndex], ingredients[index]];
  patch({ ingredients });
}

function addStep(): void {
  patch({ steps: [...props.form.steps, ""] });
}

function removeStep(index: number): void {
  if (props.form.steps.length <= 1) return;
  patch({ steps: props.form.steps.filter((_, i) => i !== index) });
}

function updateStep(index: number, value: string): void {
  const steps = [...props.form.steps];
  steps[index] = value;
  patch({ steps });
}

function moveStep(index: number, direction: -1 | 1): void {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= props.form.steps.length) return;
  const steps = [...props.form.steps];
  [steps[index], steps[nextIndex]] = [steps[nextIndex], steps[index]];
  patch({ steps });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}

function toNullableNumber(value: string | number | null | undefined): number | null {
  if (value === "" || value == null) return null;
  return Number(value);
}

const inputClass = FIELD_INPUT_CLASS + " flex-1";
</script>

<template>
  <BaseDrawer :open="open" :title="formTitle" max-width="xl" @close="emit('close')">
    <form id="recipe-form-drawer-form" class="space-y-6" @submit.prevent="emit('save')">
      <section class="space-y-4">
        <h3 class="text-sm font-medium text-surface-mid">basics</h3>
        <BaseInput
          :model-value="form.title"
          placeholder="title"
          aria-label="title"
          @update:model-value="patch({ title: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.image_url"
          placeholder="image url (https://...)"
          aria-label="image url (https://...)"
          @update:model-value="patch({ image_url: toStringValue($event) })"
        />
        <BaseImage
          v-if="showImagePreview"
          :src="form.image_url"
          :alt="form.title || 'Recipe preview'"
          class="w-full h-40 rounded-md object-cover"
        />
      </section>

      <section class="space-y-4">
        <h3 class="text-sm font-medium text-surface-mid">timing</h3>
        <div class="grid grid-cols-3 gap-3">
          <BaseInput
            :model-value="form.prep_time"
            type="number"
            placeholder="prep (min)"
            aria-label="prep (min)"
            @update:model-value="patch({ prep_time: toNullableNumber($event) })"
          />
          <BaseInput
            :model-value="form.cook_time"
            type="number"
            placeholder="cook (min)"
            aria-label="cook (min)"
            @update:model-value="patch({ cook_time: toNullableNumber($event) })"
          />
          <BaseInput
            :model-value="form.servings"
            type="number"
            placeholder="servings"
            aria-label="servings"
            @update:model-value="patch({ servings: toNullableNumber($event) })"
          />
        </div>
      </section>

      <section class="space-y-3">
        <h3 class="text-sm font-medium text-surface-mid">tags</h3>
        <div v-if="parsedTags.length" class="flex flex-wrap gap-1.5">
          <button
            v-for="tag in parsedTags"
            :key="tag"
            type="button"
            class="group inline-flex items-center gap-1"
            @click="removeTag(tag)"
          >
            <RecipeTagChip :tag="tag" compact />
            <span
              class="text-surface-mid group-hover:text-surface-light text-xs leading-none"
              aria-hidden="true"
            >
              &times;
            </span>
            <span class="sr-only">Remove {{ tag }}</span>
          </button>
        </div>
        <BaseInput
          :model-value="form.tags"
          placeholder="tags (dinner, pasta, quick)"
          aria-label="tags (dinner, pasta, quick)"
          @update:model-value="patch({ tags: toStringValue($event) })"
        />
        <div v-if="tagSuggestions.length" class="flex flex-wrap gap-1.5">
          <RecipeTagChip
            v-for="tag in tagSuggestions"
            :key="tag"
            :tag="tag"
            compact
            @click="addTag(tag)"
          />
        </div>
      </section>

      <section class="space-y-3">
        <h3 class="text-sm font-medium text-surface-mid">ingredients</h3>
        <div class="space-y-2">
          <div v-for="(_, idx) in form.ingredients" :key="idx" class="flex gap-2 items-start">
            <input
              :value="form.ingredients[idx]"
              :class="inputClass"
              :placeholder="`ingredient ${idx + 1}`"
              :aria-label="`ingredient ${idx + 1}`"
              @input="updateIngredient(idx, ($event.target as HTMLInputElement).value)"
            />
            <div class="flex flex-col gap-1 shrink-0">
              <BaseButton
                variant="ghost"
                size="sm"
                type="button"
                :disabled="idx === 0"
                aria-label="Move ingredient up"
                @click="moveIngredient(idx, -1)"
              >
                ↑
              </BaseButton>
              <BaseButton
                variant="ghost"
                size="sm"
                type="button"
                :disabled="idx === form.ingredients.length - 1"
                aria-label="Move ingredient down"
                @click="moveIngredient(idx, 1)"
              >
                ↓
              </BaseButton>
            </div>
            <BaseButton
              v-if="form.ingredients.length > 1"
              variant="ghost"
              size="sm"
              type="button"
              aria-label="Remove ingredient"
              @click="removeIngredient(idx)"
            >
              &times;
            </BaseButton>
          </div>
          <BaseButton variant="ghost" size="sm" type="button" @click="addIngredient">
            + ingredient
          </BaseButton>
        </div>
      </section>

      <section class="space-y-3">
        <h3 class="text-sm font-medium text-surface-mid">steps</h3>
        <div class="space-y-2">
          <div v-for="(_, idx) in form.steps" :key="idx" class="flex gap-2 items-start">
            <div class="text-surface-mid text-sm pt-2 w-6 text-right shrink-0">{{ idx + 1 }}.</div>
            <div class="flex-1 min-w-0">
              <BaseTextarea
                :model-value="form.steps[idx]"
                :rows="2"
                :placeholder="`step ${idx + 1}`"
                :aria-label="`step ${idx + 1}`"
                @update:model-value="updateStep(idx, String($event ?? ''))"
              />
            </div>
            <div class="flex flex-col gap-1 shrink-0">
              <BaseButton
                variant="ghost"
                size="sm"
                type="button"
                :disabled="idx === 0"
                aria-label="Move step up"
                @click="moveStep(idx, -1)"
              >
                ↑
              </BaseButton>
              <BaseButton
                variant="ghost"
                size="sm"
                type="button"
                :disabled="idx === form.steps.length - 1"
                aria-label="Move step down"
                @click="moveStep(idx, 1)"
              >
                ↓
              </BaseButton>
            </div>
            <BaseButton
              v-if="form.steps.length > 1"
              variant="ghost"
              size="sm"
              type="button"
              aria-label="Remove step"
              @click="removeStep(idx)"
            >
              &times;
            </BaseButton>
          </div>
          <BaseButton variant="ghost" size="sm" type="button" @click="addStep"> + step </BaseButton>
        </div>
      </section>

      <section class="space-y-3">
        <h3 class="text-sm font-medium text-surface-mid">notes</h3>
        <BaseTextarea
          :model-value="form.notes"
          :rows="3"
          placeholder="notes (tips, variations, source link...)"
          aria-label="notes (tips, variations, source link...)"
          @update:model-value="patch({ notes: String($event ?? '') })"
        />
      </section>
    </form>

    <template #footer>
      <div class="flex gap-3">
        <BaseButton
          type="submit"
          form="recipe-form-drawer-form"
          variant="primary"
          :disabled="loading"
        >
          {{ loading ? "saving..." : "save" }}
        </BaseButton>
        <BaseButton variant="ghost" type="button" @click="emit('close')">cancel</BaseButton>
      </div>
    </template>
  </BaseDrawer>
</template>
