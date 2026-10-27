<script setup lang="ts">
import { computed, useSlots } from "vue";

import { ADMIN_TD_ACTIONS_CLASS, ADMIN_TD_CLASS, ADMIN_TR_CLASS } from "@/constants/adminDataTable";

const props = withDefaults(
  defineProps<{
    interactive?: boolean;
    expanded?: boolean;
    expandable?: boolean;
    /** Set when row contains nested buttons/checkboxes (avoids invalid button nesting). */
    nestedInteractive?: boolean;
    /** Column count for expanded detail row. */
    colSpan?: number;
  }>(),
  {
    interactive: false,
    expanded: false,
    expandable: false,
    nestedInteractive: false,
    colSpan: 5,
  },
);

const emit = defineEmits<{ click: [MouseEvent | KeyboardEvent] }>();
const slots = useSlots();

const focusable = computed(() => props.interactive && !props.nestedInteractive);

const rowClass = computed(() => [
  ADMIN_TR_CLASS,
  props.interactive ? "cursor-pointer" : undefined,
  props.expanded ? "bg-surface-card/50" : undefined,
]);

const rowAttrs = computed(() => {
  if (!focusable.value) return {};
  return {
    role: "button" as const,
    tabindex: 0,
    "aria-expanded": props.expandable ? props.expanded : undefined,
  };
});

function onClick(event: MouseEvent): void {
  if (!props.interactive) return;
  if (props.nestedInteractive) {
    const target = event.target;
    if (target instanceof Element && target.closest("button, a, input, [data-admin-row-stop]")) {
      return;
    }
  }
  emit("click", event);
}

function onKeydown(event: KeyboardEvent): void {
  if (!focusable.value) return;
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    emit("click", event);
  }
}
</script>

<template>
  <tr :class="rowClass" v-bind="rowAttrs" @click="onClick" @keydown="onKeydown">
    <slot />
    <td
      v-if="$slots.actions"
      :class="ADMIN_TD_ACTIONS_CLASS"
      data-admin-row-stop
      @click.stop
      @keydown.stop
    >
      <div class="inline-flex items-center justify-end gap-0.5">
        <slot name="actions" />
      </div>
    </td>
  </tr>
  <tr v-if="expanded && slots.detail">
    <td
      :colspan="colSpan"
      :class="[
        ADMIN_TD_CLASS,
        'border-b border-surface-border/60 bg-surface-dark/40 text-xs text-surface-mid',
      ]"
    >
      <div class="py-1">
        <slot name="detail" />
      </div>
    </td>
  </tr>
</template>
