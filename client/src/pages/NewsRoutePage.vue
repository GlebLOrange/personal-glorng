<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";

import { usePermissions } from "@/composables/usePermissions";

const { can } = usePermissions();
const canReadNewsAdmin = computed(() => can("news", "read"));
const NewsPage = defineAsyncComponent(() => import("@/pages/NewsPage.vue"));
const NewsAdminPage = defineAsyncComponent(() => import("@/pages/admin/tools/NewsAdminPage.vue"));
</script>

<template>
  <NewsAdminPage v-if="canReadNewsAdmin" />
  <NewsPage v-else />
</template>
