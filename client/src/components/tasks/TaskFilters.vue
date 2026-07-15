<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";

defineProps<{
  canMutate?: boolean;
}>();

const emit = defineEmits<{ create: [] }>();
</script>

<template>
  <BaseButton v-if="canMutate" variant="primary" size="sm" @click="emit('create')">
    + New task
  </BaseButton>
</template>
