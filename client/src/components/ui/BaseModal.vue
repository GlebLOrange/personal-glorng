<script setup lang="ts">
import { computed, ref, useId, useSlots } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import OverlayBackdrop from "@/components/ui/OverlayBackdrop.vue";
import { useOverlayShell } from "@/composables/useOverlayShell";
import { OVERLAY_MAX_WIDTH_CLASS, type OverlayMaxWidth } from "@/constants/overlaySizes";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title?: string;
    maxWidth?: OverlayMaxWidth;
    ariaLabel?: string;
    /** Tighter header/body padding for short dialogs (e.g. confirm). */
    compact?: boolean;
  }>(),
  {
    maxWidth: "lg",
    compact: false,
  },
);

const emit = defineEmits<{ close: [] }>();

const slots = useSlots();
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
const dialogLabel = computed(() => (props.title ? undefined : (props.ariaLabel ?? "dialog")));
const widthClass = computed(() => OVERLAY_MAX_WIDTH_CLASS[props.maxWidth ?? "lg"]);
const hasCustomHeader = computed(() => Boolean(slots.header));
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
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
          <h2 v-if="title && hasCustomHeader" :id="titleId" class="sr-only">{{ title }}</h2>
          <div
            class="flex shrink-0 items-center gap-3 border-b border-surface-border px-4"
            :class="props.compact ? 'py-2' : 'py-3'"
          >
            <div class="flex min-w-0 items-center" :class="props.compact ? 'min-h-8' : 'h-10'">
              <slot name="header" :title-id="titleId">
                <h2
                  v-if="title"
                  :id="titleId"
                  class="truncate font-bold leading-none text-surface-light"
                  :class="props.compact ? 'text-base' : 'text-lg'"
                >
                  {{ title }}
                </h2>
              </slot>
            </div>
            <div
              class="ml-auto flex shrink-0 items-center gap-1"
              :class="props.compact ? 'min-h-8' : 'h-10'"
            >
              <slot name="header-actions" />
              <IconCloseButton
                ref="closeButton"
                aria-label="close"
                :class="props.compact ? '!h-8 !w-8 !min-w-8' : undefined"
                @click="emit('close')"
              />
            </div>
          </div>
          <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain">
            <div :class="props.compact ? 'px-4 py-2.5' : 'px-4 py-4'">
              <slot />
            </div>
          </div>
          <footer
            v-if="$slots.footer"
            class="shrink-0 border-t border-surface-border px-4"
            :class="props.compact ? 'py-2' : 'py-3'"
          >
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
