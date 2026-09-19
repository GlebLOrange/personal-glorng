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
    <div class="flex min-w-0 items-center gap-2">
      <SearchInput
        :model-value="search"
        class="min-w-0 flex-1"
        placeholder="search recipe"
        aria-label="search recipe"
        @update:model-value="emit('update:search', String($event ?? ''))"
      />
      <div v-if="$slots.actions" class="shrink-0">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </div>
</template>
