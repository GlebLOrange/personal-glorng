<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import type { TaskItem } from "@/types";
import { formatDate, formatScheduleDate } from "@/utils/format";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

const props = defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  truncated: boolean;
  year: number;
  month: number;
  selectedDate: string;
}>();

const emit = defineEmits<{
  prevMonth: [];
  nextMonth: [];
  selectDate: [date: string];
  selectTask: [id: number];
}>();

const focusDate = ref(props.selectedDate);

watch(
  () => props.selectedDate,
  (value) => {
    focusDate.value = value;
  },
);

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

function toDateKey(year: number, month: number, day: number): string {
  return `${year}-${pad(month + 1)}-${pad(day)}`;
}

function localDateKey(iso: string): string {
  const d = new Date(iso);
  return toDateKey(d.getFullYear(), d.getMonth(), d.getDate());
}

function todayKey(): string {
  const now = new Date();
  return toDateKey(now.getFullYear(), now.getMonth(), now.getDate());
}

const monthLabel = computed(() =>
  new Date(props.year, props.month, 1).toLocaleString(undefined, {
    month: "long",
    year: "numeric",
  }),
);

const countsByDay = computed(() => {
  const map = new Map<string, number>();
  for (const task of props.tasks) {
    const key = localDateKey(task.scheduled_at);
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  return map;
});

const selectedDayTasks = computed(() =>
  props.tasks
    .filter((task) => localDateKey(task.scheduled_at) === props.selectedDate)
    .sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at)),
);

type DayCell = {
  key: string;
  day: number;
  inMonth: boolean;
  count: number;
  isToday: boolean;
};

const cells = computed((): DayCell[] => {
  const first = new Date(props.year, props.month, 1);
  const startOffset = (first.getDay() + 6) % 7;
  const daysInMonth = new Date(props.year, props.month + 1, 0).getDate();
  const today = todayKey();
  const result: DayCell[] = [];

  for (let i = 0; i < startOffset; i++) {
    const d = new Date(props.year, props.month, 1 - (startOffset - i));
    const key = toDateKey(d.getFullYear(), d.getMonth(), d.getDate());
    result.push({
      key,
      day: d.getDate(),
      inMonth: false,
      count: countsByDay.value.get(key) ?? 0,
      isToday: key === today,
    });
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const key = toDateKey(props.year, props.month, day);
    result.push({
      key,
      day,
      inMonth: true,
      count: countsByDay.value.get(key) ?? 0,
      isToday: key === today,
    });
  }

  while (result.length % 7 !== 0) {
    const last = result[result.length - 1];
    const d = new Date(
      Number(last.key.slice(0, 4)),
      Number(last.key.slice(5, 7)) - 1,
      Number(last.key.slice(8, 10)) + 1,
    );
    const key = toDateKey(d.getFullYear(), d.getMonth(), d.getDate());
    result.push({
      key,
      day: d.getDate(),
      inMonth: false,
      count: countsByDay.value.get(key) ?? 0,
      isToday: key === today,
    });
  }

  return result;
});

function shiftFocus(delta: number): void {
  const [y, m, d] = focusDate.value.split("-").map(Number);
  const next = new Date(y, m - 1, d + delta);
  focusDate.value = toDateKey(next.getFullYear(), next.getMonth(), next.getDate());
  void nextTick(() => {
    document.getElementById(`cal-day-${focusDate.value}`)?.focus();
  });
}

function onDayKeydown(event: KeyboardEvent, key: string): void {
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    shiftFocus(-1);
    return;
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    shiftFocus(1);
    return;
  }
  if (event.key === "ArrowUp") {
    event.preventDefault();
    shiftFocus(-7);
    return;
  }
  if (event.key === "ArrowDown") {
    event.preventDefault();
    shiftFocus(7);
    return;
  }
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    emit("selectDate", key);
  }
}
</script>

