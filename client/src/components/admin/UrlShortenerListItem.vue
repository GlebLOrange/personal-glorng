<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import type { UrlItem } from "@/types";
import { formatDate } from "@/utils/format";
import { publicUrl } from "@/utils/publicLinks";

const props = withDefaults(
  defineProps<{
    url: UrlItem;
    canWrite: boolean;
    saving?: boolean;
    deleting?: boolean;
    /** Guest localStorage row — code is not a live /s/{code} redirect. */
    localRow?: boolean;
  }>(),
  { localRow: false },
);

const emit = defineEmits<{
  copy: [];
  delete: [];
  save: [title: string | null];
}>();

const editing = ref(false);
const draftTitle = ref("");
const showDeleteConfirm = ref(false);
const titleInput = ref<{ focus: () => void } | null>(null);

const shortLink = computed(() => publicUrl("s", props.url.code));
const codeDisplay = computed(() => (props.localRow ? props.url.code : shortLink.value));
const titleLabel = computed(() => props.url.title?.trim() || "—");
const copyAriaLabel = computed(() => (props.localRow ? "copy original URL" : "copy short link"));

watch(
  () => props.url.id,
  () => {
    editing.value = false;
  },
);

watch(
  () => props.saving,
  (isSaving, wasSaving) => {
    if (wasSaving && !isSaving) {
      const trimmed = draftTitle.value.trim() || null;
      if (props.url.title === trimmed) {
        editing.value = false;
      }
    }
  },
);

async function startEdit(): Promise<void> {
  draftTitle.value = props.url.title ?? "";
  editing.value = true;
  await nextTick();
  titleInput.value?.focus();
}

function cancelEdit(): void {
  editing.value = false;
  draftTitle.value = props.url.title ?? "";
}

function saveEdit(): void {
  emit("save", draftTitle.value.trim() || null);
}

function onTitleKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter") {
    event.preventDefault();
    saveEdit();
  }
  if (event.key === "Escape") {
    cancelEdit();
  }
}

function confirmDelete(): void {
  showDeleteConfirm.value = false;
  emit("delete");
}

/** Row click opens edit; links and action buttons keep their own handlers. */
function onRowClick(event: MouseEvent): void {
  if (!props.canWrite) return;
  const target = event.target;
  if (target instanceof Element && target.closest("button, a, input, [data-admin-row-stop]")) {
    return;
  }
  void startEdit();
}
</script>

<template>
  <tr v-if="editing" :class="ADMIN_TR_CLASS">
    <td colspan="6" class="px-3 py-1.5">
      <div class="flex w-full min-w-0 items-stretch gap-1">
        <BaseInput
          ref="titleInput"
          v-model="draftTitle"
          class="min-w-0 flex-1"
          placeholder="title (optional)"
          @keydown="onTitleKeydown"
        />
        <BaseButton
          variant="cancel"
          size="sm"
          class="shrink-0"
          :disabled="saving"
          @click="cancelEdit"
        >
          cancel
        </BaseButton>
        <BaseButton variant="save" size="sm" class="shrink-0" :disabled="saving" @click="saveEdit">
          {{ saving ? "…" : "save" }}
        </BaseButton>
      </div>
    </td>
  </tr>

  <tr v-else :class="[ADMIN_TR_CLASS, canWrite ? 'cursor-pointer' : undefined]" @click="onRowClick">
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <p class="truncate text-sm text-surface-light" :title="titleLabel">
        {{ titleLabel }}
      </p>
    </th>
    <td :class="ADMIN_TD_CLASS">
      <a
        v-if="!localRow"
        :href="shortLink"
        :title="shortLink"
        target="_blank"
        rel="noopener noreferrer"
        class="text-link block w-full truncate text-xs"
      >
        {{ shortLink }}
      </a>
      <p
        v-else
        class="truncate text-xs text-surface-mid"
        :title="`${url.code} (browser only — does not redirect)`"
      >
        {{ codeDisplay }}
      </p>
    </td>
    <td :class="ADMIN_TD_CLASS">
      <a
        :href="url.original_url"
        :title="url.original_url"
        target="_blank"
        rel="noopener noreferrer"
        class="text-link block w-full max-w-[14rem] truncate text-xs"
      >
        {{ url.original_url }}
      </a>
    </td>
    <td :class="[ADMIN_TD_MUTED_CLASS, 'text-right tabular-nums']">
      {{ url.clicks }}
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS">
      {{ formatDate(url.created_at) }}
    </td>
    <td :class="ADMIN_TD_ACTIONS_CLASS" data-admin-row-stop @click.stop @keydown.stop>
      <div :class="ADMIN_ACTIONS_CLASS">
        <IconEditButton v-if="canWrite" aria-label="edit title" @click="startEdit" />
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
