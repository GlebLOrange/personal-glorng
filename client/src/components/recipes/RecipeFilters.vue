<script setup lang="ts">
import SearchInput from "@/components/ui/SearchInput.vue";

defineProps<{
  search: string;
}>();

const emit = defineEmits<{
  "update:search": [value: string];
}>();
</script>

<template>
  <div class="mb-6 space-y-4">
    <SearchInput
      :model-value="search"
      class="w-full min-w-0 [&_input]:text-right"
      placeholder="search recipe"
      aria-label="search recipe"
      @update:model-value="emit('update:search', String($event ?? ''))"
    />
    <slot />
  </div>
</template>
