<script setup lang="ts">
import { defineAsyncComponent, onMounted, onUnmounted, ref } from "vue";
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

onMounted(() => {
  void loadDonations();
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
    <div class="flex justify-center mb-4">
      <router-link
        to="/privacy"
        class="text-base text-surface-sage hover:text-accent-blue transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
      >
        Privacy Policy
      </router-link>
    </div>
    <p class="flex items-center justify-center gap-2 text-base text-surface-sage text-center">
      <span>&copy; {{ year }}</span>
      <SiteLogo class-name="h-4 w-auto" />
      <span class="sr-only">Gleb.Y</span>
    </p>
  </footer>
</template>
