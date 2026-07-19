<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, useTemplateRef, watch } from "vue";

const props = withDefaults(
  defineProps<{
    /** Accessible name for the icon trigger (required for icon-only defaults). */
    ariaLabel?: string;
  }>(),
  {
    ariaLabel: "Actions",
  },
);

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<HTMLButtonElement>("trigger");
const menuRef = useTemplateRef<HTMLElement>("menu");
let previouslyFocused: HTMLElement | null = null;

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
  <div ref="root" class="relative inline-flex">
    <button
      ref="trigger"
      type="button"
      class="text-surface-mid hover:text-surface-light transition-colors p-1 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      aria-haspopup="menu"
      :aria-expanded="open"
      :aria-label="props.ariaLabel"
      @click.stop="toggle"
    >
      <slot name="trigger">
        <span class="text-lg leading-none" aria-hidden="true">⋮</span>
      </slot>
    </button>

    <div
      v-if="open"
      ref="menu"
      role="menu"
      class="absolute right-0 top-full mt-1 z-10 bg-surface-card border border-surface-border rounded-lg shadow-lg py-1 min-w-[10rem]"
      @click.stop
    >
      <slot :close="onItemSelect" />
    </div>
  </div>
</template>
