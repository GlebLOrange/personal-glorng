<script setup lang="ts">
import BaseInput from "@/components/ui/BaseInput.vue";

defineProps<{
  search: string;
}>();

const emit = defineEmits<{
  "update:search": [value: string];
}>();
</script>

<template>
  <div class="mb-6 space-y-4">
    <div class="flex flex-wrap items-center gap-3">
      <BaseInput
        :model-value="search"
        type="search"
        class="min-w-0 flex-1"
        placeholder="search recipe"
        aria-label="search recipe"
        @update:model-value="emit('update:search', String($event ?? ''))"
      />
      <slot name="actions" />
    </div>
    <slot />
  </div>
</template>
