<script setup lang="ts">
import { nextTick, ref } from "vue";

export interface AdminTab {
  id: string;
  label: string;
}

const activeTab = defineModel<string>({ required: true });
const tablistRef = ref<HTMLElement | null>(null);

const props = defineProps<{
  tabs: AdminTab[];
}>();

const tabClass = (id: string): string =>
  [
    "px-3 py-1.5 text-xs rounded-lg transition-colors",
    activeTab.value === id
      ? "bg-accent-blue/20 text-accent-blue"
      : "text-surface-mid hover:text-surface-light",
  ].join(" ");

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
    ref="tablistRef"
    class="flex flex-wrap gap-2 mb-6"
    role="tablist"
    aria-label="Admin sections"
  >
    <button
      v-for="(tab, index) in tabs"
      :key="tab.id"
      type="button"
      role="tab"
      :aria-selected="activeTab === tab.id"
      :tabindex="activeTab === tab.id ? 0 : -1"
      :class="tabClass(tab.id)"
      @click="activeTab = tab.id"
      @keydown="onTabKeydown($event, index)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>
