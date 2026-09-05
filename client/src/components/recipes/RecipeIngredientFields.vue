<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";

const props = defineProps<{
  ingredients: string[];
  /** Drawer open flag — resets details open state when the form opens. */
  formOpen: boolean;
}>();

const emit = defineEmits<{
  "update:ingredients": [value: string[]];
}>();

/** Filled (trimmed) lines — same filter as save. */
function filledCount(items: string[]): number {
  return items.map((item) => item.trim()).filter(Boolean).length;
}

const ingredientCount = computed(() => filledCount(props.ingredients));

// Uncontrolled <details>; set .open on drawer open so Vue doesn't fight native toggles.
const detailsRef = ref<HTMLDetailsElement | null>(null);

watch(
  () => props.formOpen,
  async (isOpen) => {
    if (!isOpen) return;
    await nextTick();
    if (detailsRef.value) detailsRef.value.open = true;
  },
);

function patch(ingredients: string[]): void {
  emit("update:ingredients", ingredients);
}

async function focusField(index: number): Promise<void> {
  await nextTick();
  const fields = document.querySelectorAll<HTMLElement>("[data-recipe-ingredient]");
  fields[index]?.focus();
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}

function addIngredient(): void {
  patch([...props.ingredients, ""]);
  void focusField(props.ingredients.length);
}

function removeIngredient(index: number): void {
  if (props.ingredients.length <= 1) return;
  patch(props.ingredients.filter((_, i) => i !== index));
}

function updateIngredient(index: number, value: string): void {
  const ingredients = [...props.ingredients];
  ingredients[index] = value;
  patch(ingredients);
}

function moveIngredient(index: number, direction: -1 | 1): void {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= props.ingredients.length) return;
  const ingredients = [...props.ingredients];
  [ingredients[index], ingredients[nextIndex]] = [ingredients[nextIndex], ingredients[index]];
  patch(ingredients);
}

function onIngredientEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter") return;
  event.preventDefault();
  // Insert after current row so Enter mid-list adds the next line in place.
  const ingredients = [...props.ingredients];
  ingredients.splice(index + 1, 0, "");
  patch(ingredients);
  void focusField(index + 1);
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
  const ingredients = [...props.ingredients];
  ingredients.splice(index, 1, ...lines);
  patch(ingredients);
  void focusField(index + lines.length - 1);
}
</script>

<template>
  <details ref="detailsRef" class="group rounded border border-surface-border" open>
    <summary
      class="flex h-8 cursor-pointer list-none items-center gap-1.5 px-2 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
    >
      <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
      ingredients ({{ ingredientCount }})
    </summary>
    <div class="space-y-1 border-t border-surface-border px-2 py-2">
      <ul role="list" class="space-y-1">
        <li
          v-for="(_, idx) in ingredients"
          :key="`ingredient-${idx}`"
          class="flex min-w-0 items-center gap-1"
        >
          <BaseInput
            compact
            :model-value="ingredients[idx]"
            class="min-w-0 flex-1"
            placeholder="200g flour"
            :aria-label="`ingredient ${idx + 1}`"
            data-recipe-ingredient
            @update:model-value="updateIngredient(idx, toStringValue($event))"
            @keydown="onIngredientEnter($event, idx)"
            @paste="onIngredientPaste($event, idx)"
          />
          <IconCloseButton
            v-if="ingredients.length > 1"
            :aria-label="`remove ingredient ${idx + 1}`"
            @click="removeIngredient(idx)"
          />
          <IconActionButton
            v-if="idx > 0"
            type="button"
            quiet
            :title="`move ingredient ${idx + 1} up`"
            :aria-label="`move ingredient ${idx + 1} up`"
            @click="moveIngredient(idx, -1)"
          >
            ↑
          </IconActionButton>
        </li>
      </ul>
      <IconActionButton
        type="button"
        title="add ingredient"
        aria-label="add ingredient"
        @click="addIngredient"
      >
        +
      </IconActionButton>
    </div>
  </details>
</template>
