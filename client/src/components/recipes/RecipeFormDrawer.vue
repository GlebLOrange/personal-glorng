<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { RECIPE_TAG_LIMIT, RECIPE_TAG_SET, RECIPE_TAGS } from "@/constants/recipes";
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

/** Filled (trimmed) lines — same filter as save. */
function filledLines(items: string[]): string[] {
  return items.map((item) => item.trim()).filter(Boolean);
}

function filledCount(items: string[]): number {
  return filledLines(items).length;
}

function previewLabel(items: string[], max = 2): string {
  const filled = filledLines(items);
  if (filled.length === 0) return "";
  const shown = filled
    .slice(0, max)
    .map((line) => (line.length > 40 ? `${line.slice(0, 40)}…` : line));
  const extra = filled.length > max ? ` +${filled.length - max}` : "";
  return ` — ${shown.join(", ")}${extra}`;
}

const ingredientCount = computed(() => filledCount(props.form.ingredients));
const ingredientPreview = computed(() => previewLabel(props.form.ingredients));
const stepCount = computed(() => filledCount(props.form.steps));
const stepPreview = computed(() => previewLabel(props.form.steps));

const selectedTags = computed(() =>
  props.form.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean),
);

const selectedTagsLabel = computed(() =>
  selectedTags.value.length > 0 ? selectedTags.value.join(", ") : "none",
);

/** Catalog tags plus any selected custom/imported tags not in the curated list. */
const tagChoices = computed(() => {
  const extras = selectedTags.value.filter((tag) => !RECIPE_TAG_SET.has(tag));
  return [...RECIPE_TAGS, ...extras];
});

function tagIsSelected(tag: string): boolean {
  return selectedTags.value.includes(tag);
}

function toggleTag(tag: string): void {
  const tags = selectedTags.value;
  if (tags.includes(tag)) {
    patch({ tags: tags.filter((item) => item !== tag).join(", ") });
    return;
  }
  if (tags.length >= RECIPE_TAG_LIMIT) return;
  patch({ tags: [...tags, tag].join(", ") });
}

// Uncontrolled <details>; set .open on drawer open so Vue doesn't fight native toggles.
const ingredientsDetails = ref<HTMLDetailsElement | null>(null);
const stepsDetails = ref<HTMLDetailsElement | null>(null);
const tagsDetails = ref<HTMLDetailsElement | null>(null);

watch(
  () => props.open,
  async (isOpen) => {
    if (!isOpen) return;
    await nextTick();
    if (ingredientsDetails.value) ingredientsDetails.value.open = true;
    if (stepsDetails.value) stepsDetails.value.open = true;
    if (tagsDetails.value) tagsDetails.value.open = false;
  },
);

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

function splitPasteLines(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function onIngredientPaste(event: ClipboardEvent, index: number): void {
  const lines = splitPasteLines(event.clipboardData?.getData("text") ?? "");
  if (lines.length < 2) return;
  event.preventDefault();
  const ingredients = [...props.form.ingredients];
  ingredients.splice(index, 1, ...lines);
  patch({ ingredients });
  void focusField("[data-recipe-ingredient]", index + lines.length - 1);
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

function onStepPaste(event: ClipboardEvent, index: number): void {
  const lines = splitPasteLines(event.clipboardData?.getData("text") ?? "");
  if (lines.length < 2) return;
  event.preventDefault();
  const steps = [...props.form.steps];
  steps.splice(index, 1, ...lines);
  patch({ steps });
  void focusField("[data-recipe-step]", index + lines.length - 1);
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
        @update:model-value="patch({ title: toStringValue($event) })"
      />
      <BaseInput
        :model-value="form.image_url"
        placeholder="image url"
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
          @update:model-value="patch({ prep_time: toNullableNumber($event) })"
        />
        <BaseInput
          :model-value="form.cook_time"
          type="number"
          placeholder="cook · min"
          @update:model-value="patch({ cook_time: toNullableNumber($event) })"
        />
        <BaseInput
          :model-value="form.servings"
          type="number"
          placeholder="servings"
          @update:model-value="patch({ servings: toNullableNumber($event) })"
        />
      </div>

      <details
        ref="ingredientsDetails"
        class="group rounded border border-surface-border px-3 py-2"
        open
      >
        <summary
          class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          ingredients ({{ ingredientCount }})
          <span v-if="ingredientPreview" class="text-xs text-surface-muted">{{
            ingredientPreview
          }}</span>
        </summary>
        <div class="mt-3 space-y-2">
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
                @paste="onIngredientPaste($event, idx)"
              />
              <IconCloseButton
                v-if="form.ingredients.length > 1"
                :aria-label="`remove ingredient ${idx + 1}`"
                @click="removeIngredient(idx)"
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
                </template>
              </BaseDropdownMenu>
            </li>
          </ul>
          <p class="text-xs text-surface-muted">Enter adds the next ingredient</p>
          <BaseButton variant="secondary" size="sm" type="button" @click="addIngredient">
            + ingredient
          </BaseButton>
        </div>
      </details>

      <details ref="stepsDetails" class="group rounded border border-surface-border px-3 py-2" open>
        <summary
          class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          steps ({{ stepCount }})
          <span v-if="stepPreview" class="text-xs text-surface-muted">{{ stepPreview }}</span>
        </summary>
        <div class="mt-3 space-y-2">
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
                @paste="onStepPaste($event, idx)"
              />
              <IconCloseButton
                v-if="form.steps.length > 1"
                class="mt-1"
                :aria-label="`remove step ${idx + 1}`"
                @click="removeStep(idx)"
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
                </template>
              </BaseDropdownMenu>
            </li>
          </ul>
          <p class="text-xs text-surface-muted">Ctrl/⌘ + Enter adds the next step</p>
          <BaseButton variant="secondary" size="sm" type="button" @click="addStep">
            + step
          </BaseButton>
        </div>
      </details>

      <details ref="tagsDetails" class="group rounded border border-surface-border px-3 py-2">
        <summary
          class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          tags ({{ selectedTags.length }}/{{ RECIPE_TAG_LIMIT }})
          <span class="text-xs text-surface-muted"> — {{ selectedTagsLabel }}</span>
        </summary>
        <div class="mt-3 flex flex-wrap gap-2">
          <label
            v-for="tag in tagChoices"
            :key="tag"
            :for="`recipe-drawer-tag-${tag}`"
            class="inline-flex cursor-pointer items-center gap-2 rounded border border-surface-border px-3 py-1.5 text-xs transition-colors"
            :class="{
              'border-accent-blue text-surface-light': tagIsSelected(tag),
              'text-surface-mid': !tagIsSelected(tag),
              'opacity-50': !tagIsSelected(tag) && selectedTags.length >= RECIPE_TAG_LIMIT,
            }"
          >
            <input
              :id="`recipe-drawer-tag-${tag}`"
              type="checkbox"
              :checked="tagIsSelected(tag)"
              :disabled="!tagIsSelected(tag) && selectedTags.length >= RECIPE_TAG_LIMIT"
              @change="toggleTag(tag)"
            />
            {{ tag }}
          </label>
        </div>
      </details>

      <BaseTextarea
        :model-value="form.notes"
        :rows="3"
        placeholder="notes · tips, variations"
        @update:model-value="patch({ notes: String($event ?? '') })"
      />
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton danger type="button" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            type="submit"
            form="recipe-form-drawer-form"
            family="2xx"
            :disabled="loading"
          >
            {{ loading ? "saving..." : "save" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
