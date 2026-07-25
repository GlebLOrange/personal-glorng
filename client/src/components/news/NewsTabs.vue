<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminTabBar, { type AdminTab } from "@/components/admin/AdminTabBar.vue";
import { usePermissions } from "@/composables/usePermissions";

const route = useRoute();
const router = useRouter();
const { can } = usePermissions();

const tabs = computed((): AdminTab[] => {
  const items: AdminTab[] = [{ id: "digest", label: "digest", family: "1xx" }];
  if (can("news", "read")) {
    items.push({ id: "manage", label: "manage", family: "1xx" });
  }
  if (can("news-sources", "read")) {
    items.push({ id: "sources", label: "sources", family: "1xx" });
  }
  return items;
});

const activeTab = computed(() => {
  if (route.name === "news-sources" || route.name === "news-source") return "sources";
  if (can("news", "read") && String(route.query.manage ?? "") === "1") return "manage";
  return "digest";
});

const model = computed({
  get: () => activeTab.value,
  set: (id: string) => {
    void onTab(id);
  },
});

async function onTab(id: string): Promise<void> {
  if (id === "sources") {
    await router.push({ name: "news-sources" });
    return;
  }
  if (id === "manage") {
    await router.push({ name: "news", query: { manage: "1" } });
    return;
  }
  await router.push({ name: "news", query: {} });
}

watch(
  tabs,
  (next) => {
    if (next.length <= 1) return;
    if (!next.some((tab) => tab.id === activeTab.value)) {
      void onTab(next[0]!.id);
    }
  },
  { immediate: true },
);
</script>

<template>
  <AdminTabBar
    v-if="tabs.length > 1"
    v-model="model"
    panel-id-prefix="news-surface"
    :tabs="tabs"
    flush
    class="mb-4"
  />
</template>
