<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseModal from "@/components/ui/BaseModal.vue";

withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    message?: string;
    confirmLabel?: string;
    loading?: boolean;
    closeDanger?: boolean;
  }>(),
  {
    message: "",
    confirmLabel: "confirm",
    closeDanger: true,
  },
);

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();
</script>

<template>
  <BaseModal
    v-if="open"
    :title="title"
    :close-danger="closeDanger"
    @close="emit('cancel')"
  >
    <div class="mb-6 text-sm text-surface-mid">
      <slot>
        <p>{{ message }}</p>
      </slot>
    </div>
    <div class="flex gap-3">
      <BaseButton variant="primary" :disabled="loading" @click="emit('confirm')">
        {{ loading ? "working..." : (confirmLabel ?? "confirm") }}
      </BaseButton>
      <BaseButton variant="ghost" :disabled="loading" @click="emit('cancel')">cancel</BaseButton>
    </div>
  </BaseModal>
</template>
