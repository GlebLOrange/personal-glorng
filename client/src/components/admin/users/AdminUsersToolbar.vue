<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import { userRoleClass, userStatusClass } from "@/constants/filterColors";

export type RoleFilter = "all" | "superuser" | "custom";
export type StatusFilter = "all" | "verified" | "unverified" | "protected";

const ROLE_FILTERS: { label: string; value: Exclude<RoleFilter, "all"> }[] = [
  { label: "superusers", value: "superuser" },
  { label: "custom access", value: "custom" },
];

const STATUS_FILTERS: { label: string; value: Exclude<StatusFilter, "all"> }[] = [
  { label: "verified", value: "verified" },
  { label: "unverified", value: "unverified" },
  { label: "protected", value: "protected" },
];

const searchQuery = defineModel<string>("searchQuery", { required: true });
const roleFilter = defineModel<RoleFilter>("roleFilter", { required: true });
const statusFilter = defineModel<StatusFilter>("statusFilter", { required: true });

const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const hasActiveFilters = computed(
  () => roleFilter.value !== "all" || statusFilter.value !== "all",
);
const activeFilterLabel = computed(() => {
  const parts: string[] = [];
  const role = ROLE_FILTERS.find((chip) => chip.value === roleFilter.value)?.label;
  const status = STATUS_FILTERS.find((chip) => chip.value === statusFilter.value)?.label;
  if (role) parts.push(role);
  if (status) parts.push(status);
  return parts.length ? parts.join(", ") : undefined;
});

function setRoleFilter(next: Exclude<RoleFilter, "all">): void {
  roleFilter.value = next;
  filterDropdownRef.value?.close();
}

function setUserStatusFilter(next: Exclude<StatusFilter, "all">): void {
  statusFilter.value = next;
  filterDropdownRef.value?.close();
}

function clearFilters(): void {
  roleFilter.value = "all";
  statusFilter.value = "all";
  filterDropdownRef.value?.close();
}
</script>

<template>
  <AdminListToolbar>
    <template #start>
      <div class="flex w-full min-w-0 flex-col gap-3">
        <AdminFilterDropdown
          ref="filterDropdown"
          :has-active-filters="hasActiveFilters"
          :active-label="activeFilterLabel"
          :option-labels="[
            ...ROLE_FILTERS.map((chip) => chip.label),
            ...STATUS_FILTERS.map((chip) => chip.label),
          ]"
          @clear="clearFilters"
        >
          <div class="flex flex-col gap-2">
            <AdminFilterChip
              v-for="chip in ROLE_FILTERS"
              :key="chip.value"
              :label="chip.label"
              :active="roleFilter === chip.value"
              :color-class="userRoleClass(chip.value)"
              @click="setRoleFilter(chip.value)"
            />
          </div>

          <div class="border-t border-surface-border" />

          <div class="flex flex-col gap-2">
            <AdminFilterChip
              v-for="chip in STATUS_FILTERS"
              :key="chip.value"
              :label="chip.label"
              :active="statusFilter === chip.value"
              :color-class="userStatusClass(chip.value)"
              @click="setUserStatusFilter(chip.value)"
            />
          </div>
        </AdminFilterDropdown>
        <SearchInput
          v-model="searchQuery"
          placeholder="search users by name or email"
          class="w-full"
        />
      </div>
    </template>
  </AdminListToolbar>
</template>
