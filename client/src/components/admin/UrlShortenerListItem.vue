<script setup lang="ts">
import { computed, ref, watch } from "vue";

import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
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
const displayTitle = computed(() => props.url.title || "Untitled");
const deleteMessage = computed(
  () => `Delete ${shortLink.value}? This cannot be undone.`,
);

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
  <Card hoverable>
    <div class="flex justify-between items-start gap-4">
      <div class="flex-1 min-w-0">
        <template v-if="editing">
          <BaseInput
            v-model="draftTitle"
            label="Title"
            placeholder="Optional title"
            @keydown="onTitleKeydown"
          />
          <div class="flex gap-2 mt-3">
            <BaseButton variant="primary" size="sm" :disabled="saving" @click="saveEdit">
              {{ saving ? "Saving..." : "Save" }}
            </BaseButton>
            <BaseButton variant="ghost" size="sm" :disabled="saving" @click="cancelEdit">
              Cancel
            </BaseButton>
          </div>
        </template>

        <template v-else>
          <div class="text-surface-light font-bold text-sm truncate">{{ displayTitle }}</div>
          <a
            :href="url.original_url"
            class="text-xs text-surface-mid truncate mt-1 block hover:underline"
            target="_blank"
            rel="noopener noreferrer"
            :title="url.original_url"
          >
            <span class="sr-only">Original URL (opens in new tab): </span>
            {{ url.original_url }}
          </a>
          <div class="text-xs text-surface-mid mt-1">{{ url.clicks }} clicks</div>
          <a
            :href="shortLink"
            class="text-xs text-accent-blue mt-2 block truncate hover:underline"
            target="_blank"
            rel="noopener noreferrer"
            :title="shortLink"
          >
            <span class="sr-only">Short link (opens in new tab): </span>
            {{ shortLink }}
          </a>
        </template>
      </div>

      <div v-if="!editing" class="flex flex-wrap gap-2 shrink-0">
        <BaseButton v-if="canWrite" variant="ghost" size="sm" aria-label="Edit title" @click="startEdit">
          Edit
        </BaseButton>
        <BaseButton variant="ghost" size="sm" @click="emit('copy')">Copy</BaseButton>
        <BaseButton
          v-if="canWrite"
          variant="ghost"
          size="sm"
          @click="showDeleteConfirm = true"
        >
          Delete
        </BaseButton>
      </div>
    </div>

    <ExpenseConfirmDialog
      :open="showDeleteConfirm"
      title="Delete short URL"
      :message="deleteMessage"
      confirm-label="Delete"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />
  </Card>
</template>
