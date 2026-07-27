<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import TaskIntakeList from "@/components/tasks/TaskIntakeList.vue";
import type { TaskIntakeItem } from "@/types";

defineProps<{
  intakes: TaskIntakeItem[];
  loading: boolean;
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}>();

const emit = defineEmits<{
  firstPage: [];
  prevPage: [];
  nextPage: [];
  lastPage: [];
}>();
</script>

<template>
  <section
    id="tasks-tab-panel-intakes"
    role="tabpanel"
    aria-labelledby="tasks-tab-tab-intakes"
    tabindex="0"
    class="outline-none"
  >
    <TaskIntakeList :intakes="intakes" :loading="loading" />
    <AdminListFooter
      v-if="!loading"
      :total="total"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      :has-previous-page="hasPreviousPage"
      :loading="loading"
      item-label="intakes"
      aria-label="task intakes pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
