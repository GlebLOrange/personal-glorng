<script setup lang="ts">
import { computed, useSlots } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
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
    /** Optional accessible name override; omit to use primary slot text. */
    openLabel?: string;
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
const slots = useSlots();

const focusable = computed(() => props.interactive && !props.nestedInteractive);
const primaryAsOpenControl = computed(
  () => props.interactive && props.nestedInteractive && Boolean(slots.primary),
);

const rowAttrs = computed(() => {
  if (!focusable.value) return {};
  return {
    role: "button",
    tabindex: 0,
  };
});

function onClick(event: MouseEvent): void {
  if (!props.interactive) return;
  // Nested primary button already handles activation; ignore bubbled clicks from it.
  if (primaryAsOpenControl.value) {
    const target = event.target;
    if (target instanceof Element && target.closest("[data-admin-list-open]")) {
      return;
    }
  }
  emit("click", event);
}

function onPrimaryOpen(event: MouseEvent): void {
  event.stopPropagation();
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
    variant="ghost"
    :hoverable="false"
    :interactive="focusable"
    :aria-expanded="expandable ? expanded : undefined"
    v-bind="rowAttrs"
    :class="[
      interactive ? 'cursor-pointer' : undefined,
      revealActionsOnHover ? 'group' : undefined,
      hoverable ? 'hover:bg-surface-light/5' : undefined,
    ]"
    class="w-full min-w-0 rounded-lg px-2 py-1.5 text-left"
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
        <button
          v-if="primaryAsOpenControl"
          type="button"
          data-admin-list-open
          class="min-w-0 flex-1 truncate text-left text-sm font-medium text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          :aria-label="openLabel"
          @click="onPrimaryOpen"
        >
          <slot name="primary" />
        </button>
        <span
          v-else-if="$slots.primary"
          class="min-w-0 flex-1 truncate text-sm font-medium text-surface-light"
        >
          <slot name="primary" />
        </span>
        <span v-if="$slots.meta" class="hidden truncate text-xs text-surface-muted sm:inline">
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
      <ChevronIcon
        v-if="expandable"
        direction="right"
        :open="expanded"
        class-name="size-3.5 text-surface-muted"
      />
    </div>
    <div
      v-if="expanded && $slots.detail"
      class="mt-2 border-t border-surface-border pt-2 text-xs text-surface-mid"
    >
      <slot name="detail" />
    </div>
  </Card>
</template>
