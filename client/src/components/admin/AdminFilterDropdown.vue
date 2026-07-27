<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  useTemplateRef,
  watch,
  type CSSProperties,
} from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import FilterIcon from "@/components/icons/FilterIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  FILTER_MENU_ROW_CLASS,
  TOOLBAR_POPOVER_MAX_WIDTH_CLASS,
  TOOLBAR_POPOVER_PANEL_CHROME_CLASS,
  TOOLBAR_POPOVER_PANEL_WIDTH_CLASS,
} from "@/constants/toolbarPopover";
import { useToolbarOptionsPopover } from "@/composables/useToolbarOptionsPopover";

const props = withDefaults(
  defineProps<{
    hasActiveFilters?: boolean;
    activeLabel?: string;
    /** All option labels — trigger reserves width for the longest `· label`. */
    optionLabels?: string[];
    /** Trigger prefix text (e.g. "filters", "options", "tags"). */
    label?: string;
    /** Show leading filter icon (filters menus). */
    showFilterIcon?: boolean;
    /** Show clear action at the bottom of the panel. */
    showClear?: boolean;
    /** Transparent trigger — no wash / border chrome. */
    bare?: boolean;
    /** Lock panel width to the trigger (no content growth). */
    matchTriggerWidth?: boolean;
  }>(),
  {
    label: "filters",
    showFilterIcon: true,
    showClear: true,
    bare: false,
    matchTriggerWidth: false,
  },
);

const emit = defineEmits<{
  clear: [];
}>();

/** Labels used to reserve trigger width (never shrink below longest option). */
const sizingLabels = computed(() => {
  const labels = (props.optionLabels ?? []).filter(Boolean);
  if (labels.length) return labels;
  return props.activeLabel ? [props.activeLabel] : [];
});

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<InstanceType<typeof ToolbarPillButton>>("trigger");
const panelRef = useTemplateRef<HTMLElement>("panel");
const measureRef = useTemplateRef<HTMLElement>("measure");
const panelStyle = ref<CSSProperties>({});
/** Longest dropdown line (chips / inputs / footer); trigger may not shrink below this. */
const contentMinWidthPx = ref(0);

const { close, toggle } = useToolbarOptionsPopover({
  open,
  rootRef,
  panelRef,
  triggerRef,
});

const triggerStyle = computed((): CSSProperties | undefined => {
  if (contentMinWidthPx.value <= 0) return undefined;
  return { minWidth: `${contentMinWidthPx.value}px` };
});

const bareTriggerClass = computed(() => {
  if (!props.bare) return undefined;
  const active = open.value;
  return [
    "!bg-transparent hover:enabled:!bg-transparent",
    active
      ? "!border-accent-blue/40"
      : "!border-transparent hover:enabled:!border-accent-blue/40",
  ];
});

function resolveTriggerEl(): HTMLElement | null {
  const trigger = triggerRef.value;
  if (!trigger) return null;
  if (trigger instanceof HTMLElement) return trigger;
  const el = (trigger as { $el?: unknown }).$el;
  return el instanceof HTMLElement ? el : null;
}

/** Widest natural line in the hidden probe (chips sized to label, not stretched). */
function measureContentMinWidth(): void {
  const root = measureRef.value;
  if (!root) return;

  let widest = 0;
  const nodes = root.querySelectorAll<HTMLElement>("button, input, select, textarea, label, span");
  for (const node of nodes) {
    widest = Math.max(widest, Math.ceil(node.scrollWidth));
  }
  widest = Math.max(widest, Math.ceil(root.scrollWidth));
  if (widest > 0) contentMinWidthPx.value = widest;
}

/** Place panel under the trigger; min width matches the bar (already content-floored). */
function syncPanelPosition(): void {
  const trigger = resolveTriggerEl();
  if (!trigger) return;

  const viewportPadding = 16;
  const rect = trigger.getBoundingClientRect();
  const maxWidth = window.innerWidth - viewportPadding * 2;

  if (props.matchTriggerWidth) {
    const width = Math.min(rect.width, maxWidth);
    const maxLeft = Math.max(viewportPadding, window.innerWidth - width - viewportPadding);
    panelStyle.value = {
      top: `${rect.bottom + 4}px`,
      left: `${Math.min(Math.max(rect.left, viewportPadding), maxLeft)}px`,
      width: `${width}px`,
      minWidth: `${width}px`,
      maxWidth: `${width}px`,
    };
    return;
  }

  const minWidth = Math.min(
    Math.max(rect.width, contentMinWidthPx.value),
    maxWidth,
  );
  const panelWidth = Math.max(panelRef.value?.offsetWidth ?? 0, minWidth);
  const maxLeft = Math.max(viewportPadding, window.innerWidth - panelWidth - viewportPadding);
  panelStyle.value = {
    top: `${rect.bottom + 4}px`,
    left: `${Math.min(Math.max(rect.left, viewportPadding), maxLeft)}px`,
    minWidth: `${minWidth}px`,
  };
}

