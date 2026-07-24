<script setup lang="ts">
import { computed, nextTick } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import type { RecipeFormData } from "@/composables/useRecipes";

const props = defineProps<{
  open: boolean;
  form: RecipeFormData;
  formTitle: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:form": [value: RecipeFormData];
}>();

const showImagePreview = computed(() => Boolean(props.form.image_url.trim()));

function patch(patch: Partial<RecipeFormData>): void {
  emit("update:form", { ...props.form, ...patch });
}

async function focusField(selector: string, index: number): Promise<void> {
  await nextTick();
  const fields = document.querySelectorAll<HTMLElement>(selector);
  fields[index]?.focus();
}

function addIngredient(): void {
  patch({ ingredients: [...props.form.ingredients, ""] });
  void focusField("[data-recipe-ingredient]", props.form.ingredients.length);
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

function onIngredientEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter") return;
  event.preventDefault();
  // Insert after current row so Enter mid-list adds the next line in place.
  const ingredients = [...props.form.ingredients];
  ingredients.splice(index + 1, 0, "");
  patch({ ingredients });
  void focusField("[data-recipe-ingredient]", index + 1);
}

function addStep(): void {
  patch({ steps: [...props.form.steps, ""] });
  void focusField("[data-recipe-step]", props.form.steps.length);
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

function onStepModEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter" || !(event.metaKey || event.ctrlKey)) return;
  event.preventDefault();
  const steps = [...props.form.steps];
  steps.splice(index + 1, 0, "");
  patch({ steps });
  void focusField("[data-recipe-step]", index + 1);
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
  <BaseDrawer :open="open" :title="formTitle" max-width="2xl" @close="emit('close')">
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
        <p class="text-xs text-surface-mid uppercase tracking-wider">Ingredients</p>
        <ul role="list" class="space-y-2">
          <li
            v-for="(_, idx) in form.ingredients"
            :key="`ingredient-${idx}`"
            class="flex min-w-0 items-center gap-1"
          >
            <BaseInput
              :model-value="form.ingredients[idx]"
              class="min-w-0 flex-1"
              placeholder="200g flour"
              :aria-label="`ingredient ${idx + 1}`"
              data-recipe-ingredient
              @update:model-value="updateIngredient(idx, toStringValue($event))"
              @keydown="onIngredientEnter($event, idx)"
            />
            <BaseDropdownMenu
              v-if="form.ingredients.length > 1"
              :aria-label="`ingredient ${idx + 1} actions`"
              placement="bottom"
            >
              <template #default="{ close: closeMenu }">
                <BaseDropdownMenuItem
                  v-if="idx > 0"
                  @select="
                    closeMenu();
                    moveIngredient(idx, -1);
                  "
                >
                  move up
                </BaseDropdownMenuItem>
                <BaseDropdownMenuItem
                  v-if="idx < form.ingredients.length - 1"
                  @select="
                    closeMenu();
                    moveIngredient(idx, 1);
                  "
                >
                  move down
                </BaseDropdownMenuItem>
                <BaseDropdownMenuItem
                  destructive
                  @select="
                    closeMenu();
                    removeIngredient(idx);
                  "
                >
                  remove
                </BaseDropdownMenuItem>
              </template>
            </BaseDropdownMenu>
          </li>
        </ul>
        <BaseButton variant="secondary" size="sm" type="button" @click="addIngredient">
          + ingredient
        </BaseButton>
      </div>

      <div class="space-y-2">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Steps</p>
        <ul role="list" class="space-y-2">
          <li
            v-for="(_, idx) in form.steps"
            :key="`step-${idx}`"
            class="flex min-w-0 items-start gap-2"
          >
            <span
              class="mt-2.5 inline-flex h-6 w-6 shrink-0 items-center justify-center text-xs text-surface-mid"
              aria-hidden="true"
            >
              {{ idx + 1 }}
            </span>
            <BaseTextarea
              :model-value="form.steps[idx]"
              class="min-w-0 flex-1"
              :rows="2"
              placeholder="Preheat oven to 200°C"
              :aria-label="`step ${idx + 1}`"
              data-recipe-step
              @update:model-value="updateStep(idx, String($event ?? ''))"
              @keydown="onStepModEnter($event, idx)"
            />
            <BaseDropdownMenu
              v-if="form.steps.length > 1"
              :aria-label="`step ${idx + 1} actions`"
              placement="bottom"
            >
              <template #default="{ close: closeMenu }">
                <BaseDropdownMenuItem
                  v-if="idx > 0"
                  @select="
                    closeMenu();
                    moveStep(idx, -1);
                  "
                >
                  move up
                </BaseDropdownMenuItem>
                <BaseDropdownMenuItem
                  v-if="idx < form.steps.length - 1"
                  @select="
                    closeMenu();
                    moveStep(idx, 1);
                  "
                >
                  move down
                </BaseDropdownMenuItem>
                <BaseDropdownMenuItem
                  destructive
                  @select="
                    closeMenu();
                    removeStep(idx);
                  "
                >
                  remove
                </BaseDropdownMenuItem>
              </template>
            </BaseDropdownMenu>
          </li>
        </ul>
        <p class="text-xs text-surface-muted">Ctrl/⌘ + Enter adds the next step</p>
        <BaseButton variant="secondary" size="sm" type="button" @click="addStep">
          + step
        </BaseButton>
      </div>

      <BaseInput
        :model-value="form.tags"
        placeholder="tags · italian, vegetarian"
        aria-label="tags"
        @update:model-value="patch({ tags: toStringValue($event) })"
      />

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
