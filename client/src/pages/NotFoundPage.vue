<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import StatusBadge from "@/components/ui/StatusBadge.vue";
import { httpStatusClass } from "@/constants/httpStatusColors";

type PathContext = {
  title: string;
  body: string;
  /** Extra recovery link when privacy is the natural next step. */
  showPrivacy?: boolean;
};

const route = useRoute();

/** Warm copy for intentional public-surface gaps (pricing / terms / signup). */
function contextForPath(fullPath: string): PathContext | null {
  const first = fullPath.toLowerCase().split(/[/?#]/).find(Boolean) ?? "";
  if (first === "pricing" || first === "rates") {
    return {
      title: "No public price list here.",
      body: "Compensation is role- and contract-specific. If you'd like to talk about work, send an inquiry from the home page.",
    };
  }
  if (first === "terms" || first === "tos") {
    return {
      title: "No public terms page.",
      body: "This is a personal portfolio, not a packaged product. Privacy details live on the privacy page.",
      showPrivacy: true,
    };
  }
  if (first === "signup" || first === "register") {
    return {
      title: "Signup isn't open.",
      body: "Accounts are owner-provisioned — there's no public registration on Gleb.Y.",
    };
  }
  return null;
}

const context = computed(() => contextForPath(route.fullPath));
const heading = computed(() => context.value?.title ?? "This path isn't on Gleb.Y.");
</script>

<template>
  <div class="flex min-h-[calc(100dvh-8rem)] items-center justify-center px-6 py-12">
    <div class="flex w-full max-w-md flex-col items-center gap-4 text-center">
      <StatusBadge label="404" :class-name="httpStatusClass(404)" size="md" />
      <h1 class="text-2xl font-bold leading-none text-surface-light">{{ heading }}</h1>
      <p v-if="context" class="text-sm text-surface-mid">{{ context.body }}</p>
      <p class="text-meta font-data break-all">{{ route.fullPath }}</p>
      <RouterLink to="/" class="cta-primary mt-2">Home</RouterLink>
      <nav
        aria-label="recovery links"
        class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2"
      >
        <RouterLink
          v-if="context?.showPrivacy"
          to="/privacy"
          class="nav-link inline-flex min-h-11 items-center text-sm"
        >
          privacy
        </RouterLink>
        <RouterLink to="/#experience" class="nav-link inline-flex min-h-11 items-center text-sm">
          experience
        </RouterLink>
        <RouterLink to="/tools" class="nav-link inline-flex min-h-11 items-center text-sm">
          tools
        </RouterLink>
        <RouterLink to="/news" class="nav-link inline-flex min-h-11 items-center text-sm">
          news
        </RouterLink>
      </nav>
    </div>
  </div>
</template>
