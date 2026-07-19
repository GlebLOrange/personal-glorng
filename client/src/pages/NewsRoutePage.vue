<script setup lang="ts">
import { defineAsyncComponent } from "vue";

/** Public news digest for all visitors (admin lives at /admin/tools/news). */
const NewsPage = defineAsyncComponent(() =>
  import("@/pages/NewsPage.vue").then((mod) => mod.default),
);
</script>

<template>
  <NewsPage />
</template>
