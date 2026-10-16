<script setup lang="ts">
import { nextTick, watch } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_MOBILE_LIST_CLASS,
  ADMIN_MOBILE_ROW_WRAP_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TH_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
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
    // Mobile + desktop edit fields both exist; focus the visible one.
    const candidates = [
      document.getElementById(`cat-name-${id}`),
      document.getElementById(`cat-name-table-${id}`),
    ];
    const el = candidates.find(
      (node): node is HTMLElement => node instanceof HTMLElement && node.offsetParent !== null,
    );
    el?.focus();
  },
);

function onCategoryRowClick(category: ExpenseCategory): void {
  if (props.editingCategoryId === category.id) return;
  emit("startEditCategory", category);
}
</script>

<template>
  <EmptyState v-if="expenseCategories.length === 0" description="no categories yet" />

  <div v-else class="mt-1 min-w-0">
    <div :class="ADMIN_MOBILE_LIST_CLASS">
      <template v-for="category in expenseCategories" :key="`m-${category.id}`">
        <div
          v-if="editingCategoryId === category.id"
          :class="[ADMIN_MOBILE_ROW_WRAP_CLASS, 'flex min-w-0 flex-wrap items-end gap-2']"
        >
          <BaseInput
            :id="`cat-name-${category.id}`"
            v-model="editingCategoryName"
            label="name"
            class="min-w-[8rem] flex-1"
            @keyup.enter="emit('saveCategoryRename')"
          />
          <BaseButton variant="cancel" class="shrink-0" @click="emit('cancelEditCategory')">
            cancel
          </BaseButton>
          <ToolbarPillButton action="save" class="shrink-0" @click="emit('saveCategoryRename')">
            save
          </ToolbarPillButton>
        </div>
        <div
          v-else
          :class="[ADMIN_MOBILE_ROW_WRAP_CLASS, 'flex min-w-0 cursor-pointer items-center gap-2']"
          role="button"
          tabindex="0"
          @click="onCategoryRowClick(category)"
          @keydown.enter.prevent="onCategoryRowClick(category)"
          @keydown.space.prevent="onCategoryRowClick(category)"
        >
          <p class="min-w-0 flex-1 truncate text-sm text-surface-light" :title="category.name">
            {{ category.name }}
          </p>
          <div :class="ADMIN_ACTIONS_CLASS" @click.stop @keydown.stop>
            <IconEditButton
              :aria-label="`rename ${category.name}`"
              @click="emit('startEditCategory', category)"
            />
            <IconCloseButton
              :aria-label="`delete ${category.name}`"
              @click="emit('removeCategory', category)"
            />
          </div>
        </div>
      </template>
    </div>

    <AdminDataTable table-label="expense categories">
      <template #header>
        <th :class="ADMIN_TH_CLASS">name</th>
        <th class="w-px px-2 text-right">
          <span class="sr-only">actions</span>
        </th>
      </template>

      <template v-for="category in expenseCategories" :key="category.id">
        <tr v-if="editingCategoryId === category.id" :class="ADMIN_TR_CLASS">
          <td :class="ADMIN_TD_CLASS" colspan="2">
            <div class="flex min-w-0 flex-wrap items-end gap-2 py-1">
              <BaseInput
                :id="`cat-name-table-${category.id}`"
                v-model="editingCategoryName"
                label="name"
                class="min-w-[8rem] flex-1"
                @keyup.enter="emit('saveCategoryRename')"
              />
              <BaseButton
                variant="cancel"
                class="shrink-0"
                @click="emit('cancelEditCategory')"
              >
                cancel
              </BaseButton>
              <ToolbarPillButton
                action="save"
                class="shrink-0"
                @click="emit('saveCategoryRename')"
              >
                save
              </ToolbarPillButton>
            </div>
          </td>
        </tr>
        <AdminDataRow
          v-else
          interactive
          nested-interactive
          :col-span="2"
          @click="onCategoryRowClick(category)"
        >
          <td :class="ADMIN_TD_TITLE_CLASS">
            <p class="truncate text-sm text-surface-light" :title="category.name">
              {{ category.name }}
            </p>
          </td>
          <template #actions>
            <IconEditButton
              :aria-label="`rename ${category.name}`"
              @click="emit('startEditCategory', category)"
            />
            <IconCloseButton
              :aria-label="`delete ${category.name}`"
              @click="emit('removeCategory', category)"
            />
          </template>
        </AdminDataRow>
      </template>
    </AdminDataTable>
  </div>
</template>
