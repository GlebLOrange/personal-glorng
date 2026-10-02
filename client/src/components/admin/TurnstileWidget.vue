<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{
  siteKey: string;
}>();

const emit = defineEmits<{
  "update:token": [token: string];
  error: [message: string];
}>();

const host = ref<HTMLElement | null>(null);
let widgetId: string | undefined;
let scriptEl: HTMLScriptElement | null = null;

type TurnstileApi = {
  render: (
    el: HTMLElement,
    options: {
      sitekey: string;
      callback: (token: string) => void;
      "error-callback"?: () => void;
      "expired-callback"?: () => void;
      theme?: "auto" | "light" | "dark";
    },
  ) => string;
  remove: (id: string) => void;
  reset: (id?: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

function loadScript(): Promise<TurnstileApi> {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      'script[data-turnstile="1"]',
    );
    if (existing) {
      existing.addEventListener("load", () => {
        if (window.turnstile) resolve(window.turnstile);
        else reject(new Error("Turnstile failed to load"));
      });
      existing.addEventListener("error", () => reject(new Error("Turnstile failed to load")));
      return;
    }
    const el = document.createElement("script");
    el.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    el.async = true;
    el.dataset.turnstile = "1";
    el.onload = () => {
      if (window.turnstile) resolve(window.turnstile);
      else reject(new Error("Turnstile failed to load"));
    };
    el.onerror = () => reject(new Error("Turnstile failed to load"));
    scriptEl = el;
    document.head.appendChild(el);
  });
}

async function mountWidget(): Promise<void> {
  if (!props.siteKey || !host.value) return;
  try {
    const api = await loadScript();
    if (widgetId !== undefined) {
      api.remove(widgetId);
      widgetId = undefined;
    }
    widgetId = api.render(host.value, {
      sitekey: props.siteKey,
      theme: "auto",
      callback: (token: string) => emit("update:token", token),
      "error-callback": () => {
        emit("update:token", "");
        emit("error", "captcha failed. try again");
      },
      "expired-callback": () => emit("update:token", ""),
    });
  } catch {
    emit("error", "captcha failed to load");
  }
}

function reset(): void {
  emit("update:token", "");
  if (widgetId !== undefined && window.turnstile) {
    window.turnstile.reset(widgetId);
  }
}

defineExpose({ reset });

onMounted(() => {
  void mountWidget();
});

watch(
  () => props.siteKey,
  () => {
    void mountWidget();
  },
);

onBeforeUnmount(() => {
  if (widgetId !== undefined && window.turnstile) {
    window.turnstile.remove(widgetId);
    widgetId = undefined;
  }
});
</script>

<template>
  <div ref="host" class="cf-turnstile" data-testid="turnstile-host" />
</template>
