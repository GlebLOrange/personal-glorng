<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { TASK_STATUSES, statusLabel } from "@/constants/taskStatus";
import { SELECT_CLASS_COMPACT } from "@/constants/formClasses";

defineProps<{
  taskCountLabel: string;
}>();

const filterStatus = defineModel<string>("filterStatus", { required: true });

const emit = defineEmits<{ create: [] }>();
</script>

<template>
  <div class="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between mb-4">
    <div class="flex flex-col sm:flex-row gap-3 sm:items-center">
      <select v-model="filterStatus" :class="SELECT_CLASS_COMPACT">
        <option value="">All statuses</option>
        <option v-for="status in TASK_STATUSES" :key="status" :value="status">
          {{ statusLabel(status) }}
        </option>
      </select>
      <span class="text-xs text-surface-mid">{{ taskCountLabel }}</span>
    </div>
    <BaseButton variant="primary" size="sm" @click="emit('create')">+ New task</BaseButton>
  </div>
</template>
