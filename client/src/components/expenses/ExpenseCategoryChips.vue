<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps<{
  categoryOptions: string[];
}>();

const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });
const dropdownRef = useTemplateRef<InstanceType<typeof AdminFilterDropdown>>("dropdownRef");

const activeLabel = computed(() => categoryFilter.value ?? "all");

const optionLabels = computed(() => ["all", ...props.categoryOptions]);

function selectCategory(category: string | null): void {
  categoryFilter.value = category;
  dropdownRef.value?.close();
}

function clearCategory(): void {
  categoryFilter.value = null;
}
</script>

<template>
  <AdminFilterDropdown
    ref="dropdownRef"
    label="filter by category"
    :has-active-filters="categoryFilter !== null"
    :active-label="activeLabel"
    :option-labels="optionLabels"
    :match-trigger-width="false"
    @clear="clearCategory"
  >
    <template #chips>
      <BaseButton
        size="sm"
        class="w-full justify-start"
        :variant="categoryFilter === null ? 'primary' : 'ghost'"
        @click="selectCategory(null)"
      >
        all
      </BaseButton>
      <BaseButton
        v-for="category in categoryOptions"
        :key="category"
        size="sm"
        class="w-full justify-start"
        :variant="categoryFilter === category ? 'primary' : 'ghost'"
        @click="selectCategory(category)"
      >
        {{ category }}
      </BaseButton>
    </template>
  </AdminFilterDropdown>
</template>
