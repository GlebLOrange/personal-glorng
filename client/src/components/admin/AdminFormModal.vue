<script setup lang="ts">
import BaseModal from "@/components/ui/BaseModal.vue";
import type { OverlayMaxWidth } from "@/constants/overlaySizes";

defineProps<{
  open: boolean;
  title: string;
  maxWidth?: OverlayMaxWidth;
}>();

const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <BaseModal :open="open" :title="title" :max-width="maxWidth" @close="emit('close')">
    <slot />
  </BaseModal>
</template>