function onViewportChange(): void {
  measureContentMinWidth();
  if (!open.value) return;
  syncPanelPosition();
}

watch(open, async (isOpen) => {
  if (!isOpen) {
    window.removeEventListener("resize", onViewportChange);
    window.removeEventListener("scroll", onViewportChange, true);
    return;
  }
  await nextTick();
  measureContentMinWidth();
  syncPanelPosition();
  requestAnimationFrame(() => {
    measureContentMinWidth();
    syncPanelPosition();
  });
  window.addEventListener("resize", onViewportChange);
  window.addEventListener("scroll", onViewportChange, true);
});

onMounted(async () => {
  await nextTick();
  measureContentMinWidth();
  requestAnimationFrame(() => {
    measureContentMinWidth();
  });
  window.addEventListener("resize", onViewportChange);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onViewportChange);
  window.removeEventListener("scroll", onViewportChange, true);
});

function onClear(): void {
  emit("clear");
  close();
}

defineExpose({ close });
</script>

<template>
  <div ref="root" class="relative inline-flex" :class="open ? 'z-40' : undefined">
    <ToolbarPillButton
      ref="trigger"
      family="1xx"
      :class="[TOOLBAR_POPOVER_MAX_WIDTH_CLASS, bareTriggerClass]"
      :style="triggerStyle"
      :selected="bare ? open : open || hasActiveFilters"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      <FilterIcon v-if="showFilterIcon" class-name="size-3.5" />
      {{ label }}
      <span v-if="sizingLabels.length" class="inline-grid justify-items-start">
        <span
          v-for="opt in sizingLabels"
          :key="opt"
          class="invisible col-start-1 row-start-1 whitespace-nowrap"
          aria-hidden="true"
        >
          · {{ opt }}
        </span>
        <span
          v-if="activeLabel"
          class="col-start-1 row-start-1 truncate whitespace-nowrap text-surface-muted"
        >
          · {{ activeLabel }}
        </span>
      </span>
      <ChevronIcon :open="open" />
    </ToolbarPillButton>

    <!-- Probe: natural width of dropdown lines (not stretched). CSS max-w still caps the trigger. -->
    <div
      ref="measure"
      class="pointer-events-none invisible absolute left-0 top-0 -z-10 w-max whitespace-nowrap"
      aria-hidden="true"
    >
      <div v-if="$slots.chips" class="flex w-max flex-col [&_button]:!w-auto">
        <slot name="chips" />
      </div>
      <div v-if="$slots.default" class="w-max [&_*]:max-w-none">
        <slot />
      </div>
      <div v-if="$slots.footer" class="w-max [&_button]:!w-auto">
        <slot name="footer" />
      </div>
      <span v-if="showClear" class="inline-block px-2 text-xs leading-normal">clear</span>
    </div>

    <Teleport to="body">
      <div
        v-if="open"
        ref="panel"
        role="dialog"
        :aria-label="label"
        tabindex="-1"
        class="fixed z-50"
        :class="[
          matchTriggerWidth ? TOOLBAR_POPOVER_MAX_WIDTH_CLASS : TOOLBAR_POPOVER_PANEL_WIDTH_CLASS,
          TOOLBAR_POPOVER_PANEL_CHROME_CLASS,
        ]"
        :style="panelStyle"
        @click.stop
      >
        <div class="space-y-3">
          <div v-if="$slots.chips" class="flex flex-col gap-2">
            <slot name="chips" />
          </div>
          <slot />
        </div>
        <slot name="footer" />
        <div v-if="showClear" class="mt-3">
          <button
            type="button"
            :class="[
              FILTER_MENU_ROW_CLASS,
              'justify-start border-transparent bg-transparent text-surface-mid transition-colors hover:enabled:border-status-error/40 hover:enabled:bg-status-error/15 hover:enabled:text-status-error',
            ]"
            :disabled="!hasActiveFilters"
            @click="onClear"
          >
            clear
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
