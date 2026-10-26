<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";
import { SMALL_TOOL_TABS, type SmallToolTab } from "@/constants/smallToolTabs";
import { actionFamilyClass } from "@/constants/httpStatusColors";

const route = useRoute();
const router = useRouter();
const tablistRef = ref<HTMLElement | null>(null);

const activeTab = computed(
  () => SMALL_TOOL_TABS.find((tab) => tab.name === route.name) ?? SMALL_TOOL_TABS[0],
);

const pageTitle = computed(() => {
  const metaTitle = route.meta.title;
  return typeof metaTitle === "string" && metaTitle ? metaTitle : (activeTab.value?.label ?? "Tools");
});

function tabButtonId(tabId: string): string {
  return `small-tools-tab-${tabId}`;
}

function tabPanelId(tabId: string): string {
  return `small-tools-panel-${tabId}`;
}

function tabClass(tab: SmallToolTab): string {
  return actionFamilyClass("1xx", activeTab.value?.id === tab.id);
}

async function activateTabAt(index: number, shouldFocus = false): Promise<void> {
  const tab = SMALL_TOOL_TABS[index];
  if (!tab) return;
  await router.push(tab.to);
  if (!shouldFocus) return;
  await nextTick();
  tablistRef.value?.querySelectorAll<HTMLElement>('[role="tab"]')[index]?.focus();
}

function onTabKeydown(event: KeyboardEvent, index: number): void {
  if (SMALL_TOOL_TABS.length === 0) return;
  if (event.key === "Home") {
    event.preventDefault();
    void activateTabAt(0, true);
    return;
  }
  if (event.key === "End") {
    event.preventDefault();
    void activateTabAt(SMALL_TOOL_TABS.length - 1, true);
    return;
  }
  if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;

  event.preventDefault();
  const direction = event.key === "ArrowRight" ? 1 : -1;
  const nextIndex = (index + direction + SMALL_TOOL_TABS.length) % SMALL_TOOL_TABS.length;
  void activateTabAt(nextIndex, true);
}
</script>

<template>
  <div class="mx-auto w-full max-w-sm space-y-4 px-6 py-6">
    <div class="relative flex h-10 items-center">
      <h1 class="pr-14 text-left text-2xl font-bold leading-none text-surface-light">
        <span class="accent-gradient">{{ pageTitle }}</span>
      </h1>
      <BackLink to="/tools" class="absolute right-0 top-1/2 -translate-y-1/2" />
    </div>

    <PinnedToolsRow />

    <div
      ref="tablistRef"
      class="flex flex-wrap gap-2"
      role="tablist"
      aria-label="small tools"
    >
      <RouterLink
        v-for="(tab, index) in SMALL_TOOL_TABS"
        :id="tabButtonId(tab.id)"
        :key="tab.id"
        :to="tab.to"
        role="tab"
        :aria-selected="activeTab?.id === tab.id"
        :aria-controls="tabPanelId(tab.id)"
        :tabindex="activeTab?.id === tab.id ? 0 : -1"
        :class="tabClass(tab)"
        @keydown="onTabKeydown($event, index)"
      >
        {{ tab.label }}
      </RouterLink>
    </div>

    <div
      :id="activeTab ? tabPanelId(activeTab.id) : undefined"
      role="tabpanel"
      :aria-labelledby="activeTab ? tabButtonId(activeTab.id) : undefined"
      class="h-[28rem] max-h-[calc(100dvh-16rem)] min-h-0 overflow-y-auto overscroll-contain rounded-lg border border-transparent bg-surface-card/40 p-3"
    >
      <RouterView />
    </div>
  </div>
</template>
