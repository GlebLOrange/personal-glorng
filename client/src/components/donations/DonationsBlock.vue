<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import type { DonationsConfig } from "@/types";
import { safeNavigationHref } from "@/utils/safeUrl";

defineProps<{
  config: DonationsConfig;
}>();

const isStartingCheckout = ref(false);
const checkoutError = ref(false);
const secondaryLinkButton = "cta-secondary inline-flex items-center";

function safeHref(value: string | null | undefined): string | null {
  return value ? safeNavigationHref(value) : null;
}

async function startStripeCheckout(): Promise<void> {
  checkoutError.value = false;
  isStartingCheckout.value = true;
  try {
    const { data } = await api.post<{ url: string }>("/donations/checkout");
    const checkoutUrl = safeNavigationHref(data.url);
    if (!checkoutUrl) {
      throw new Error("Donation checkout returned an unsafe URL");
    }
    window.location.href = checkoutUrl;
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    checkoutError.value = true;
  } finally {
    isStartingCheckout.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap gap-4">
      <a
        v-if="config.stripe.enabled && safeHref(config.stripe.url)"
        :href="safeHref(config.stripe.url) ?? '#'"
        class="cta-primary"
        target="_blank"
        rel="noopener noreferrer"
      >
        donate by card
      </a>

      <BaseButton
        v-else-if="config.stripe.checkout_enabled"
        variant="primary"
        size="lg"
        :loading="isStartingCheckout"
        @click="startStripeCheckout"
      >
        {{ isStartingCheckout ? "opening..." : "donate by card" }}
      </BaseButton>

      <a
        v-if="config.paypal.enabled && safeHref(config.paypal.url)"
        :href="safeHref(config.paypal.url) ?? '#'"
        :class="secondaryLinkButton"
        target="_blank"
        rel="noopener noreferrer"
      >
        donate with paypal
      </a>

      <a
        v-if="config.patreon.enabled && safeHref(config.patreon.url)"
        :href="safeHref(config.patreon.url) ?? '#'"
        :class="secondaryLinkButton"
        target="_blank"
        rel="noopener noreferrer"
      >
        monthly support
      </a>
    </div>

    <p v-if="checkoutError" class="text-label text-accent-golden" role="status">
      Could not open card checkout. Please try again in a moment.
    </p>
  </div>
</template>
