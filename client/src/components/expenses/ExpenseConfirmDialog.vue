<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseModal from "@/components/ui/BaseModal.vue";

defineProps<{
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  loading?: boolean;
}>();

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();
</script>

<template>
  <BaseModal v-if="open" :title="title" @close="emit('cancel')">
    <p class="text-sm text-surface-mid mb-6">{{ message }}</p>
    <div class="flex gap-3">
      <BaseButton variant="primary" :disabled="loading" @click="emit('confirm')">
        {{ loading ? "working..." : (confirmLabel ?? "confirm") }}
      </BaseButton>
      <BaseButton variant="ghost" :disabled="loading" @click="emit('cancel')">cancel</BaseButton>
    </div>
  </BaseModal>
</template>
