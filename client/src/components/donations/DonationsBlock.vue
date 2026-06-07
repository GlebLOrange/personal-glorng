<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { useClipboard } from "@/composables/useClipboard";
import type { DonationsConfig } from "@/types";

defineProps<{
  config: DonationsConfig;
}>();

const { copy } = useClipboard();
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap gap-4">
      <a
        v-if="config.stripe.enabled"
        :href="config.stripe.url"
        target="_blank"
        rel="noopener noreferrer"
      >
        <BaseButton variant="primary" size="lg"> Support via Stripe </BaseButton>
      </a>

      <a
        v-if="config.telegram.enabled"
        :href="config.telegram.url"
        target="_blank"
        rel="noopener noreferrer"
      >
        <BaseButton variant="secondary" size="lg"> Telegram </BaseButton>
      </a>
    </div>

    <div
      v-if="config.crypto.btc || config.crypto.eth"
      class="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      <BaseCard v-if="config.crypto.btc" hoverable>
        <div class="text-label text-accent-blue mb-2">BTC</div>
        <code class="text-sm font-data text-surface-light break-all">{{ config.crypto.btc }}</code>
        <BaseButton variant="ghost" size="sm" class="mt-3" @click="copy(config.crypto.btc)">
          Copy Address
        </BaseButton>
      </BaseCard>

      <BaseCard v-if="config.crypto.eth" hoverable>
        <div class="text-label text-accent-blue mb-2">ETH</div>
        <code class="text-sm font-data text-surface-light break-all">{{ config.crypto.eth }}</code>
        <BaseButton variant="ghost" size="sm" class="mt-3" @click="copy(config.crypto.eth)">
          Copy Address
        </BaseButton>
      </BaseCard>
    </div>
  </div>
</template>
