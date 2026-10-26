<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";
import { usePermissions } from "@/composables/usePermissions";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";
import { actionFamilyClass } from "@/constants/httpStatusColors";
import { useAuthStore } from "@/stores/auth";

type SmallToolTab = {
  id: string;
  label: string;
  to: string;
  name: string;
  /** Login-only tools — hidden from guests. */
  requiresAuth?: boolean;
  /** Capability slug when requiresAuth. */
  slug?: string;
};

const SMALL_TOOL_TABS: SmallToolTab[] = [
  { id: "weather", label: "Weather", to: "/weather", name: WEATHER_ROUTE_NAME },
  { id: "calculator", label: "Calc", to: "/calculator", name: "calculator" },
  {
    id: "password-generator",
    label: "Password",
    to: "/password-generator",
    name: "password-generator",
  },
  { id: "qr-generator", label: "QR", to: "/qr-generator", name: "qr-generator" },
  {
    id: "vid-download",
    label: "Video",
    to: "/vid-download",
    name: "vid-download",
    requiresAuth: true,
    slug: "vid-download",
  },
  {
    id: "email",
    label: "Email",
    to: "/tools/send-email",
    name: "tool-email",
    requiresAuth: true,
    slug: "email",
  },
];

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { canAccess } = usePermissions();
const tablistRef = ref<HTMLElement | null>(null);

const visibleTabs = computed(() =>
  SMALL_TOOL_TABS.filter((tab) => {
    if (!tab.requiresAuth) return true;
    if (!auth.isAuthenticated) return false;
    return tab.slug ? canAccess(tab.slug) : true;
  }),
);

const activeTab = computed(
  () => visibleTabs.value.find((tab) => tab.name === route.name) ?? visibleTabs.value[0],
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
  const tab = visibleTabs.value[index];
  if (!tab) return;
  await router.push(tab.to);
  if (!shouldFocus) return;
  await nextTick();
  tablistRef.value?.querySelectorAll<HTMLElement>('[role="tab"]')[index]?.focus();
}

function onTabKeydown(event: KeyboardEvent, index: number): void {
  if (visibleTabs.value.length === 0) return;
  if (event.key === "Home") {
    event.preventDefault();
    void activateTabAt(0, true);
    return;
  }
  if (event.key === "End") {
    event.preventDefault();
    void activateTabAt(visibleTabs.value.length - 1, true);
    return;
  }
  if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;

  event.preventDefault();
  const direction = event.key === "ArrowRight" ? 1 : -1;
  const nextIndex = (index + direction + visibleTabs.value.length) % visibleTabs.value.length;
  void activateTabAt(nextIndex, true);
}
</script>

<template>
  <div class="flex min-h-[calc(100dvh-8rem)] items-center justify-center px-6 py-12">
    <div class="relative w-full max-w-sm space-y-4">
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
          v-for="(tab, index) in visibleTabs"
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
        class="h-[28rem] overflow-y-auto overscroll-contain rounded-lg border border-transparent bg-surface-card/40 p-3"
      >
        <RouterView />
      </div>
    </div>
  </div>
</template>
