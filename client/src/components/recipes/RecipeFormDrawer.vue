<script setup lang="ts">
import { computed } from "vue";

import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
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
</script>

<template>
  <BaseDrawer :open="open" :title="formTitle" max-width="xl" @close="emit('close')">
    <form id="recipe-form-drawer-form" class="space-y-4" @submit.prevent="emit('save')">
      <BaseInput
        :model-value="form.title"
        placeholder="enter title"
        aria-label="title"
        @update:model-value="patch({ title: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.image_url"
        placeholder="image url"
        aria-label="image url"
        @update:model-value="patch({ image_url: toStringValue($event) })"
      />
      <BaseImage
        v-if="showImagePreview"
        :src="form.image_url"
        :alt="form.title || 'Recipe preview'"
        class="w-full h-40 rounded-md object-cover"
      />

      <div class="grid grid-cols-3 gap-3">
        <BaseInput
          :model-value="form.prep_time"
          type="number"
          placeholder="prep · min"
          aria-label="prep time in minutes"
          @update:model-value="patch({ prep_time: toNullableNumber($event) })"
        />
        <BaseInput
          :model-value="form.cook_time"
          type="number"
          placeholder="cook · min"
          aria-label="cook time in minutes"
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

      <div class="space-y-2">
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
              class="text-surface-mid text-xs leading-none group-hover:text-status-error"
              aria-hidden="true"
            >
              &times;
            </span>
            <span class="sr-only">remove {{ tag }}</span>
          </button>
        </div>
        <BaseInput
          :model-value="form.tags"
          placeholder="tags · dinner, pasta"
          aria-label="tags"
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
      </div>

      <div class="space-y-2">
        <div
          v-for="(_, idx) in form.ingredients"
          :key="idx"
          class="flex min-w-0 items-center gap-1"
        >
          <BaseButton
            v-if="idx === 0"
            variant="ghost"
            type="button"
            class="w-11 px-0"
            aria-label="add ingredient"
            @click="addIngredient"
          >
            +
          </BaseButton>
          <span v-else class="inline-flex h-11 w-11 shrink-0" aria-hidden="true" />
          <BaseInput
            :model-value="form.ingredients[idx]"
            class="min-w-0 flex-1"
            placeholder="ingredient"
            :aria-label="`ingredient ${idx + 1}`"
            @update:model-value="updateIngredient(idx, toStringValue($event))"
          />
          <BaseButton
            variant="ghost"
            type="button"
            class="w-11 px-0"
            :disabled="idx === 0"
            aria-label="move ingredient up"
            @click="moveIngredient(idx, -1)"
          >
            ↑
          </BaseButton>
          <BaseButton
            variant="ghost"
            type="button"
            class="w-11 px-0"
            :disabled="idx === form.ingredients.length - 1"
            aria-label="move ingredient down"
            @click="moveIngredient(idx, 1)"
          >
            ↓
          </BaseButton>
          <BaseButton
            variant="ghost"
            danger
            type="button"
            class="w-11 px-0"
            :disabled="form.ingredients.length <= 1"
            aria-label="remove ingredient"
            @click="removeIngredient(idx)"
          >
            &times;
          </BaseButton>
        </div>
      </div>

      <div class="space-y-2">
        <div v-for="(_, idx) in form.steps" :key="idx" class="flex min-w-0 items-center gap-1">
          <BaseButton
            v-if="idx === 0"
            variant="ghost"
            type="button"
            class="w-11 px-0"
            aria-label="add step"
            @click="addStep"
          >
            +
          </BaseButton>
          <span v-else class="inline-flex h-11 w-11 shrink-0" aria-hidden="true" />
          <BaseInput
            :model-value="form.steps[idx]"
            class="min-w-0 flex-1"
            placeholder="step"
            :aria-label="`step ${idx + 1}`"
            @update:model-value="updateStep(idx, toStringValue($event))"
          />
          <BaseButton
            variant="ghost"
            type="button"
            class="w-11 px-0"
            :disabled="idx === 0"
            aria-label="move step up"
            @click="moveStep(idx, -1)"
          >
            ↑
          </BaseButton>
          <BaseButton
            variant="ghost"
            type="button"
            class="w-11 px-0"
            :disabled="idx === form.steps.length - 1"
            aria-label="move step down"
            @click="moveStep(idx, 1)"
          >
            ↓
          </BaseButton>
          <BaseButton
            variant="ghost"
            danger
            type="button"
            class="w-11 px-0"
            :disabled="form.steps.length <= 1"
            aria-label="remove step"
            @click="removeStep(idx)"
          >
            &times;
          </BaseButton>
        </div>
      </div>

      <BaseTextarea
        :model-value="form.notes"
        :rows="3"
        placeholder="notes · tips, variations"
        aria-label="notes"
        @update:model-value="patch({ notes: String($event ?? '') })"
      />
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
