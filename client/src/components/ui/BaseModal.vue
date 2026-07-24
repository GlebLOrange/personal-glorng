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
    title?: string;
    maxWidth?: OverlayMaxWidth;
    ariaLabel?: string;
  }>(),
  {
    maxWidth: "lg",
  },
);

const emit = defineEmits<{ close: [] }>();

const panelRef = ref<HTMLElement | null>(null);
const closeButton = ref<InstanceType<typeof IconCloseButton> | null>(null);
const titleId = useId();

useOverlayShell({
  open: () => props.open,
  panelRef,
  onClose: () => emit("close"),
  initialFocusFallback: () => {
    const el = closeButton.value?.$el;
    return el instanceof HTMLElement ? el : null;
  },
});

const labelledBy = computed(() => (props.title ? titleId : undefined));
const dialogLabel = computed(() =>
  props.title ? undefined : (props.ariaLabel ?? "Dialog"),
);
const widthClass = computed(
  () => OVERLAY_MAX_WIDTH_CLASS[props.maxWidth ?? "lg"],
);
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <OverlayBackdrop @close="emit('close')" />
        <div
          ref="panelRef"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="labelledBy"
          :aria-label="dialogLabel"
          tabindex="-1"
          :class="[
            'relative flex max-h-[calc(100dvh-2rem)] w-full flex-col rounded-xl border border-surface-border bg-surface-card shadow-sm focus:outline-none',
            widthClass,
          ]"
          @click.stop
        >
          <div class="flex shrink-0 items-center gap-2 px-6 pb-3 pt-5">
            <div class="min-w-0 flex-1">
              <slot name="header" :title-id="titleId">
                <h2
                  v-if="title"
                  :id="titleId"
                  class="text-lg font-bold text-surface-light"
                >
                  {{ title }}
                </h2>
              </slot>
            </div>
            <div class="flex shrink-0 items-center gap-1">
              <slot name="header-actions" />
              <IconCloseButton
                ref="closeButton"
                class="w-[10%] shrink-0"
                aria-label="Close"
                @click="emit('close')"
              />
            </div>
          </div>
          <div
            class="min-h-0 flex-1 overflow-y-auto overscroll-contain px-6 pb-8 [scrollbar-gutter:stable]"
          >
            <slot />
          </div>
          <footer
            v-if="$slots.footer"
            class="shrink-0 border-t border-surface-border px-6 py-4"
          >
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
