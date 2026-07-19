<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

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
const titleInput = ref<{ focus: () => void } | null>(null);

const shortLink = computed(() => publicUrl("s", props.url.code));
const displayTitle = computed(() => props.url.title || props.url.original_url);

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
</script>

<template>
  <AdminListRow v-if="editing" :hoverable="false">
    <template #primary>
      <BaseInput
        ref="titleInput"
        v-model="draftTitle"
        placeholder="title (optional)"
        aria-label="title (optional)"
        @keydown="onTitleKeydown"
      />
    </template>
    <template #actions>
      <BaseButton variant="primary" size="sm" :disabled="saving" @click="saveEdit">
        {{ saving ? "…" : "save" }}
      </BaseButton>
      <BaseButton variant="ghost" size="sm" :disabled="saving" @click="cancelEdit">
        cancel
      </BaseButton>
    </template>
  </AdminListRow>

  <AdminListRow
    v-else
    :interactive="canWrite"
    :nested-interactive="canWrite"
    hoverable
    @click="startEdit"
  >
    <template #primary>
      <span :title="displayTitle">{{ displayTitle }}</span>
    </template>
    <template #meta>
      <a
        :href="shortLink"
        :title="`${url.original_url} · ${shortLink}`"
        target="_blank"
        rel="noopener noreferrer"
        class="text-accent-blue underline-offset-2 hover:underline"
        @click.stop
      >
        {{ shortLink }}
      </a>
    </template>
    <template #actions>
      <BaseButton
        v-if="canWrite"
        variant="ghost"
        size="sm"
        aria-label="edit title"
        @click="startEdit"
      >
        ✎
      </BaseButton>
      <BaseButton variant="ghost" size="sm" aria-label="copy short link" @click="emit('copy')">
        ⎘
      </BaseButton>
      <BaseButton
        v-if="canWrite"
        variant="ghost"
        danger
        size="sm"
        aria-label="delete short URL"
        @click="showDeleteConfirm = true"
      >
        ✕
      </BaseButton>
    </template>
  </AdminListRow>

  <ExpenseConfirmDialog
    :open="showDeleteConfirm"
    title="delete short URL"
    confirm-label="delete"
    :loading="deleting"
    @confirm="confirmDelete"
    @cancel="showDeleteConfirm = false"
  >
    <p>
      Delete
      <a
        :href="shortLink"
        target="_blank"
        rel="noopener noreferrer"
        class="text-accent-blue underline underline-offset-2"
        @click.stop
      >
        {{ shortLink }}
      </a>
      ? This cannot be undone.
    </p>
  </ExpenseConfirmDialog>
</template>
