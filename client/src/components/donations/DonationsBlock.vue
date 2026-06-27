<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import type { DonationsConfig } from "@/types";

defineProps<{
  config: DonationsConfig;
}>();

const isStartingCheckout = ref(false);
const checkoutError = ref(false);
const linkButtonBase =
  "inline-flex items-center font-medium transition-all duration-200 rounded-lg border " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 " +
  "px-6 py-3 text-base";
const primaryLinkButton =
  "bg-gradient-to-r from-accent-blue to-accent-violet text-white border-transparent hover:opacity-90";
const secondaryLinkButton = "bg-surface-card text-surface-light border-surface-border hover:border-accent-blue";

async function startStripeCheckout(): Promise<void> {
  checkoutError.value = false;
  isStartingCheckout.value = true;
  try {
    const { data } = await api.post<{ url: string }>("/donations/checkout");
    window.location.href = data.url;
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
        v-if="config.stripe.enabled"
        :href="config.stripe.url"
        :class="[linkButtonBase, primaryLinkButton]"
        target="_blank"
        rel="noopener noreferrer"
      >
        Donate by Card
      </a>

      <BaseButton
        v-else-if="config.stripe.checkout_enabled"
        variant="primary"
        size="lg"
        :disabled="isStartingCheckout"
        @click="startStripeCheckout"
      >
        {{ isStartingCheckout ? "Opening..." : "Donate by Card" }}
      </BaseButton>

      <a
        v-if="config.paypal.enabled"
        :href="config.paypal.url"
        :class="[linkButtonBase, secondaryLinkButton, 'min-h-11 gap-3 text-left hover:text-accent-blue']"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img
          src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif"
          alt=""
          aria-hidden="true"
          class="h-7 w-auto rounded bg-white px-2 py-1"
        />
        <span class="flex flex-col leading-tight">
          <span class="font-semibold">Donate with PayPal</span>
          <span class="text-xs font-medium text-surface-mid">Cards accepted</span>
        </span>
      </a>

      <a
        v-if="config.patreon.enabled"
        :href="config.patreon.url"
        :class="[linkButtonBase, secondaryLinkButton]"
        target="_blank"
        rel="noopener noreferrer"
      >
        Monthly Support
      </a>
    </div>

    <p v-if="checkoutError" class="text-label text-accent-golden" role="status">
      Could not open card checkout. Please try again in a moment.
    </p>
  </div>
</template>
