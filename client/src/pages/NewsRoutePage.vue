<script setup lang="ts">
import { computed } from "vue";

import { usePermissions } from "@/composables/usePermissions";
import NewsPage from "@/pages/NewsPage.vue";
import NewsAdminPage from "@/pages/admin/tools/NewsAdminPage.vue";

const { can } = usePermissions();
const canReadNewsAdmin = computed(() => can("news", "read"));
</script>

<template>
  <NewsAdminPage v-if="canReadNewsAdmin" />
  <NewsPage v-else />
</template>
