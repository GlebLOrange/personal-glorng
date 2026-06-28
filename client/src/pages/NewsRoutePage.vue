<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";

import { usePermissions } from "@/composables/usePermissions";

const { isSuperuser } = usePermissions();
const canReadNewsAdmin = computed(() => isSuperuser.value);
const NewsPage = defineAsyncComponent(() =>
  import("@/pages/NewsPage.vue").then((mod) => mod.default),
);
const NewsAdminPage = defineAsyncComponent(() =>
  import("@/pages/admin/tools/NewsAdminPage.vue").then((mod) => mod.default),
);
</script>

<template>
  <NewsAdminPage v-if="canReadNewsAdmin" />
  <NewsPage v-else />
</template>
