<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";

const props = defineProps<{
  /** Button label stem after Show/Hide (e.g. "data extract usage guide"). */
  title: string;
}>();

const open = ref(false);
</script>

<template>
  <div>
    <BaseButton
      variant="ghost"
      size="sm"
      class="mb-4"
      :aria-expanded="open"
      @click="open = !open"
    >
      {{ open ? "▾ Hide" : "▸ Show" }} {{ props.title }}
    </BaseButton>

    <Card v-if="open">
      <slot />
    </Card>
  </div>
</template>