<template>
  <section
    id="tasks-tab-panel-calendar"
    role="tabpanel"
    aria-labelledby="tasks-tab-tab-calendar"
    tabindex="0"
    class="outline-none"
  >
    <div class="mb-4 flex min-w-0 items-center justify-between gap-3">
      <BaseButton
        variant="ghost"
        size="sm"
        class="min-h-11 min-w-11"
        aria-label="previous month"
        @click="emit('prevMonth')"
      >
        <ChevronIcon direction="left" class-name="size-4" />
      </BaseButton>
      <h2 class="text-sm font-medium lowercase text-surface-light">{{ monthLabel }}</h2>
      <BaseButton
        variant="ghost"
        size="sm"
        class="min-h-11 min-w-11"
        aria-label="next month"
        @click="emit('nextMonth')"
      >
        <ChevronIcon direction="right" class-name="size-4" />
      </BaseButton>
    </div>

    <div
      v-if="loading"
      class="grid grid-cols-7 border-l border-t border-surface-border/15"
      aria-busy="true"
      aria-label="loading calendar"
    >
      <div
        v-for="n in 28"
        :key="n"
        class="min-h-11 animate-pulse border-b border-r border-surface-border/15 bg-surface-border/20"
      />
    </div>

    <div v-else class="space-y-4">
      <div
        class="grid grid-cols-7 border-l border-t border-surface-border/15"
        role="grid"
        aria-label="month calendar"
      >
        <div
          v-for="label in WEEKDAYS"
          :key="label"
          class="border-b border-r border-surface-border/15 px-1 py-1 text-center text-xs text-surface-mid"
          role="columnheader"
        >
          {{ label }}
        </div>
        <button
          v-for="cell in cells"
          :id="`cal-day-${cell.key}`"
          :key="cell.key"
          type="button"
          role="gridcell"
          class="flex min-h-11 min-w-0 cursor-pointer flex-col items-center justify-center border-b border-r border-surface-border/15 px-1 py-1 text-sm transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 focus-visible:ring-inset"
          :class="[
            cell.inMonth ? 'text-surface-light' : 'text-surface-mid/50',
            cell.key === selectedDate
              ? 'bg-accent-coral/10 text-accent-coral'
              : 'hover:bg-surface-mid/10',
          ]"
          :aria-label="
            cell.isToday
              ? `${cell.key}, today, ${cell.count} tasks`
              : `${cell.key}, ${cell.count} tasks`
          "
          :aria-selected="cell.key === selectedDate"
          :tabindex="cell.key === focusDate ? 0 : -1"
          @click="emit('selectDate', cell.key)"
          @keydown="onDayKeydown($event, cell.key)"
          @focus="focusDate = cell.key"
        >
          <span class="leading-none">{{ cell.day }}</span>
          <span class="mt-0.5 text-[10px] leading-none text-surface-mid">
            <template v-if="cell.isToday">today · </template>
            {{ cell.count }}
          </span>
        </button>
      </div>

      <p v-if="truncated" class="text-xs text-status-warning">
        Showing the first 100 tasks this month. Narrow the month or use the queue for the rest.
      </p>

      <div class="border-t border-surface-border pt-4">
        <h3 class="mb-2 text-sm font-medium text-surface-mid">
          {{ formatDate(selectedDate) }}
        </h3>
        <p v-if="!selectedDayTasks.length" class="text-sm text-surface-mid">
          No tasks on this day.
        </p>
        <ul v-else class="space-y-2">
          <li v-for="task in selectedDayTasks" :key="task.id">
            <button
              type="button"
              class="flex w-full min-w-0 cursor-pointer items-center gap-3 rounded-lg border border-transparent px-3 py-2 text-left transition-colors duration-150 hover:bg-surface-mid/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50"
              @click="emit('selectTask', task.id)"
            >
              <span class="min-w-0 flex-1 truncate text-sm lowercase text-surface-light">
                {{ task.title }}
              </span>
              <span class="shrink-0 text-xs text-datetime">
                {{ formatScheduleDate(task.scheduled_at).headline }}
              </span>
              <StatusBadge
                :label="statusLabel(task.status)"
                :class-name="statusBadgeClass(task.status)"
              />
            </button>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
