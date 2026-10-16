<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import SiteLogo from "@/components/brand/SiteLogo.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import type { DonationsConfig } from "@/types";
import { consumeQueryParams } from "@/utils/consumeQueryParams";

const DonationsBlock = defineAsyncComponent(
  () => import("@/components/donations/DonationsBlock.vue"),
);

const year = new Date().getFullYear();
const route = useRoute();
const router = useRouter();
const showDonationThanks = ref(false);

/** Hire surfaces — keep donations off the CV and shared profile. */
const showDonations = computed(() => {
  const name = route.name;
  return name !== "portfolio" && name !== "profile" && name !== "home";
});

const {
  data: donations,
  loading: donationsLoading,
  fetch: fetchDonations,
} = useCachedApi<DonationsConfig>("/donations/config");
const donationsError = ref(false);
const donationsFetched = ref(false);

async function loadDonations(): Promise<void> {
  donationsError.value = false;
  try {
    await fetchDonations();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    donationsError.value = true;
  } finally {
    donationsFetched.value = true;
  }
}

watch(
  showDonations,
  (visible) => {
    if (visible && !donationsFetched.value) {
      void loadDonations();
    }
  },
  { immediate: true },
);

onMounted(() => {
  if (String(route.query.donated ?? "") === "1") {
    showDonationThanks.value = true;
    void consumeQueryParams(router, route.path, route.query, ["donated"]);
  }
});

onUnmounted(() => {
  showDonationThanks.value = false;
});
</script>

<template>
  <footer
    class="border-t border-surface-border py-10 pb-[calc(2.5rem+env(safe-area-inset-bottom))]"
  >
    <div
      v-if="showDonations"
      class="mx-auto mb-4 flex max-w-lg flex-wrap items-center justify-center gap-x-3 gap-y-2 print:hidden"
    >
      <p class="text-meta">support this work</p>
      <p v-if="showDonationThanks" class="text-label text-status-success" role="status">
        thanks for your support
      </p>
      <div
        v-if="donationsLoading && !donationsFetched"
        class="h-8 w-24 animate-pulse rounded-lg bg-surface-card"
        aria-busy="true"
      />
      <DonationsBlock v-else-if="donations" layout="center" :config="donations" />
      <p v-else-if="donationsError" class="text-label text-status-error" role="status">
        support options unavailable
      </p>
    </div>
    <nav
      aria-label="footer"
      class="mb-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 print:hidden"
    >
      <router-link
        to="/news"
        class="nav-link-quiet inline-flex min-h-11 items-center px-1"
      >
        news
      </router-link>
      <router-link
        to="/tools"
        class="nav-link-quiet inline-flex min-h-11 items-center px-1"
      >
        tools
      </router-link>
      <router-link
        to="/privacy"
        class="nav-link-quiet inline-flex min-h-11 items-center px-1"
      >
        privacy policy
      </router-link>
    </nav>
    <p class="flex items-center justify-center gap-2 text-base text-surface-sage text-center">
      <span>&copy; {{ year }}</span>
      <SiteLogo class-name="h-7 w-auto" />
      <span class="sr-only">Gleb.Y</span>
    </p>
  </footer>
</template>
