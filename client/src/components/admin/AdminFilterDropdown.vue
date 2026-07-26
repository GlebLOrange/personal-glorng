<script setup lang="ts">
import {
  nextTick,
  onBeforeUnmount,
  ref,
  useTemplateRef,
  watch,
  type CSSProperties,
} from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import FilterIcon from "@/components/icons/FilterIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { TOOLBAR_POPOVER_PANEL_CHROME_CLASS } from "@/constants/toolbarPopover";
import { useToolbarOptionsPopover } from "@/composables/useToolbarOptionsPopover";

withDefaults(
  defineProps<{
    hasActiveFilters?: boolean;
    activeLabel?: string;
    /** Trigger prefix text (e.g. "filters", "tags"). */
    label?: string;
  }>(),
  {
    label: "filters",
  },
);

const emit = defineEmits<{
  clear: [];
}>();

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const triggerRef = useTemplateRef<InstanceType<typeof ToolbarPillButton>>("trigger");
const panelRef = useTemplateRef<HTMLElement>("panel");
const panelStyle = ref<CSSProperties>({});
const triggerStyle = ref<CSSProperties>({});

const { close, toggle } = useToolbarOptionsPopover({
  open,
  rootRef,
  panelRef,
  triggerRef,
});

function resolveTriggerEl(): HTMLElement | null {
  const trigger = triggerRef.value;
  if (!trigger) return null;
  if (trigger instanceof HTMLElement) return trigger;
  const el = (trigger as { $el?: unknown }).$el;
  return el instanceof HTMLElement ? el : null;
}

/** Place panel under the trigger; size both to the longest menu label. */
function syncPanelLayout(): void {
  const trigger = resolveTriggerEl();
  const panel = panelRef.value;
  if (!trigger || !panel) return;

  const rect = trigger.getBoundingClientRect();
  // Content-fit panel (no minWidth from trigger — longest chip/footer wins).
  panelStyle.value = {
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
  };

  // Match filters pill to panel width after content lays out.
  const width = panel.offsetWidth;
  if (width > 0) {
    triggerStyle.value = { width: `${width}px` };
  }
}

function onViewportChange(): void {
  if (!open.value) return;
  syncPanelLayout();
}

watch(open, async (isOpen) => {
  if (!isOpen) {
    triggerStyle.value = {};
    window.removeEventListener("resize", onViewportChange);
    window.removeEventListener("scroll", onViewportChange, true);
    return;
  }
  await nextTick();
  syncPanelLayout();
  // Second frame: chips/footer may still be settling intrinsic width.
  requestAnimationFrame(() => {
    syncPanelLayout();
  });
  window.addEventListener("resize", onViewportChange);
  window.addEventListener("scroll", onViewportChange, true);
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
      class="w-full"
      :style="triggerStyle"
      :selected="open || hasActiveFilters"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      <FilterIcon class-name="size-3.5" />
      {{ label }}<span v-if="activeLabel" class="text-surface-muted"> · {{ activeLabel }}</span>
      <ChevronIcon :open="open" />
    </ToolbarPillButton>

    <Teleport to="body">
      <div
        v-if="open"
        ref="panel"
        role="dialog"
        :aria-label="label"
        tabindex="-1"
        class="fixed z-50 w-max max-w-[min(100vw-2rem,28rem)]"
        :class="TOOLBAR_POPOVER_PANEL_CHROME_CLASS"
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
        <div class="mt-3">
          <button
            type="button"
            class="w-full whitespace-nowrap rounded-lg border border-transparent bg-transparent px-2 py-1 text-left text-xs leading-normal text-surface-mid transition-colors hover:enabled:border-status-error/40 hover:enabled:bg-status-error/15 hover:enabled:text-status-error focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:cursor-not-allowed disabled:opacity-50"
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
