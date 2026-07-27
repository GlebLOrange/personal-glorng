<script setup lang="ts">
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
  useSlots,
  useTemplateRef,
  watch,
} from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import { actionFamilyClass, iconActionClass } from "@/constants/httpStatusColors";

const props = withDefaults(
  defineProps<{
    /** Accessible name for the icon trigger (required for icon-only defaults). */
    ariaLabel?: string;
    /** Menu opens below (default) or above the trigger. */
    placement?: "bottom" | "top";
  }>(),
  {
    ariaLabel: "Actions",
    placement: "bottom",
  },
);

const slots = useSlots();
const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<HTMLButtonElement>("trigger");
const menuRef = useTemplateRef<HTMLElement>("menu");
let previouslyFocused: HTMLElement | null = null;

const hasCustomTrigger = computed(() => Boolean(slots.trigger));

const menuPositionClass = computed(() =>
  props.placement === "top" ? "bottom-full mb-1" : "top-full mt-1",
);

const triggerClass = computed(() => {
  if (hasCustomTrigger.value) {
    // Labeled triggers (e.g. more actions) match ToolbarPillButton h-11.
    return actionFamilyClass("1xx", open.value);
  }
  // Icon-only default — h-11 square chrome.
  return iconActionClass("1xx", open.value);
});

function getMenuItems(): HTMLElement[] {
  const menu = menuRef.value;
  if (!menu) return [];
  return Array.from(menu.querySelectorAll<HTMLElement>('[role="menuitem"]')).filter(
    (item) => item.tabIndex >= 0 && !item.hasAttribute("disabled"),
  );
}

function focusItem(index: number): void {
  const items = getMenuItems();
  if (items.length === 0) return;
  const normalized = ((index % items.length) + items.length) % items.length;
  items[normalized]?.focus();
}

function toggle(): void {
  open.value = !open.value;
}

function close(): void {
  open.value = false;
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

  const items = getMenuItems();
  if (items.length === 0) return;
  const activeIndex = items.findIndex((item) => item === document.activeElement);

  if (event.key === "ArrowDown") {
    event.preventDefault();
    focusItem(activeIndex < 0 ? 0 : activeIndex + 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    focusItem(activeIndex < 0 ? items.length - 1 : activeIndex - 1);
  } else if (event.key === "Home") {
    event.preventDefault();
    focusItem(0);
  } else if (event.key === "End") {
    event.preventDefault();
    focusItem(items.length - 1);
  }
}

function onItemSelect(): void {
  close();
}

watch(open, async (isOpen) => {
  if (isOpen) {
    previouslyFocused = document.activeElement as HTMLElement | null;
    await nextTick();
    focusItem(0);
    return;
  }
  const restore = previouslyFocused ?? triggerRef.value;
  previouslyFocused = null;
  restore?.focus();
});

onMounted(() => {
  // Capture: drawer panels use @click.stop, which blocks bubble-phase document listeners.
  document.addEventListener("click", onDocumentClick, true);
  document.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick, true);
  document.removeEventListener("keydown", onKeydown);
});

defineExpose({ close });
</script>

<template>
  <div ref="root" class="relative inline-flex">
    <button
      ref="trigger"
      type="button"
      :class="triggerClass"
      aria-haspopup="menu"
      :aria-expanded="open"
      :aria-label="hasCustomTrigger ? undefined : props.ariaLabel"
      :title="props.ariaLabel"
      @click.stop="toggle"
    >
      <span class="inline-flex items-center gap-1.5">
        <slot name="trigger" :open="open" />
        <ChevronIcon :open="open" />
      </span>
    </button>

    <div
      v-if="open"
      ref="menu"
      role="menu"
      :class="[
        'absolute right-0 z-10 min-w-[10rem] rounded-lg border border-surface-border bg-surface-card py-1 shadow-lg',
        menuPositionClass,
      ]"
      @click.stop
    >
      <slot :close="onItemSelect" />
    </div>
  </div>
</template>
