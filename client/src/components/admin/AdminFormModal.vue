<script setup lang="ts">
import BaseModal from "@/components/ui/BaseModal.vue";

defineProps<{
  open: boolean;
  title: string;
  maxWidth?: "md" | "lg" | "2xl";
}>();

const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <BaseModal v-if="open" :title="title" :max-width="maxWidth" @close="emit('close')">
    <slot />
  </BaseModal>
</template>
