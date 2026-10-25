<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

type BuildCopy = {
  runs: string;
  api: string;
  gated: string;
};

type BuildLane = {
  label: string;
  text: string;
};

const BUILD_COPY: Record<string, BuildCopy> = {
  weather: {
    runs: "Live weather lookup with pinned cities stored in this browser for guests.",
    api: "Calls /weather for forecasts; guest pins stay local until you sign in.",
    gated: "Cross-device saved locations require a signed-in account.",
  },
  calculator: {
    runs: "Client keypad that evaluates two-operand expressions through the API.",
    api: "POST /tools/calculator with { a, b, op }.",
    gated: "No personal data — the same page works for guests and signed-in users.",
  },
  "password-generator": {
    runs: "Generates a strong password on the server and shows it only in this session.",
    api: "POST /tools/password-generator with length and charset options.",
    gated: "Nothing is stored; regenerate anytime on this page.",
  },
  "qr-generator": {
    runs: "Builds an SVG QR from the payload you enter (sample URL prefilled for demos).",
    api: "POST /tools/qr-generator for generate; library routes need permission.",
    gated: "Save and list your QR library after signing in with write access.",
  },
  "url-shortener": {
    runs: "Create form stays live; guests see sample short-link rows instead of a private list.",
    api: "POST /tools/url-shortener to create; GET list is permission-gated.",
    gated: "View, edit, and delete your short URLs after signing in.",
  },
  recipes: {
    runs: "Guests see static sample cards; signed-in users load the real recipe book.",
    api: "GET /recipes (and write routes) when authenticated.",
    gated: "Personal recipes and cook mode stay behind sign-in — not moved under /admin.",
  },
};

/** Auto-collapse the open spoiler once so the tool form gets the viewport. */
const AUTO_COLLAPSE_MS = 5000;

const props = defineProps<{ slug: string }>();

const isOpen = ref(true);
let collapseTimer: ReturnType<typeof setTimeout> | null = null;

const copy = computed(() => BUILD_COPY[props.slug] ?? null);

const lanes = computed((): BuildLane[] => {
  const current = copy.value;
  if (!current) return [];
  return [
    { label: "runs", text: current.runs },
    { label: "api", text: current.api },
    { label: "behind login", text: current.gated },
  ];
});

function clearCollapseTimer(): void {
  if (collapseTimer !== null) {
    clearTimeout(collapseTimer);
    collapseTimer = null;
  }
}

function onToggle(event: Event): void {
  const details = event.currentTarget;
  if (!(details instanceof HTMLDetailsElement)) return;
  isOpen.value = details.open;
  // User took over — don't force-close after their toggle.
  clearCollapseTimer();
}

onMounted(() => {
  collapseTimer = setTimeout(() => {
    collapseTimer = null;
    isOpen.value = false;
  }, AUTO_COLLAPSE_MS);
});

onUnmounted(() => {
  clearCollapseTimer();
});
</script>

<template>
  <details
    v-if="copy"
    :open="isOpen"
    class="mb-3 rounded-lg border border-surface-border bg-surface-card px-2 py-1"
    @toggle="onToggle"
  >
    <summary
      class="flex min-h-11 cursor-pointer list-none items-center text-sm font-medium text-surface-light [&::-webkit-details-marker]:hidden"
    >
      how this is built
    </summary>
    <dl class="mt-1 flex flex-col gap-y-0.5 border-t border-surface-border pt-1 text-sm leading-tight text-surface-mid">
      <div
        v-for="lane in lanes"
        :key="lane.label"
        class="flex items-baseline gap-3"
      >
        <dt
          class="order-2 shrink-0 whitespace-nowrap text-right text-xs uppercase tracking-wider text-surface-sage"
        >
          {{ lane.label }}
        </dt>
        <dd class="order-1 min-w-0 flex-1 leading-tight">
          {{ lane.text }}
        </dd>
      </div>
    </dl>
  </details>
</template>
