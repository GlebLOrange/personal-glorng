<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import {
  filledListCount,
  focusRecipeListField,
  insertBlankAfter,
  replaceWithPasteLines,
  splitPasteLines,
} from "@/utils/recipeListFields";

const FIELD_SELECTOR = "[data-recipe-step]";

const props = defineProps<{
  steps: string[];
  /** Drawer open flag — resets details open state when the form opens. */
  formOpen: boolean;
}>();

const emit = defineEmits<{
  "update:steps": [value: string[]];
}>();

const stepCount = computed(() => filledListCount(props.steps));

// Uncontrolled <details>; set .open on drawer open so Vue doesn't fight native toggles.
const detailsRef = ref<HTMLDetailsElement | null>(null);

watch(
  () => props.formOpen,
  async (isOpen) => {
    if (!isOpen) return;
    await nextTick();
    if (detailsRef.value) detailsRef.value.open = false;
  },
);

function patch(steps: string[]): void {
  emit("update:steps", steps);
}

async function focusField(index: number): Promise<void> {
  await focusRecipeListField(detailsRef.value, FIELD_SELECTOR, index);
}

function addStep(): void {
  patch([...props.steps, ""]);
  void focusField(props.steps.length);
}

function removeStep(index: number): void {
  if (props.steps.length <= 1) return;
  patch(props.steps.filter((_, i) => i !== index));
}

function updateStep(index: number, value: string): void {
  const steps = [...props.steps];
  steps[index] = value;
  patch(steps);
}

function onStepModEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter" || !(event.metaKey || event.ctrlKey)) return;
  event.preventDefault();
  patch(insertBlankAfter(props.steps, index));
  void focusField(index + 1);
}

function onStepPaste(event: ClipboardEvent, index: number): void {
  const lines = splitPasteLines(event.clipboardData?.getData("text") ?? "");
  if (lines.length < 2) return;
  event.preventDefault();
  patch(replaceWithPasteLines(props.steps, index, lines));
  void focusField(index + lines.length - 1);
}
</script>

<template>
  <details ref="detailsRef" class="group rounded border border-surface-border">
    <summary
      class="flex h-8 cursor-pointer list-none items-center gap-1.5 px-2 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
    >
      <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
      steps ({{ stepCount }})
    </summary>
    <div class="space-y-1 border-t border-surface-border px-2 py-2">
      <ul role="list" class="space-y-1">
        <li v-for="(_, idx) in steps" :key="`step-${idx}`" class="flex min-w-0 items-start gap-1">
          <span
            class="inline-flex h-8 w-5 shrink-0 items-center justify-center text-xs text-surface-mid"
            aria-hidden="true"
          >
            {{ idx + 1 }}
          </span>
          <IconActionButton
            v-if="idx === steps.length - 1"
            type="button"
            title="add step"
            aria-label="add step"
            @click="addStep"
          >
            +
          </IconActionButton>
          <span
            v-else
            class="box-border h-10 w-10 min-w-10 shrink-0"
            aria-hidden="true"
          />
          <BaseTextarea
            compact
            :model-value="steps[idx]"
            class="min-w-0 w-full flex-1"
            :rows="2"
            placeholder="Preheat oven to 200°C"
            :aria-label="`step ${idx + 1}`"
            data-recipe-step
            @update:model-value="updateStep(idx, String($event ?? ''))"
            @keydown="onStepModEnter($event, idx)"
            @paste="onStepPaste($event, idx)"
          />
          <IconCloseButton
            v-if="steps.length > 1"
            :aria-label="`remove step ${idx + 1}`"
            @click="removeStep(idx)"
          />
        </li>
      </ul>
    </div>
  </details>
</template>
