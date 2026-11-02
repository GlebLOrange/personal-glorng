<script setup lang="ts">
import {
  ADMIN_TABLE_CLASS,
  ADMIN_TABLE_WRAP_CLASS,
  ADMIN_THEAD_ROW_CLASS,
} from "@/constants/adminDataTable";

defineProps<{
  /** Accessible name for the table (maps to aria-label). */
  tableLabel: string;
}>();
</script>

<template>
  <div :class="ADMIN_TABLE_WRAP_CLASS">
    <table :class="ADMIN_TABLE_CLASS" :aria-label="tableLabel">
      <thead v-if="$slots.header" class="sticky top-0 z-10">
        <tr :class="ADMIN_THEAD_ROW_CLASS">
          <slot name="header" />
        </tr>
      </thead>
      <tbody>
        <slot />
      </tbody>
    </table>
  </div>
</template>
