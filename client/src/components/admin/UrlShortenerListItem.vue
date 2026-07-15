<script setup lang="ts">
import { computed, ref, watch } from "vue";

import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import type { UrlItem } from "@/types";
import { publicUrl } from "@/utils/publicLinks";

const props = defineProps<{
  url: UrlItem;
  canWrite: boolean;
  saving?: boolean;
  deleting?: boolean;
}>();

const emit = defineEmits<{
  copy: [];
  delete: [];
  save: [title: string | null];
}>();

const editing = ref(false);
const draftTitle = ref("");
const showDeleteConfirm = ref(false);

const shortLink = computed(() => publicUrl("s", props.url.code));
const displayTitle = computed(() => props.url.title || props.url.original_url);
const deleteMessage = computed(
  () => `Delete ${shortLink.value}? This cannot be undone.`,
);

const collapsedMeta = computed(() => {
  return `${props.url.clicks} clicks · ${shortLink.value}`;
});

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

function startEdit(): void {
  draftTitle.value = props.url.title ?? "";
  editing.value = true;
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
</script>

<template>
  <AdminListRow v-if="editing" :hoverable="false">
    <template #primary>
      <BaseInput
        v-model="draftTitle"
        compact
        placeholder="optional title (uses url if empty)"
        aria-label="optional title"
        @keydown="onTitleKeydown"
      />
    </template>
    <template #actions>
      <BaseButton variant="primary" size="sm" :disabled="saving" @click="saveEdit">
        {{ saving ? "…" : "Save" }}
      </BaseButton>
      <BaseButton variant="ghost" size="sm" :disabled="saving" @click="cancelEdit">
        Cancel
      </BaseButton>
    </template>
  </AdminListRow>

  <AdminListRow v-else hoverable nested-interactive>
    <template #primary>
      <span :title="displayTitle">{{ displayTitle }}</span>
    </template>
    <template #meta>
      <span :title="`${url.original_url} · ${shortLink}`">{{ collapsedMeta }}</span>
    </template>
    <template #actions>
      <BaseButton
        v-if="canWrite"
        variant="ghost"
        size="sm"
        aria-label="Edit title"
        @click="startEdit"
      >
        ✎
      </BaseButton>
      <BaseButton variant="ghost" size="sm" aria-label="Copy short link" @click="emit('copy')">
        ⎘
      </BaseButton>
      <BaseButton
        v-if="canWrite"
        variant="ghost"
        size="sm"
        aria-label="Delete short URL"
        @click="showDeleteConfirm = true"
      >
        ✕
      </BaseButton>
    </template>
  </AdminListRow>

  <ExpenseConfirmDialog
    :open="showDeleteConfirm"
    title="Delete short URL"
    :message="deleteMessage"
    confirm-label="Delete"
    :loading="deleting"
    @confirm="confirmDelete"
    @cancel="showDeleteConfirm = false"
  />
</template>
