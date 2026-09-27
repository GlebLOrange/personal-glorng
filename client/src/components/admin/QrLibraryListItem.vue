<script setup lang="ts">
import { computed, ref } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import type { QrListItem } from "@/types";

const props = defineProps<{
  item: QrListItem;
  canWrite: boolean;
  deleting?: boolean;
}>();

const emit = defineEmits<{
  select: [];
  delete: [];
}>();

const showDeleteConfirm = ref(false);

const displayTitle = computed(() => props.item.label?.trim() || props.item.content_preview);

function confirmDelete(): void {
  showDeleteConfirm.value = false;
  emit("delete");
}
</script>

<template>
  <AdminListRow
    interactive
    nested-interactive
    hoverable
    center-meta
    reveal-actions-on-hover
    @click="emit('select')"
  >
    <template #primary>
      <span class="flex min-w-0 items-center gap-3">
        <img
          :src="item.svg_url"
          alt=""
          class="size-12 shrink-0 rounded bg-white p-1"
          loading="lazy"
        />
        <span class="min-w-0 truncate" :title="displayTitle">{{ displayTitle }}</span>
      </span>
    </template>
    <template #meta>
      <span class="truncate" :title="item.content_preview">
        <template v-if="item.label">{{ item.content_preview }} · </template>
        {{ item.error_level }}
      </span>
    </template>
    <template #actions>
      <IconEditButton aria-label="edit saved QR" @click="emit('select')" />
      <IconCloseButton
        v-if="canWrite"
        aria-label="delete saved QR"
        @click="showDeleteConfirm = true"
      />
    </template>
  </AdminListRow>

  <ConfirmDialog
    :open="showDeleteConfirm"
    title="delete saved QR"
    confirm-label="delete"
    danger
    :loading="deleting"
    @confirm="confirmDelete"
    @cancel="showDeleteConfirm = false"
  >
    <p>
      delete
      <span class="font-medium text-surface-high">{{ displayTitle }}</span>
      ? this cannot be undone
    </p>
  </ConfirmDialog>
</template>
