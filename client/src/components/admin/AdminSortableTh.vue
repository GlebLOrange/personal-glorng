<script setup lang="ts">
import { computed } from "vue";
import { ADMIN_SORT_HEADER_BUTTON_CLASS, ADMIN_TH_CLASS } from "@/constants/adminDataTable";

/** Shared sortable column header: aria-sort on th, button with direction arrow. */
const props = withDefaults(
  defineProps<{
    label: string;
    direction: "ascending" | "descending" | "none";
    align?: "left" | "right";
  }>(),
  { align: "left" },
);

const emit = defineEmits<{ sort: [] }>();

const active = computed(() => props.direction !== "none");
const arrow = computed(() =>
  props.direction === "ascending" ? "↑" : props.direction === "descending" ? "↓" : "↕",
);
const nextLabel = computed(() =>
  props.direction === "ascending"
    ? `sort by ${props.label}, descending`
    : `sort by ${props.label}, ascending`,
);
</script>

<template>
  <th
    :class="[ADMIN_TH_CLASS, align === 'right' ? 'text-right' : 'text-left']"
    scope="col"
    :aria-sort="direction"
  >
    <button
      type="button"
      :class="[
        ADMIN_SORT_HEADER_BUTTON_CLASS,
        align === 'right' ? 'w-full justify-end' : '',
        active ? 'font-medium text-surface-light' : 'text-surface-mid',
      ]"
      :aria-label="nextLabel"
      @click="emit('sort')"
    >
      <span>{{ label }}</span>
      <span
        aria-hidden="true"
        :class="['inline-block w-3 text-center', active ? 'text-accent-coral' : 'text-surface-muted']"
        >{{ arrow }}</span
      >
    </button>
  </th>
</template>
