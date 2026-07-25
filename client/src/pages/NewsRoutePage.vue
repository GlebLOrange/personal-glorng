<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import { useRoute } from "vue-router";

import { usePermissions } from "@/composables/usePermissions";

/** Public digest, or editorial manage list when ?manage=1 and news:read. */
const NewsPage = defineAsyncComponent(() =>
  import("@/pages/NewsPage.vue").then((mod) => mod.default),
);
const NewsAdminPage = defineAsyncComponent(() =>
  import("@/pages/admin/tools/NewsAdminPage.vue").then((mod) => mod.default),
);

const route = useRoute();
const { can } = usePermissions();

const showManage = computed(() => can("news", "read") && String(route.query.manage ?? "") === "1");
</script>

<template>
  <NewsAdminPage v-if="showManage" />
  <NewsPage v-else />
</template>
