<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, useTemplateRef, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

withDefaults(
  defineProps<{
    hasActiveFilters?: boolean;
    activeLabel?: string;
    /** Trigger prefix text (e.g. "filters", "tags"). */
    label?: string;
  }>(),
  {
    label: "filters",
  },
);

const emit = defineEmits<{
  clear: [];
}>();

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<InstanceType<typeof ToolbarPillButton>>("trigger");
const panelRef = useTemplateRef<HTMLElement>("panel");
let previouslyFocused: HTMLElement | null = null;

function getFocusableElements(el: HTMLElement): HTMLElement[] {
  return Array.from(
    el.querySelectorAll<HTMLElement>(
      'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]',
    ),
  ).filter((item) => item.tabIndex >= 0);
}

function toggle(): void {
  open.value = !open.value;
}

function close(): void {
  open.value = false;
}

function onClear(): void {
  emit("clear");
  close();
}

function onDocumentClick(event: MouseEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  if (root && !root.contains(event.target as Node)) {
    close();
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (!open.value) return;

  if (event.key === "Escape") {
    event.stopPropagation();
    event.preventDefault();
    close();
    return;
  }

  if (event.key !== "Tab" || !panelRef.value) return;

  const focusables = getFocusableElements(panelRef.value);
  if (focusables.length === 0) {
    event.preventDefault();
    return;
  }

  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  const active = document.activeElement;

  if (event.shiftKey) {
    if (active === first || !panelRef.value.contains(active)) {
      last.focus();
      event.preventDefault();
    }
    return;
  }

  if (active === last || !panelRef.value.contains(active)) {
    first.focus();
    event.preventDefault();
  }
}

function focusTrigger(): void {
  const trigger = triggerRef.value;
  if (!trigger) return;
  const el = (trigger as unknown as { $el?: HTMLElement }).$el;
  if (el instanceof HTMLElement) {
    el.focus();
  }
}

watch(open, async (isOpen) => {
  if (isOpen) {
    previouslyFocused = document.activeElement as HTMLElement | null;
    await nextTick();
    const panel = panelRef.value;
    if (!panel) return;
    const focusables = getFocusableElements(panel);
    if (focusables.length > 0) {
      focusables[0].focus();
    } else {
      panel.focus();
    }
    return;
  }
  const restore = previouslyFocused;
  previouslyFocused = null;
  if (restore) {
    restore.focus();
  } else {
    focusTrigger();
  }
});

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKeydown);
});

defineExpose({ close });
</script>

<template>
  <div ref="root" class="relative inline-flex" :class="open ? 'z-40' : undefined">
    <ToolbarPillButton
      ref="trigger"
      family="1xx"
      :selected="open || hasActiveFilters"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      {{ label }}<span v-if="activeLabel" class="text-surface-muted"> · {{ activeLabel }}</span>
      <ChevronIcon :open="open" />
    </ToolbarPillButton>

    <div
      v-if="open"
      ref="panel"
      role="dialog"
      :aria-label="label"
      tabindex="-1"
      class="absolute left-0 top-full z-10 mt-1 w-max max-w-[min(100vw-2rem,36rem)] rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg"
      @click.stop
    >
      <div class="space-y-3">
        <div v-if="$slots.chips" class="flex flex-col gap-2">
          <slot name="chips" />
        </div>
        <slot />
      </div>
      <slot name="footer" />
      <div class="mt-3 flex flex-wrap justify-start gap-2">
        <BaseButton
          variant="ghost"
          danger
          size="sm"
          :disabled="!hasActiveFilters"
          @click="onClear"
        >
          clear
        </BaseButton>
      </div>
    </div>
  </div>
</template>
