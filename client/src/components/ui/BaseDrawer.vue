<script setup lang="ts">
import { computed, ref, useId } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import OverlayBackdrop from "@/components/ui/OverlayBackdrop.vue";
import { useOverlayShell } from "@/composables/useOverlayShell";
import {
  OVERLAY_MAX_WIDTH_CLASS,
  type OverlayMaxWidth,
} from "@/constants/overlaySizes";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    maxWidth?: OverlayMaxWidth;
  }>(),
  {
    maxWidth: "lg",
  },
);

const emit = defineEmits<{ close: [] }>();

const panel = ref<HTMLElement | null>(null);
const closeButton = ref<InstanceType<typeof IconCloseButton> | null>(null);
const titleId = useId();

useOverlayShell({
  open: () => props.open,
  panelRef: panel,
  onClose: () => emit("close"),
  initialFocusFallback: () => {
    const el = closeButton.value?.$el;
    return el instanceof HTMLElement ? el : null;
  },
});

const panelWidth = computed(
  () => OVERLAY_MAX_WIDTH_CLASS[props.maxWidth ?? "lg"],
);
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-slide">
      <div v-if="open" class="fixed inset-0 z-50 flex justify-end">
        <OverlayBackdrop @close="emit('close')" />
        <aside
          ref="panel"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :class="[
            'drawer-panel relative flex h-full w-full flex-col border-l border-surface-border bg-surface-dark shadow-xl',
            panelWidth,
          ]"
          @click.stop
        >
          <header
            class="flex shrink-0 items-start justify-between gap-3 border-b border-surface-border px-6 py-4"
          >
            <div class="min-w-0 flex-1">
              <slot name="title" :title-id="titleId">
                <h2 :id="titleId" class="truncate text-lg font-bold text-surface-light">
                  {{ title }}
                </h2>
              </slot>
            </div>
            <div class="flex shrink-0 items-center gap-1">
              <slot name="header-actions" />
              <IconCloseButton
                ref="closeButton"
                aria-label="Close drawer"
                @click="emit('close')"
              />
            </div>
          </header>

          <div class="flex-1 overflow-y-auto px-6 py-5">
            <slot />
          </div>

          <footer
            v-if="$slots.footer"
            class="shrink-0 border-t border-surface-border bg-surface-dark px-6 py-4"
          >
            <slot name="footer" />
          </footer>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>
