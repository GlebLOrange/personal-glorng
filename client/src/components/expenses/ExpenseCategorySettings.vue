<script setup lang="ts">
import { nextTick, watch } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import type { ExpenseCategory } from "@/types";

const props = defineProps<{
  expenseCategories: ExpenseCategory[];
  editingCategoryId: number | null;
}>();

const editingCategoryName = defineModel<string>("editingCategoryName", { required: true });

const emit = defineEmits<{
  startEditCategory: [category: ExpenseCategory];
  cancelEditCategory: [];
  saveCategoryRename: [];
  removeCategory: [category: ExpenseCategory];
}>();

watch(
  () => props.editingCategoryId,
  async (id) => {
    if (id == null) return;
    await nextTick();
    document.getElementById(`cat-name-${id}`)?.focus();
  },
);

function onCategoryRowClick(category: ExpenseCategory): void {
  if (props.editingCategoryId === category.id) return;
  emit("startEditCategory", category);
}
</script>

<template>
  <EmptyState
    v-if="expenseCategories.length === 0"
    description="no categories yet"
  />

  <div v-else class="mt-1 min-w-0">
    <AdminListRow
      v-for="category in expenseCategories"
      :key="category.id"
      interactive
      nested-interactive
      reveal-actions-on-hover
      status-class="accent-blue"
      :expanded="editingCategoryId === category.id"
      @click="onCategoryRowClick(category)"
    >
      <template v-if="editingCategoryId === category.id" #primary>
        <div class="flex min-w-0 flex-1 flex-wrap items-end gap-2" @click.stop>
          <BaseInput
            :id="`cat-name-${category.id}`"
            v-model="editingCategoryName"
            label="name"
            class="min-w-[8rem] flex-1"
            @keyup.enter="emit('saveCategoryRename')"
          />
          <ToolbarPillButton family="2xx" class="shrink-0" @click="emit('saveCategoryRename')">
            save
          </ToolbarPillButton>
          <BaseButton variant="secondary" class="h-10 shrink-0" @click="emit('cancelEditCategory')">
            cancel
          </BaseButton>
        </div>
      </template>
      <template v-else #primary>
        <span :title="category.name">{{ category.name }}</span>
      </template>
      <template v-if="editingCategoryId !== category.id" #actions>
        <IconEditButton
          :aria-label="`rename ${category.name}`"
          @click="emit('startEditCategory', category)"
        />
        <IconCloseButton
          :aria-label="`delete ${category.name}`"
          @click="emit('removeCategory', category)"
        />
      </template>
    </AdminListRow>
  </div>
</template>
