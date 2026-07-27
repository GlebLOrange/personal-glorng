<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
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
const exitButton = ref<InstanceType<typeof IconCloseButton> | null>(null);
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
        class="fixed inset-0 z-[60] flex flex-col bg-surface-dark focus:outline-none"
      >
        <header class="flex items-center justify-between border-b border-surface-border px-4 py-3">
          <p class="min-w-0 truncate text-lg font-bold leading-none text-surface-light">
            {{ recipe.title }}
          </p>
          <IconCloseButton
            ref="exitButton"
            class="ml-4 shrink-0"
            aria-label="exit cook mode"
            @click="emit('close')"
          />
        </header>

        <div class="h-1 bg-surface-border">
          <div
            class="h-full bg-accent-blue transition-[width] duration-300"
            :style="{ width: `${progress}%` }"
          />
        </div>

        <div class="border-b border-surface-border px-4 py-2">
          <BaseButton
            type="button"
            variant="ghost"
            quiet
            size="sm"
            class="gap-1.5"
            @click="showIngredients = !showIngredients"
          >
            <ChevronIcon :open="showIngredients" />
            {{ showIngredients ? "hide" : "show" }} ingredients ({{ recipe.ingredients.length }})
          </BaseButton>
          <ul
            v-if="showIngredients"
            class="mt-2 max-h-32 space-y-1 overflow-y-auto text-sm text-surface-light"
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

        <div
          class="flex flex-1 flex-col items-center justify-center px-6 py-8 text-center"
          role="region"
          aria-label="Cook mode step"
        >
          <div class="mb-6 font-data text-5xl text-accent-blue">{{ stepIndex + 1 }}</div>
          <p class="max-w-2xl text-xl leading-relaxed text-surface-light sm:text-2xl">
            {{ currentStep }}
          </p>
        </div>

        <footer
          class="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-t border-surface-border px-4 py-4"
        >
          <IconActionButton
            family="1xx"
            :disabled="stepIndex === 0"
            aria-label="previous"
            title="previous"
            @click="goPrev"
          >
            &lt;
          </IconActionButton>
          <p class="min-w-0 text-center text-sm text-accent-blue">
            step {{ stepIndex + 1 }} of {{ totalSteps }}
          </p>
          <IconActionButton
            v-if="stepIndex < totalSteps - 1"
            family="1xx"
            aria-label="next"
            title="next"
            @click="goNext"
          >
            &gt;
          </IconActionButton>
          <IconCloseButton v-else aria-label="done" @click="emit('close')" />
        </footer>
      </div>
    </Transition>
  </Teleport>
</template>
