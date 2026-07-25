<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { useOverlayShell } from "@/composables/useOverlayShell";
import type { Recipe } from "@/types";

const props = defineProps<{
  recipe: Recipe | null;
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const panelRef = ref<HTMLElement | null>(null);
const exitButton = ref<InstanceType<typeof BaseButton> | null>(null);
const stepIndex = ref(0);
const showIngredients = ref(false);
let wakeLock: { release: () => Promise<void> } | null = null;

const currentStep = computed(() => props.recipe?.steps[stepIndex.value] ?? "");
const totalSteps = computed(() => props.recipe?.steps.length ?? 0);
const progress = computed(() =>
  totalSteps.value ? ((stepIndex.value + 1) / totalSteps.value) * 100 : 0,
);
const dialogLabel = computed(() =>
  props.recipe ? `Cook mode: ${props.recipe.title}` : "Cook mode",
);

useOverlayShell({
  open: () => props.open && Boolean(props.recipe),
  panelRef,
  onClose: () => emit("close"),
  initialFocusFallback: () => {
    const el = exitButton.value?.$el;
    return el instanceof HTMLElement ? el : null;
  },
});

async function requestWakeLock(): Promise<void> {
  if (!("wakeLock" in navigator)) return;
  try {
    wakeLock = await navigator.wakeLock.request("screen");
  } catch {
    /* unsupported or denied */
  }
}

async function releaseWakeLock(): Promise<void> {
  if (!wakeLock) return;
  try {
    await wakeLock.release();
  } catch {
    /* ignore */
  }
  wakeLock = null;
}

function goPrev(): void {
  if (stepIndex.value > 0) stepIndex.value -= 1;
}

function goNext(): void {
  if (stepIndex.value < totalSteps.value - 1) stepIndex.value += 1;
}

function onKeydown(event: KeyboardEvent): void {
  if (!props.open) return;
  if (event.key === "ArrowLeft") goPrev();
  if (event.key === "ArrowRight") goNext();
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      stepIndex.value = 0;
      showIngredients.value = false;
      void requestWakeLock();
      return;
    }
    void releaseWakeLock();
  },
);

watch(
  () => props.recipe?.id,
  () => {
    stepIndex.value = 0;
  },
);

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
  void releaseWakeLock();
});
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open && recipe"
        ref="panelRef"
        role="dialog"
        aria-modal="true"
        :aria-label="dialogLabel"
        tabindex="-1"
        class="fixed inset-0 z-[60] bg-surface-dark flex flex-col focus:outline-none"
      >
        <header class="flex items-center justify-between px-4 py-3 border-b border-surface-border">
          <div class="min-w-0">
            <p class="text-xs text-surface-mid truncate">{{ recipe.title }}</p>
            <p class="text-sm text-accent-blue">Step {{ stepIndex + 1 }} of {{ totalSteps }}</p>
          </div>
          <BaseButton
            ref="exitButton"
            type="button"
            variant="ghost"
            quiet
            size="sm"
            class="shrink-0 ml-4"
            @click="emit('close')"
          >
            Exit cook mode
          </BaseButton>
        </header>

        <div class="h-1 bg-surface-border">
          <div
            class="h-full bg-accent-blue transition-all duration-300"
            :style="{ width: `${progress}%` }"
          />
        </div>

        <div class="px-4 py-2 border-b border-surface-border">
          <BaseButton
            type="button"
            variant="ghost"
            quiet
            size="sm"
            @click="showIngredients = !showIngredients"
          >
            {{ showIngredients ? "Hide" : "Show" }} ingredients ({{ recipe.ingredients.length }})
          </BaseButton>
          <ul
            v-if="showIngredients"
            class="mt-2 text-sm text-surface-light space-y-1 max-h-32 overflow-y-auto"
          >
            <li
              v-for="(ing, i) in recipe.ingredients"
              :key="i"
              class="before:content-['·_'] before:text-accent-blue"
            >
              {{ ing }}
            </li>
          </ul>
        </div>

        <main class="flex-1 flex flex-col items-center justify-center px-6 py-8 text-center">
          <div class="text-5xl font-mono text-accent-blue mb-6">{{ stepIndex + 1 }}</div>
          <p class="text-xl sm:text-2xl text-surface-light leading-relaxed max-w-2xl">
            {{ currentStep }}
          </p>
        </main>

        <footer
          class="flex items-center justify-between gap-4 px-4 py-4 border-t border-surface-border"
        >
          <BaseButton variant="ghost" :disabled="stepIndex === 0" @click="goPrev">
            previous
          </BaseButton>
          <BaseButton v-if="stepIndex < totalSteps - 1" variant="primary" @click="goNext">
            next
          </BaseButton>
          <BaseButton v-else variant="primary" @click="emit('close')">done</BaseButton>
        </footer>
      </div>
    </Transition>
  </Teleport>
</template>
