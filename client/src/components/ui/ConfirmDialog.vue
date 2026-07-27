<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseModal from "@/components/ui/BaseModal.vue";

withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    message?: string;
    confirmLabel?: string;
    /** Shown on the confirm button while loading. */
    loadingLabel?: string;
    loading?: boolean;
    danger?: boolean;
  }>(),
  {
    message: "",
    confirmLabel: "confirm",
    loadingLabel: "working…",
    danger: false,
  },
);

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();
</script>

<template>
  <BaseModal :open="open" :title="title" compact max-width="sm" @close="emit('cancel')">
    <div class="text-sm lowercase text-surface-mid">
      <slot>
        <p>{{ message }}</p>
      </slot>
    </div>
    <template #footer>
      <div class="flex justify-between gap-3">
        <BaseButton variant="secondary" size="sm" :disabled="loading" @click="emit('cancel')">
          cancel
        </BaseButton>
        <BaseButton
          size="sm"
          :variant="danger ? 'secondary' : 'success'"
          :danger="danger"
          :disabled="loading"
          @click="emit('confirm')"
        >
          {{ loading ? loadingLabel : (confirmLabel ?? "confirm") }}
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
