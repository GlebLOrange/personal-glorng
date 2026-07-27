<script setup lang="ts">
import { nextTick, ref } from "vue";

import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import {
  ACTION_PILL_BASE,
  actionFamilyClass,
  type HttpStatusFamily,
} from "@/constants/httpStatusColors";

export interface AdminTab {
  id: string;
  label: string;
  /** Pale HTTP-family color for hover/selected (default 1xx). */
  family?: HttpStatusFamily;
  /** Optional leading icon for sync/refresh tabs — paints the whole tab pale purple. */
  icon?: "sync" | "refresh";
}

const activeTab = defineModel<string>({ required: true });
const tablistRef = ref<HTMLElement | null>(null);

const props = withDefaults(
  defineProps<{
    tabs: AdminTab[];
    panelIdPrefix?: string;
    /** Drop bottom margin when the bar sits in a shared chrome row. */
    flush?: boolean;
    ariaLabel?: string;
  }>(),
  {
    panelIdPrefix: "admin-tab",
    flush: false,
    ariaLabel: "Admin sections",
  },
);

/** Sync/refresh tabs use marketing violet wash (full chip, not icon-only). */
function violetTabClass(selected: boolean): string {
  if (selected) {
    return `${ACTION_PILL_BASE} bg-accent-violet/15 border-accent-violet/40 text-accent-violet`;
  }
  return `${ACTION_PILL_BASE} border-transparent bg-accent-violet/3 text-accent-violet hover:enabled:border-accent-violet/40 hover:enabled:bg-accent-violet/15`;
}

const tabClass = (tab: AdminTab): string => {
  const selected = activeTab.value === tab.id;
  if (tab.icon === "sync" || tab.icon === "refresh") {
    return violetTabClass(selected);
  }
  return actionFamilyClass(tab.family ?? "1xx", selected);
};

function tabButtonId(tabId: string): string {
  return `${props.panelIdPrefix}-tab-${tabId}`;
}

function tabPanelId(tabId: string): string {
  return `${props.panelIdPrefix}-panel-${tabId}`;
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
  <div class="flex min-w-0 flex-wrap items-center gap-2" :class="flush ? undefined : 'mb-6'">
    <div
      ref="tablistRef"
      class="flex flex-wrap gap-2"
      role="tablist"
      :aria-label="ariaLabel"
    >
      <button
        v-for="(tab, index) in tabs"
        :id="tabButtonId(tab.id)"
        :key="tab.id"
        type="button"
        role="tab"
        :aria-selected="activeTab === tab.id"
        :aria-controls="tabPanelId(tab.id)"
        :tabindex="activeTab === tab.id ? 0 : -1"
        :class="tabClass(tab)"
        @click="activeTab = tab.id"
        @keydown="onTabKeydown($event, index)"
      >
        <SyncIcon v-if="tab.icon === 'sync'" class-name="size-3.5 shrink-0" />
        <RefreshIcon v-else-if="tab.icon === 'refresh'" class-name="size-3.5 shrink-0" />
        {{ tab.label }}
      </button>
    </div>
    <div v-if="$slots.end" class="ml-auto flex shrink-0 items-center">
      <slot name="end" />
    </div>
  </div>
</template>
