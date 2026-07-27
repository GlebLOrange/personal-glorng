<script setup lang="ts">
import { computed, useSlots } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import { Card } from "@/components/ui/card";
import { CONTROL_SIZE } from "@/constants/formClasses";

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
    /** Absolutely center the meta slot in the row (e.g. short URL). */
    centerMeta?: boolean;
    /** Optional accessible name override; omit to use primary slot text. */
    openLabel?: string;
    /** Status badge classes — border/bg tint the row on hover / focus / expanded. */
    statusClass?: string;
  }>(),
  {
    interactive: false,
    expanded: false,
    hoverable: true,
    expandable: false,
    nestedInteractive: false,
    revealActionsOnHover: false,
    centerMeta: false,
  },
);

const emit = defineEmits<{ click: [MouseEvent | KeyboardEvent] }>();
const slots = useSlots();

const focusable = computed(() => props.interactive && !props.nestedInteractive);
const primaryAsOpenControl = computed(
  () => props.interactive && props.nestedInteractive && Boolean(slots.primary),
);

/**
 * Full static class strings so Tailwind keeps them.
 * Idle is surface-card; status wash paints only on hover / focus / expanded.
 * Use ring-inset (not border) so CONTROL_SIZE matches BaseInput / icon buttons.
 */
const STATUS_ROW_TONES: Record<string, { interactive: string; active: string }> = {
  "accent-blue": {
    interactive:
      "hover:!ring-accent-blue/50 focus-visible:!ring-accent-blue/50 focus-within:!ring-accent-blue/50 hover:!bg-accent-blue/15 focus-visible:!bg-accent-blue/15 focus-within:!bg-accent-blue/15",
    active: "!ring-accent-blue/50 !bg-accent-blue/15",
  },
  "status-success": {
    interactive:
      "hover:!ring-status-success/50 focus-visible:!ring-status-success/50 focus-within:!ring-status-success/50 hover:!bg-status-success/15 focus-visible:!bg-status-success/15 focus-within:!bg-status-success/15",
    active: "!ring-status-success/50 !bg-status-success/15",
  },
  "status-warning": {
    interactive:
      "hover:!ring-status-warning/50 focus-visible:!ring-status-warning/50 focus-within:!ring-status-warning/50 hover:!bg-status-warning/15 focus-visible:!bg-status-warning/15 focus-within:!bg-status-warning/15",
    active: "!ring-status-warning/50 !bg-status-warning/15",
  },
  "status-error": {
    interactive:
      "hover:!ring-status-error/50 focus-visible:!ring-status-error/50 focus-within:!ring-status-error/50 hover:!bg-status-error/15 focus-visible:!bg-status-error/15 focus-within:!bg-status-error/15",
    active: "!ring-status-error/50 !bg-status-error/15",
  },
  "status-critical": {
    interactive:
      "hover:!ring-status-critical/50 focus-visible:!ring-status-critical/50 focus-within:!ring-status-critical/50 hover:!bg-status-critical/15 focus-visible:!bg-status-critical/15 focus-within:!bg-status-critical/15",
    active: "!ring-status-critical/50 !bg-status-critical/15",
  },
  "surface-mid": {
    interactive:
      "hover:!ring-surface-border focus-visible:!ring-surface-border focus-within:!ring-surface-border hover:!bg-surface-mid/10 focus-visible:!bg-surface-mid/10 focus-within:!bg-surface-mid/10",
    active: "!ring-surface-border !bg-surface-mid/10",
  },
};

function statusToneKey(statusClass: string): string | null {
  for (const key of Object.keys(STATUS_ROW_TONES)) {
    if (statusClass.includes(key)) return key;
  }
  return null;
}

const statusToneClass = computed(() => {
  if (!props.statusClass) return "";
  const key = statusToneKey(props.statusClass);
  if (!key) return "";
  const tone = STATUS_ROW_TONES[key];
  return [tone.interactive, props.expanded ? tone.active : undefined].filter(Boolean).join(" ");
});

