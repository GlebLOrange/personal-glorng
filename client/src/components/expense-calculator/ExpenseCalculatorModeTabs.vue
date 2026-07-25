<script setup lang="ts">
import { computed } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import type { ExpenseCalculatorMode } from "@/composables/useExpenseCalculator";

const props = defineProps<{
  activeMode: ExpenseCalculatorMode;
  tabs: Array<{ id: ExpenseCalculatorMode; label: string }>;
}>();

const emit = defineEmits<{ change: [mode: ExpenseCalculatorMode] }>();

const mode = computed({
  get: () => props.activeMode,
  set: (value: string) => emit("change", value as ExpenseCalculatorMode),
});
</script>

<template>
  <AdminTabBar v-model="mode" :tabs="tabs" panel-id-prefix="expense-calc" flush />
</template>
