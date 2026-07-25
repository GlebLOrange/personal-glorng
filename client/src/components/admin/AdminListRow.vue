<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";

const props = withDefaults(
  defineProps<{
    interactive?: boolean;
    expanded?: boolean;
    hoverable?: boolean;
    expandable?: boolean;
    /** Set when row contains nested buttons/checkboxes (avoids invalid button nesting). */
    nestedInteractive?: boolean;
    /** Hide row actions until hover or focus-within (keyboard accessible). */
    revealActionsOnHover?: boolean;
  }>(),
  {
    interactive: false,
    expanded: false,
    hoverable: true,
    expandable: false,
    nestedInteractive: false,
    revealActionsOnHover: false,
  },
);

const emit = defineEmits<{ click: [MouseEvent | KeyboardEvent] }>();

const focusable = computed(() => props.interactive && !props.nestedInteractive);

const rowAttrs = computed(() => {
  if (!focusable.value) return {};
  return {
    role: "button",
    tabindex: 0,
  };
});

function onClick(event: MouseEvent): void {
  if (!props.interactive) return;
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
  <Card
    as="div"
    variant="dense"
    :hoverable="hoverable && interactive"
    :interactive="focusable"
    :aria-expanded="expandable ? expanded : undefined"
    v-bind="rowAttrs"
    :class="[
      interactive ? 'cursor-pointer' : undefined,
      revealActionsOnHover ? 'group' : undefined,
    ]"
    class="w-full min-w-0 text-left"
    @click="onClick"
    @keydown="onKeydown"
  >
    <div class="flex min-w-0 items-center gap-2">
      <div v-if="$slots.leading" class="shrink-0" @click.stop @keydown.stop>
        <slot name="leading" />
      </div>
      <div v-if="$slots.badge" class="shrink-0">
        <slot name="badge" />
      </div>
      <div class="flex min-w-0 flex-1 items-center gap-2 overflow-hidden">
        <span v-if="$slots.primary" class="truncate text-sm font-medium text-surface-light">
          <slot name="primary" />
        </span>
        <span
          v-if="$slots.meta"
          class="hidden truncate text-xs text-surface-muted sm:inline"
        >
          <slot name="meta" />
        </span>
      </div>
      <div v-if="$slots.time" class="shrink-0 whitespace-nowrap text-xs text-surface-muted">
        <slot name="time" />
      </div>
      <div
        v-if="$slots.actions"
        class="flex shrink-0 items-center gap-1"
        :class="
          revealActionsOnHover
            ? 'opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-within:opacity-100 [@media(hover:none)]:opacity-100'
            : undefined
        "
        @click.stop
        @keydown.stop
      >
        <slot name="actions" />
      </div>
      <span
        v-if="expandable"
        class="shrink-0 text-xs text-surface-muted"
        aria-hidden="true"
      >
        {{ expanded ? "▾" : "▸" }}
      </span>
    </div>
    <div
      v-if="expanded && $slots.detail"
      class="mt-2 border-t border-surface-border pt-2 text-xs text-surface-mid"
    >
      <slot name="detail" />
    </div>
  </Card>
</template>
