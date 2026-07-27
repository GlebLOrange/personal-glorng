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
import {
  actionFamilyClass,
  iconActionClass,
  type HttpStatusFamily,
} from "@/constants/httpStatusColors";

const props = withDefaults(
  defineProps<{
    /** Accessible name for the icon trigger (required for icon-only defaults). */
    ariaLabel?: string;
    /** Menu opens below (default) or above the trigger. */
    placement?: "bottom" | "top";
    /** Custom `#trigger` is an icon (no chevron / labeled width). */
    iconOnly?: boolean;
    /** Trigger paint family — edit menus use 3xx (pale yellow) to match IconEditButton. */
    family?: HttpStatusFamily;
  }>(),
  {
    ariaLabel: "Actions",
    placement: "bottom",
    iconOnly: false,
    family: "1xx",
  },
);

const slots = useSlots();
const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<HTMLButtonElement>("trigger");
const menuRef = useTemplateRef<HTMLElement>("menu");
/** Shared min width so trigger and menu stay aligned (no jump). */
const sharedMinWidthPx = ref<number | null>(null);
let previouslyFocused: HTMLElement | null = null;
let shouldRestoreFocus = true;

const hasCustomTrigger = computed(() => Boolean(slots.trigger));
const isLabeledTrigger = computed(() => hasCustomTrigger.value && !props.iconOnly);

const menuPositionClass = computed(() =>
  props.placement === "top" ? "bottom-full mb-1" : "top-full mt-1",
);

const triggerClass = computed(() => {
  if (isLabeledTrigger.value) {
    // Labeled triggers (e.g. more actions) match ToolbarPillButton h-10.
    return [actionFamilyClass(props.family, open.value), "w-full"];
  }
  // Icon-only — h-10 square chrome.
  return iconActionClass(props.family, open.value);
});

const rootStyle = computed(() =>
  sharedMinWidthPx.value != null ? { minWidth: `${sharedMinWidthPx.value}px` } : undefined,
);

function getMenuItems(): HTMLElement[] {
  const menu = menuRef.value;
  if (!menu) return [];
  return Array.from(menu.querySelectorAll<HTMLElement>('[role="menuitem"]')).filter(
    (item) => item.tabIndex >= 0 && !item.hasAttribute("disabled"),
  );
}

function longestMenuItemWidth(menu: HTMLElement): number {
  let longest = 0;
  for (const item of menu.querySelectorAll<HTMLElement>('[role="menuitem"]')) {
    const previousWidth = item.style.width;
    const previousMinWidth = item.style.minWidth;
    item.style.width = "max-content";
    item.style.minWidth = "max-content";
    longest = Math.max(longest, item.getBoundingClientRect().width);
    item.style.width = previousWidth;
    item.style.minWidth = previousMinWidth;
  }
  return longest;
}

function syncSharedMinWidth(): void {
  // Icon-only triggers stay square; only labeled menus share width with items.
  if (!isLabeledTrigger.value) return;
  const menu = menuRef.value;
  const trigger = triggerRef.value;
  if (!menu || !trigger) return;

  const triggerWidth = trigger.getBoundingClientRect().width;
  const itemWidth = longestMenuItemWidth(menu);
  // Menu chrome: horizontal padding/margins around items (~0.5rem each side).
  const menuChrome = 16;
  const next = Math.ceil(Math.max(triggerWidth, itemWidth + menuChrome));
  if (sharedMinWidthPx.value == null || next > sharedMinWidthPx.value) {
    sharedMinWidthPx.value = next;
  }
}

function focusItem(index: number): void {
  const items = getMenuItems();
  if (items.length === 0) return;
  const normalized = ((index % items.length) + items.length) % items.length;
  items[normalized]?.focus();
}

function toggle(): void {
  if (open.value) {
    close();
    return;
  }
  open.value = true;
}

function close(restoreFocus = true): void {
  shouldRestoreFocus = restoreFocus;
  open.value = false;
}

function onDocumentClick(event: MouseEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  if (root && !root.contains(event.target as Node)) {
    close(false);
  }
}

function onFocusOut(event: FocusEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  const nextTarget = event.relatedTarget;
  if (root && nextTarget instanceof Node && root.contains(nextTarget)) return;
  close(false);
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
    shouldRestoreFocus = true;
    await nextTick();
    syncSharedMinWidth();
    focusItem(0);
    return;
  }
  const restore = shouldRestoreFocus ? (previouslyFocused ?? triggerRef.value) : null;
  previouslyFocused = null;
  shouldRestoreFocus = true;
  restore?.focus();
});

onMounted(async () => {
  // Capture: drawer panels use @click.stop, which blocks bubble-phase document listeners.
  document.addEventListener("click", onDocumentClick, true);
  document.addEventListener("keydown", onKeydown);
  await nextTick();
  // Menu stays mounted (invisible when closed) so we can size the trigger up front.
  syncSharedMinWidth();
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick, true);
  document.removeEventListener("keydown", onKeydown);
});

defineExpose({ close });
</script>

<template>
  <div ref="root" class="relative inline-flex" :style="rootStyle" @focusout="onFocusOut">
    <button
      ref="trigger"
      type="button"
      :class="triggerClass"
      aria-haspopup="menu"
      :aria-expanded="open"
      :aria-label="props.ariaLabel"
      @click.stop="toggle"
    >
      <span class="inline-flex items-center gap-1.5">
        <slot name="trigger" :open="open" />
        <ChevronIcon v-if="!hasCustomTrigger || isLabeledTrigger" :open="open" />
      </span>
    </button>

    <div
      ref="menu"
      role="menu"
      :aria-hidden="!open"
      :class="[
        'absolute z-10 rounded-lg border border-surface-border bg-surface-card py-1 shadow-lg',
        isLabeledTrigger ? 'left-0 right-0' : 'right-0 min-w-[10rem]',
        open ? menuPositionClass : 'invisible pointer-events-none',
      ]"
      @click.stop
    >
      <slot :close="onItemSelect" />
    </div>
  </div>
</template>
