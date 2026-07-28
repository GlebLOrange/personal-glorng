<script setup lang="ts">
import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import type { DonationsConfig } from "@/types";
import { safeNavigationHref } from "@/utils/safeUrl";

const props = defineProps<{
  config: DonationsConfig;
}>();

const isStartingCheckout = ref(false);
const checkoutError = ref(false);

type DonationAction = {
  id: "stripe-url" | "stripe-checkout" | "paypal" | "patreon";
  label: string;
  href?: string;
};

function safeHref(value: string | null | undefined): string | null {
  return value ? safeNavigationHref(value) : null;
}

const actions = computed((): DonationAction[] => {
  const items: DonationAction[] = [];
  const stripeUrl = safeHref(props.config.stripe.url);
  if (props.config.stripe.enabled && stripeUrl) {
    items.push({ id: "stripe-url", label: "donate by card", href: stripeUrl });
  } else if (props.config.stripe.checkout_enabled) {
    items.push({ id: "stripe-checkout", label: "donate by card" });
  }
  const paypalUrl = safeHref(props.config.paypal.url);
  if (props.config.paypal.enabled && paypalUrl) {
    items.push({ id: "paypal", label: "donate with paypal", href: paypalUrl });
  }
  const patreonUrl = safeHref(props.config.patreon.url);
  if (props.config.patreon.enabled && patreonUrl) {
    items.push({ id: "patreon", label: "monthly support", href: patreonUrl });
  }
  return items;
});

const primaryAction = computed(() => actions.value[0] ?? null);
const secondaryActions = computed(() => actions.value.slice(1));

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
  <div class="flex min-w-0 flex-col items-end gap-2">
    <div class="flex flex-wrap items-center justify-end gap-4">
      <template v-if="primaryAction">
        <a
          v-if="primaryAction.id !== 'stripe-checkout' && primaryAction.href"
          :href="primaryAction.href"
          class="cta-primary"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ primaryAction.label }}
        </a>
        <button
          v-else-if="primaryAction.id === 'stripe-checkout'"
          type="button"
          class="cta-primary"
          :disabled="isStartingCheckout"
          @click="startStripeCheckout"
        >
          {{ isStartingCheckout ? "opening…" : primaryAction.label }}
        </button>
      </template>

      <a
        v-for="action in secondaryActions"
        :key="action.id"
        :href="action.href"
        class="cta-secondary inline-flex items-center"
        target="_blank"
        rel="noopener noreferrer"
      >
        {{ action.label }}
      </a>
    </div>

    <p v-if="checkoutError" class="text-label text-status-error" role="status">
      Could not open card checkout. Please try again in a moment.
    </p>
  </div>
</template>
