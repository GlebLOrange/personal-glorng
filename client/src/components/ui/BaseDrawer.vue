<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, watch } from "vue";

import { useScrollLock } from "@/composables/useScrollLock";
import { focusEditableField } from "@/utils/focusField";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    maxWidth?: "md" | "lg" | "xl";
  }>(),
  {
    maxWidth: "lg",
  },
);

const emit = defineEmits<{ close: [] }>();

const panel = ref<HTMLElement | null>(null);
const closeButton = ref<HTMLButtonElement | null>(null);
let returnFocusTarget: HTMLElement | null = null;

useScrollLock(() => props.open);

const panelWidth = computed(() => {
  if (props.maxWidth === "md") return "max-w-md";
  if (props.maxWidth === "xl") return "max-w-2xl";
  return "max-w-lg";
});

function focusableElements(): HTMLElement[] {
  const root = panel.value;
  if (!root) return [];
  return Array.from(
    root.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  );
}

function trapFocus(event: KeyboardEvent): void {
  const focusable = focusableElements();
  const first = focusable[0];
  const last = focusable.at(-1);
  if (!first || !last) return;

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
    return;
  }
  if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    emit("close");
    return;
  }
  if (event.key === "Tab") trapFocus(event);
}

watch(
  () => props.open,
  async (open) => {
    if (!open) {
      document.removeEventListener("keydown", onKeydown);
      await nextTick();
      returnFocusTarget?.focus();
      return;
    }

    returnFocusTarget =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.addEventListener("keydown", onKeydown);
    await nextTick();
    focusEditableField(panel.value, closeButton.value);
  },
  { immediate: true },
);

onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex justify-end">
      <Transition name="fade">
        <div
          v-if="open"
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          aria-hidden="true"
          @click="emit('close')"
        />
      </Transition>
      <Transition name="drawer-slide" appear>
        <aside
          v-if="open"
          ref="panel"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          :class="[
            'drawer-panel relative flex h-full w-full flex-col border-l border-surface-border bg-surface-dark shadow-xl',
            panelWidth,
          ]"
          @click.stop
        >
          <header
            class="flex shrink-0 items-start justify-between gap-3 border-b border-surface-border px-6 py-4"
          >
            <h2 class="min-w-0 flex-1 truncate text-lg font-bold text-surface-light">
              <slot name="title">
                {{ title }}
              </slot>
            </h2>
            <div class="flex shrink-0 items-center gap-1">
              <slot name="header-actions" />
              <button
                ref="closeButton"
                type="button"
                class="min-h-11 min-w-11 rounded text-xl leading-none text-surface-mid hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
                aria-label="Close drawer"
                @click="emit('close')"
              >
                &times;
              </button>
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
      </Transition>
    </div>
  </Teleport>
</template>
