<script setup lang="ts">
import { nextTick, ref } from "vue";

export interface OrbitTab {
  id: string;
  label: string;
}

const activeTab = defineModel<string>({ required: true });
const tablistRef = ref<HTMLElement | null>(null);

const props = withDefaults(
  defineProps<{
    tabs: OrbitTab[];
    panelIdPrefix?: string;
    /** Drop bottom margin when the bar sits in a shared chrome row. */
    flush?: boolean;
    ariaLabel?: string;
  }>(),
  {
    panelIdPrefix: "admin-tab",
    flush: false,
    ariaLabel: "expense sections",
  },
);

/** Subtle vertical stagger on md+ so the row reads as an orbit without a canvas. */
const STAGGER_CLASS = [
  "md:translate-y-0",
  "md:translate-y-1",
  "md:-translate-y-1",
  "md:translate-y-2",
  "md:-translate-y-0.5",
  "md:translate-y-1.5",
] as const;

function tabButtonId(tabId: string): string {
  return `${props.panelIdPrefix}-tab-${tabId}`;
}

function tabPanelId(tabId: string): string {
  return `${props.panelIdPrefix}-panel-${tabId}`;
}

function planetInitial(label: string): string {
  const trimmed = label.trim();
  return trimmed ? trimmed[0]!.toUpperCase() : "?";
}

function staggerClass(index: number): string {
  return STAGGER_CLASS[index % STAGGER_CLASS.length] ?? "md:translate-y-0";
}

function planetButtonClass(tabId: string): string {
  const selected = activeTab.value === tabId;
  const base =
    "flex size-11 shrink-0 cursor-pointer items-center justify-center rounded-full border text-sm font-semibold transition-[transform,background-color,border-color,color] duration-200 motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50";
  if (selected) {
    return `${base} scale-110 border-accent-blue/40 bg-accent-blue/15 text-accent-blue`;
  }
  // Stronger fill so discs read on the photo scrim.
  return `${base} border-transparent bg-surface-dark/90 text-surface-mid hover:bg-surface-border/80 hover:text-surface-light`;
}

function labelClass(tabId: string): string {
  const selected = activeTab.value === tabId;
  return selected
    ? "max-w-[5.5rem] truncate text-center text-xs font-medium text-surface-light"
    : "max-w-[5.5rem] truncate text-center text-xs text-surface-mid";
}

function activateTabAt(index: number, shouldFocus = false): void {
  const tab = props.tabs[index];
  if (!tab) return;
  activeTab.value = tab.id;
  if (!shouldFocus) return;

  void nextTick(() => {
    tablistRef.value?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[index]?.focus();
  });
}

function onTabKeydown(event: KeyboardEvent, index: number): void {
  if (props.tabs.length === 0) return;
  if (event.key === "Home") {
    event.preventDefault();
    activateTabAt(0, true);
    return;
  }
  if (event.key === "End") {
    event.preventDefault();
    activateTabAt(props.tabs.length - 1, true);
    return;
  }
  if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;

  event.preventDefault();
  const direction = event.key === "ArrowRight" ? 1 : -1;
  const nextIndex = (index + direction + props.tabs.length) % props.tabs.length;
  activateTabAt(nextIndex, true);
}
</script>

<template>
  <div
    class="relative overflow-hidden rounded-lg p-3 sm:p-4"
    :class="flush ? undefined : 'mb-6'"
  >
    <img
      src="/expenses/orbit-earth.webp"
      alt=""
      aria-hidden="true"
      decoding="async"
      fetchpriority="low"
      width="1200"
      height="600"
      class="pointer-events-none absolute inset-0 size-full object-cover"
    />
    <!-- Scrim keeps labels/export readable on the photo in both themes. -->
    <div class="pointer-events-none absolute inset-0 bg-surface-dark/80" aria-hidden="true" />
    <span class="sr-only">Background: NASA Earth from orbit (public domain).</span>

    <div class="relative z-10 flex min-w-0 flex-wrap items-center gap-3">
      <div
        ref="tablistRef"
        class="flex min-w-0 flex-wrap items-end gap-x-3 gap-y-2"
        role="tablist"
        :aria-label="ariaLabel"
      >
        <div
          v-for="(tab, index) in tabs"
          :key="tab.id"
          class="flex flex-col items-center gap-1.5 transition-transform duration-200 motion-reduce:transition-none"
          :class="staggerClass(index)"
        >
          <button
            :id="tabButtonId(tab.id)"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.id"
            :aria-controls="tabPanelId(tab.id)"
            :tabindex="activeTab === tab.id ? 0 : -1"
            :class="planetButtonClass(tab.id)"
            @click="activeTab = tab.id"
            @keydown="onTabKeydown($event, index)"
          >
            <span aria-hidden="true">{{ planetInitial(tab.label) }}</span>
            <span class="sr-only">{{ tab.label }}</span>
          </button>
          <span :class="labelClass(tab.id)" aria-hidden="true">{{ tab.label }}</span>
        </div>
      </div>
      <div v-if="$slots.end" class="ml-auto flex shrink-0 items-center">
        <slot name="end" />
      </div>
    </div>
  </div>
</template>
