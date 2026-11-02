<script setup lang="ts">
import { computed, ref } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_ROW_CLASS,
} from "@/constants/adminDataTable";
import type { QrListItem } from "@/types";
import { formatDate } from "@/utils/format";

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

const labelText = computed(() => props.item.label?.trim() || "—");
const previewIsHttpUrl = computed(() => /^https?:\/\//i.test(props.item.content_preview.trim()));

function confirmDelete(): void {
  showDeleteConfirm.value = false;
  emit("delete");
}
</script>

<template>
  <AdminDataRow interactive nested-interactive :col-span="6" @click="emit('select')">
    <td :class="ADMIN_TD_CLASS">
      <img
        :src="item.svg_url"
        alt=""
        class="size-10 shrink-0 rounded bg-white p-0.5"
        loading="lazy"
      />
    </td>
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <p class="truncate text-sm text-surface-light" :title="labelText">{{ labelText }}</p>
    </th>
    <td :class="ADMIN_TD_CLASS">
      <a
        v-if="previewIsHttpUrl"
        :href="item.content_preview"
        target="_blank"
        rel="noopener noreferrer"
        class="text-link block w-full max-w-[16rem] truncate text-xs"
        :title="item.content_preview"
      >
        {{ item.content_preview }}
      </a>
      <p
        v-else
        class="max-w-[16rem] truncate text-xs text-surface-mid"
        :title="item.content_preview"
      >
        {{ item.content_preview }}
      </p>
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS">
      <span class="uppercase" :title="`error correction ${item.error_level}`">{{
        item.error_level
      }}</span>
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS">
      {{ formatDate(item.updated_at) }}
    </td>
    <td :class="ADMIN_TD_ACTIONS_CLASS" data-admin-row-stop @click.stop @keydown.stop>
      <div :class="ADMIN_ACTIONS_CLASS">
        <IconEditButton aria-label="edit saved QR" @click="emit('select')" />
        <IconCloseButton
          v-if="canWrite"
          aria-label="delete saved QR"
          @click="showDeleteConfirm = true"
        />
      </div>
    </td>
  </AdminDataRow>

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
      <span class="font-medium text-surface-light">{{ labelText }}</span>
      ? this cannot be undone
    </p>
  </ConfirmDialog>
</template>
