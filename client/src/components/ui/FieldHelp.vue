<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  useId,
  useTemplateRef,
  watch,
} from "vue";

import QuestionIcon from "@/components/icons/QuestionIcon.vue";

const props = withDefaults(
  defineProps<{
    /** Help copy shown in the popover; also exposed to assistive tech via contentId. */
    text: string;
    /** Optional id for the help content (for aria-describedby). */
    contentId?: string;
    /** Tooltip edge alignment relative to the ? control. */
    align?: "start" | "end";
    /** Prefer `top` when the control sits on the trailing edge of a field. */
    placement?: "bottom" | "top";
    /** `sm` fits the border-notch label row; `md` is the standalone hit target. */
    size?: "md" | "sm";
  }>(),
  { align: "start", placement: "bottom", size: "md" },
);

const buttonClass = computed(() =>
  props.size === "sm"
    ? "inline-flex size-4 items-center justify-center rounded-full text-surface-mid transition-colors hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
    : "inline-flex h-10 w-10 items-center justify-center rounded-full text-surface-mid transition-colors hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50",
);

const iconClass = computed(() => (props.size === "sm" ? "size-3" : "size-3.5"));

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const buttonRef = useTemplateRef<HTMLButtonElement>("buttonEl");
const panelStyle = ref<Record<string, string>>({});
const fallbackId = useId();
const panelId = computed(() => props.contentId ?? `field-help-${fallbackId}`);
/** Focus opens the tip; the same user gesture's click must not immediately toggle it shut. */
let suppressClickToggle = false;

/** Arrow sits on the panel edge that faces the ? (top-right when placement=top + align=end). */
const arrowClass = computed(() => {
  const edge = props.align === "end" ? "right-2.5" : "left-2.5";
  // Rotated square keeps a real border (CSS triangles often lose the outline).
  if (props.placement === "top") {
    return `absolute top-full ${edge} -mt-[5px] size-2.5 rotate-45 border-b border-r border-surface-border bg-surface-card`;
  }
  return `absolute bottom-full ${edge} -mb-[5px] size-2.5 rotate-45 border-l border-t border-surface-border bg-surface-card`;
});

let closeTimer: ReturnType<typeof setTimeout> | null = null;

function clearCloseTimer(): void {
  if (closeTimer !== null) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
}

function syncPanelPosition(): void {
  const btn = buttonRef.value;
  if (!btn) return;
  const r = btn.getBoundingClientRect();
  if (r.width === 0 && r.height === 0) return;
  const gap = 8;
  // Anchor to the button's top-right (or top-left) corner for placement=top.
  if (props.placement === "top") {
    if (props.align === "end") {
      panelStyle.value = {
        top: `${Math.round(r.top - gap)}px`,
        left: `${Math.round(r.right)}px`,
        transform: "translate(-100%, -100%)",
      };
    } else {
      panelStyle.value = {
        top: `${Math.round(r.top - gap)}px`,
        left: `${Math.round(r.left)}px`,
        transform: "translateY(-100%)",
      };
    }
    return;
  }
  if (props.align === "end") {
    panelStyle.value = {
      top: `${Math.round(r.bottom + gap)}px`,
      left: `${Math.round(r.right)}px`,
      transform: "translateX(-100%)",
    };
  } else {
    panelStyle.value = {
      top: `${Math.round(r.bottom + gap)}px`,
      left: `${Math.round(r.left)}px`,
    };
  }
}

async function show(): Promise<void> {
  clearCloseTimer();
  open.value = true;
  await nextTick();
  syncPanelPosition();
}

function scheduleHide(): void {
  clearCloseTimer();
  closeTimer = setTimeout(() => {
    open.value = false;
    closeTimer = null;
  }, 120);
}

function hide(): void {
  clearCloseTimer();
  suppressClickToggle = false;
  open.value = false;
}

function onFocus(): void {
  suppressClickToggle = true;
  void show();
}

function toggle(): void {
  if (suppressClickToggle) {
    suppressClickToggle = false;
    return;
  }
  clearCloseTimer();
  if (open.value) {
    open.value = false;
    return;
  }
  void show();
}

function onDocumentPointerDown(event: PointerEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  const target = event.target;
  if (!(target instanceof Node)) return;
  if (root?.contains(target)) return;
  const panel = document.getElementById(panelId.value);
  if (panel?.contains(target)) return;
  hide();
}

function onDocumentKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && open.value) {
    event.stopPropagation();
    hide();
  }
}

function onReposition(): void {
  if (open.value) syncPanelPosition();
}

onMounted(() => {
  document.addEventListener("pointerdown", onDocumentPointerDown, true);
  document.addEventListener("keydown", onDocumentKeydown, true);
  window.addEventListener("scroll", onReposition, true);
  window.addEventListener("resize", onReposition);
});

onBeforeUnmount(() => {
  clearCloseTimer();
  document.removeEventListener("pointerdown", onDocumentPointerDown, true);
  document.removeEventListener("keydown", onDocumentKeydown, true);
  window.removeEventListener("scroll", onReposition, true);
  window.removeEventListener("resize", onReposition);
});

watch(
  () => props.text,
  () => hide(),
);
</script>

<template>
  <span
    ref="root"
    class="relative inline-flex shrink-0"
    @mouseenter="show"
    @mouseleave="scheduleHide"
  >
    <button
      ref="buttonEl"
      type="button"
      :class="buttonClass"
      aria-label="help"
      :aria-expanded="open"
      :aria-controls="panelId"
      @click.stop="toggle"
      @focus="onFocus"
      @blur="scheduleHide"
    >
      <QuestionIcon :class-name="iconClass" />
    </button>
    <!-- Always in DOM for aria-describedby; visually teleported when open so overflow shells cannot clip. -->
    <span :id="panelId" class="sr-only">{{ text }}</span>
    <Teleport to="body">
      <span
        v-if="open"
        role="tooltip"
        class="pointer-events-none fixed z-50 w-max max-w-[min(100vw-2rem,18rem)] rounded-md border border-surface-border bg-surface-card px-2.5 py-1.5 text-xs lowercase leading-normal text-surface-mid shadow-lg"
        :style="panelStyle"
        @mouseenter="show"
        @mouseleave="scheduleHide"
      >
        {{ text }}
        <span aria-hidden="true" :class="arrowClass" />
      </span>
    </Teleport>
  </span>
</template>
