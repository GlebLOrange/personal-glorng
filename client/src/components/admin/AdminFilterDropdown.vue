<script setup lang="ts">
import { ref, useTemplateRef } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
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

const { close, toggle } = useToolbarOptionsPopover({
  open,
  rootRef,
  panelRef,
  triggerRef,
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
      :selected="open || hasActiveFilters"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      {{ label }}<span v-if="activeLabel" class="text-surface-muted"> · {{ activeLabel }}</span>
      <ChevronIcon :open="open" />
    </ToolbarPillButton>

    <div
      v-if="open"
      ref="panel"
      role="dialog"
      :aria-label="label"
      tabindex="-1"
      class="absolute left-0 top-full z-10 mt-1 w-max max-w-[min(100vw-2rem,36rem)] rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg"
      @click.stop
    >
      <div class="space-y-3">
        <div v-if="$slots.chips" class="flex flex-col gap-2">
          <slot name="chips" />
        </div>
        <slot />
      </div>
      <slot name="footer" />
      <div class="mt-3 flex flex-wrap justify-start gap-2">
        <BaseButton variant="ghost" danger size="sm" :disabled="!hasActiveFilters" @click="onClear">
          clear
        </BaseButton>
      </div>
    </div>
  </div>
</template>