const showNeutralHover = computed(() => props.hoverable && !props.statusClass);

/** Computed so Tailwind class strings never nest `"` inside a `:class="..."` attribute. */
const rowClass = computed(() => [
  props.interactive ? "cursor-pointer" : undefined,
  props.revealActionsOnHover || props.centerMeta ? "group relative" : undefined,
  showNeutralHover.value
    ? "hover:ring-accent-blue/40 hover:bg-surface-light/10 focus-visible:ring-accent-blue/40 focus-within:ring-accent-blue/40"
    : undefined,
  statusToneClass.value || undefined,
]);

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
    :class="rowClass"
    class="admin-list-row-rule flex w-full min-w-0 flex-col justify-start overflow-hidden rounded-md !border-0 !bg-surface-card px-2 text-left ring-1 ring-inset ring-transparent"
    @click="onClick"
    @keydown="onKeydown"
  >
    <div
      data-admin-list-header
      :class="['flex w-full min-w-0 shrink-0 items-center gap-2', CONTROL_SIZE]"
    >
      <div
        v-if="$slots.leading"
        class="flex shrink-0 items-center"
        @click.stop
        @keydown.stop
      >
        <slot name="leading" />
      </div>
      <div v-if="$slots.badge" class="flex h-full shrink-0 items-center">
        <slot name="badge" />
      </div>
      <div class="flex min-w-0 flex-1 items-center gap-2 overflow-hidden">
        <button
          v-if="primaryAsOpenControl"
          type="button"
          data-admin-list-open
          class="min-w-0 flex-1 truncate rounded text-left text-sm font-medium leading-none text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
          :aria-label="openLabel"
          @click="onPrimaryOpen"
        >
          <slot name="primary" />
        </button>
        <span
          v-else-if="$slots.primary"
          class="min-w-0 flex-1 truncate text-sm font-medium leading-none text-surface-light"
        >
          <slot name="primary" />
        </span>
        <span
          v-if="$slots.meta && !centerMeta"
          class="hidden truncate text-xs lowercase leading-none text-surface-muted sm:inline"
        >
          <slot name="meta" />
        </span>
      </div>
      <div
        v-if="$slots.meta && centerMeta"
        class="pointer-events-none absolute inset-0 hidden items-center justify-center sm:flex"
      >
        <span class="pointer-events-auto max-w-[min(100%,24rem)] truncate px-2 text-xs lowercase leading-none text-surface-muted">
          <slot name="meta" />
        </span>
      </div>
      <div
        v-if="$slots.time"
        class="shrink-0 whitespace-nowrap text-xs lowercase leading-none text-surface-muted"
      >
        <slot name="time" />
      </div>
      <!-- In-flow actions only when always visible — hover actions overlay so h-10 icons don't skew centering. -->
      <div
        v-if="$slots.actions && !revealActionsOnHover"
        class="flex shrink-0 items-center gap-1"
        @click.stop
        @keydown.stop
      >
        <slot name="actions" />
      </div>
      <ChevronIcon
        v-if="expandable"
        direction="right"
        :open="expanded"
        class-name="size-3.5 shrink-0 text-surface-muted"
      />
    </div>
    <div
      v-if="$slots.actions && revealActionsOnHover"
      class="absolute inset-y-0 right-1 z-10 flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-within:opacity-100 [@media(hover:none)]:opacity-100 [&_button]:!h-full [&_button]:!max-h-full [&_button]:!min-h-0 [&_button]:!w-10 [&_button]:!min-w-0"
      @click.stop
      @keydown.stop
    >
      <slot name="actions" />
    </div>
    <div
      v-if="expanded && $slots.detail"
      class="mt-2 border-t border-surface-border pt-2 pb-2 text-xs text-surface-mid"
    >
      <slot name="detail" />
    </div>
  </Card>
</template>
