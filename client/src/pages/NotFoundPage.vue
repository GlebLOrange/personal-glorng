<script setup lang="ts">
import { useRoute } from "vue-router";

import StatusBadge from "@/components/ui/StatusBadge.vue";
import { httpStatusClass } from "@/constants/httpStatusColors";

const route = useRoute();
</script>

<template>
  <div
    class="flex min-h-[calc(100dvh-8rem)] items-center justify-center px-6 py-12"
  >
    <div class="flex w-full max-w-md flex-col items-center gap-4 text-center">
      <StatusBadge label="404" :class-name="httpStatusClass(404)" size="md" />
      <h1 class="text-2xl font-bold leading-none text-surface-light">
        This path isn't on Gleb.Y.
      </h1>
      <p class="text-meta font-data break-all">{{ route.fullPath }}</p>
      <RouterLink to="/" class="cta-primary mt-2">Home</RouterLink>
      <nav
        aria-label="recovery links"
        class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2"
      >
        <RouterLink
          to="/tools"
          class="nav-link inline-flex min-h-11 items-center text-sm"
        >
          Tools
        </RouterLink>
        <RouterLink
          to="/news"
          class="nav-link inline-flex min-h-11 items-center text-sm"
        >
          News
        </RouterLink>
      </nav>
    </div>
  </div>
</template>
