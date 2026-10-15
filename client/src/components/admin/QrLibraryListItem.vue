<script setup lang="ts">
import { computed, ref } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_MOBILE_ROW_WRAP_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
} from "@/constants/adminDataTable";
import type { QrListItem } from "@/types";

const props = withDefaults(
  defineProps<{
    item: QrListItem;
    canWrite: boolean;
    deleting?: boolean;
    layout?: "card" | "table";
  }>(),
  { layout: "card" },
);

const emit = defineEmits<{
  select: [];
  delete: [];
}>();

const showDeleteConfirm = ref(false);

const displayTitle = computed(() => props.item.label?.trim() || props.item.content_preview);
const previewIsHttpUrl = computed(() => /^https?:\/\//i.test(props.item.content_preview.trim()));

function confirmDelete(): void {
  showDeleteConfirm.value = false;
  emit("delete");
}

function onRowClick(event: MouseEvent): void {
  const target = event.target;
  if (target instanceof Element && target.closest("button, a, input, [data-admin-row-stop]")) {
    return;
  }
  emit("select");
}
</script>

<template>
  <AdminDataRow
    v-if="layout === 'table'"
    interactive
    nested-interactive
    :col-span="4"
    @click="emit('select')"
  >
    <td :class="ADMIN_TD_CLASS">
      <img
        :src="item.svg_url"
        alt=""
        class="size-10 shrink-0 rounded bg-white p-0.5"
        loading="lazy"
      />
    </td>
    <td :class="ADMIN_TD_TITLE_CLASS">
      <template v-if="item.label">
        <p class="truncate text-sm text-surface-light" :title="item.label">{{ item.label }}</p>
        <a
          v-if="previewIsHttpUrl"
          :href="item.content_preview"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-0.5 block w-full truncate text-xs text-accent-blue underline-offset-2 hover:underline"
          :title="item.content_preview"
        >
          {{ item.content_preview }}
        </a>
        <p
          v-else
          class="mt-0.5 truncate text-xs text-surface-mid"
          :title="item.content_preview"
        >
          {{ item.content_preview }}
        </p>
      </template>
      <a
        v-else-if="previewIsHttpUrl"
        :href="item.content_preview"
        target="_blank"
        rel="noopener noreferrer"
        class="block w-full truncate text-sm text-accent-blue underline-offset-2 hover:underline"
        :title="item.content_preview"
      >
        {{ item.content_preview }}
      </a>
      <p v-else class="truncate text-sm text-surface-light" :title="item.content_preview">
        {{ item.content_preview }}
      </p>
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS">
      <span class="uppercase" :title="`error correction ${item.error_level}`">{{
        item.error_level
      }}</span>
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

  <div
    v-else
    :class="[ADMIN_MOBILE_ROW_WRAP_CLASS, 'flex min-w-0 cursor-pointer items-center gap-2']"
    @click="onRowClick"
  >
    <img
      :src="item.svg_url"
      alt=""
      class="size-10 shrink-0 rounded bg-white p-0.5"
      loading="lazy"
    />
    <div class="min-w-0 flex-1">
      <template v-if="item.label">
        <p class="truncate text-sm text-surface-light" :title="item.label">{{ item.label }}</p>
        <a
          v-if="previewIsHttpUrl"
          :href="item.content_preview"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-0.5 block truncate text-xs text-accent-blue underline-offset-2 hover:underline"
          :title="item.content_preview"
          @click.stop
        >
          {{ item.content_preview }}
        </a>
        <p
          v-else
          class="mt-0.5 truncate text-xs text-surface-mid"
          :title="item.content_preview"
        >
          {{ item.content_preview }}
        </p>
      </template>
      <a
        v-else-if="previewIsHttpUrl"
        :href="item.content_preview"
        target="_blank"
        rel="noopener noreferrer"
        class="block truncate text-sm text-accent-blue underline-offset-2 hover:underline"
        :title="item.content_preview"
        @click.stop
      >
        {{ item.content_preview }}
      </a>
      <p v-else class="truncate text-sm text-surface-light" :title="item.content_preview">
        {{ item.content_preview }}
      </p>
    </div>
    <span
      class="shrink-0 text-xs uppercase text-surface-muted"
      :title="`error correction ${item.error_level}`"
    >
      {{ item.error_level }}
    </span>
    <div :class="ADMIN_ACTIONS_CLASS" data-admin-row-stop @click.stop @keydown.stop>
      <IconEditButton aria-label="edit saved QR" @click="emit('select')" />
      <IconCloseButton
        v-if="canWrite"
        aria-label="delete saved QR"
        @click="showDeleteConfirm = true"
      />
    </div>
  </div>

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
      <span class="font-medium text-surface-light">{{ displayTitle }}</span>
      ? this cannot be undone
    </p>
  </ConfirmDialog>
</template>
