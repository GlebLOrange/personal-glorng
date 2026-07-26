<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";

const props = defineProps<{
  steps: string[];
  /** Drawer open flag — resets details open state when the form opens. */
  formOpen: boolean;
}>();

const emit = defineEmits<{
  "update:steps": [value: string[]];
}>();

/** Filled (trimmed) lines — same filter as save. */
function filledCount(items: string[]): number {
  return items.map((item) => item.trim()).filter(Boolean).length;
}

const stepCount = computed(() => filledCount(props.steps));

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

function patch(steps: string[]): void {
  emit("update:steps", steps);
}

async function focusField(index: number): Promise<void> {
  await nextTick();
  const fields = document.querySelectorAll<HTMLElement>("[data-recipe-step]");
  fields[index]?.focus();
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

function moveStep(index: number, direction: -1 | 1): void {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= props.steps.length) return;
  const steps = [...props.steps];
  [steps[index], steps[nextIndex]] = [steps[nextIndex], steps[index]];
  patch(steps);
}

function onStepModEnter(event: KeyboardEvent, index: number): void {
  if (event.key !== "Enter" || !(event.metaKey || event.ctrlKey)) return;
  event.preventDefault();
  const steps = [...props.steps];
  steps.splice(index + 1, 0, "");
  patch(steps);
  void focusField(index + 1);
}

function splitPasteLines(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function onStepPaste(event: ClipboardEvent, index: number): void {
  const lines = splitPasteLines(event.clipboardData?.getData("text") ?? "");
  if (lines.length < 2) return;
  event.preventDefault();
  const steps = [...props.steps];
  steps.splice(index, 1, ...lines);
  patch(steps);
  void focusField(index + lines.length - 1);
}
</script>

<template>
  <details ref="detailsRef" class="group rounded border border-surface-border" open>
    <summary
      class="flex h-8 cursor-pointer list-none items-center gap-1.5 px-2 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
    >
      <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
      steps ({{ stepCount }})
    </summary>
    <div class="space-y-1 border-t border-surface-border px-2 py-2">
      <ul role="list" class="space-y-1">
        <li
          v-for="(_, idx) in steps"
          :key="`step-${idx}`"
          class="flex min-w-0 items-start gap-1"
        >
          <span
            class="inline-flex h-8 w-5 shrink-0 items-center justify-center text-xs text-surface-mid"
            aria-hidden="true"
          >
            {{ idx + 1 }}
          </span>
          <BaseTextarea
            compact
            :model-value="steps[idx]"
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
            v-if="steps.length > 1"
            :aria-label="`remove step ${idx + 1}`"
            @click="removeStep(idx)"
          />
          <BaseDropdownMenu
            v-if="steps.length > 1"
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
                v-if="idx < steps.length - 1"
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
      <IconActionButton type="button" title="add step" aria-label="add step" @click="addStep">
        +
      </IconActionButton>
    </div>
  </details>
</template>
