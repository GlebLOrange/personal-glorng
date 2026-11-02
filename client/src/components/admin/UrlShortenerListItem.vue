<script setup lang="ts">
import { computed, ref } from "vue";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import type { UrlItem } from "@/types";
import { publicUrl } from "@/utils/publicLinks";

const props = withDefaults(
  defineProps<{
    url: UrlItem;
    canWrite: boolean;
    deleting?: boolean;
    /** Guest localStorage row — code is not a live /s/{code} redirect. */
    localRow?: boolean;
  }>(),
  { localRow: false },
);

const emit = defineEmits<{
  copy: [];
  delete: [];
}>();

const showDeleteConfirm = ref(false);

const shortLink = computed(() => publicUrl("s", props.url.code));
const copyAriaLabel = computed(() => (props.localRow ? "copy original URL" : "copy short link"));

function confirmDelete(): void {
  showDeleteConfirm.value = false;
  emit("delete");
}
</script>

<template>
  <tr :class="ADMIN_TR_CLASS">
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <a
        :href="url.original_url"
        :title="url.original_url"
        target="_blank"
        rel="noopener noreferrer"
        class="text-link block w-full truncate text-xs font-normal"
      >
        {{ url.original_url }}
      </a>
    </th>
    <td :class="ADMIN_TD_ACTIONS_CLASS" data-admin-row-stop @click.stop @keydown.stop>
      <div :class="ADMIN_ACTIONS_CLASS">
        <IconCopyButton :aria-label="copyAriaLabel" @click="emit('copy')" />
        <IconCloseButton
          v-if="canWrite"
          aria-label="delete short URL"
          @click="showDeleteConfirm = true"
        />
      </div>
    </td>
  </tr>

  <ConfirmDialog
    :open="showDeleteConfirm"
    title="delete short URL"
    confirm-label="delete"
    danger
    :loading="deleting"
    @confirm="confirmDelete"
    @cancel="showDeleteConfirm = false"
  >
    <p>
      delete
      <a
        v-if="!localRow"
        :href="shortLink"
        target="_blank"
        rel="noopener noreferrer"
        class="text-link"
        @click.stop
      >
        {{ shortLink }}
      </a>
      <span v-else class="font-medium text-surface-light">{{ url.code }}</span>
      ? this cannot be undone
    </p>
  </ConfirmDialog>
</template>
