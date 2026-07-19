<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import { IMAGE_PLACEHOLDER_SRC } from "@/constants/images";
import { safeImageSrc } from "@/utils/safeImageSrc";

const props = withDefaults(
  defineProps<{
    src?: string | null;
    alt: string;
    lazy?: boolean;
    width?: number | string;
    height?: number | string;
  }>(),
  {
    lazy: true,
  },
);

const safeSrc = computed(() => safeImageSrc(props.src));

const aspectStyle = computed(() => {
  const w = Number(props.width);
  const h = Number(props.height);
  if (Number.isFinite(w) && Number.isFinite(h) && w > 0 && h > 0) {
    return { aspectRatio: `${w} / ${h}` };
  }
  return undefined;
});

const imgRef = ref<HTMLImageElement | null>(null);
const loaded = ref(false);
const failed = ref(false);

async function syncLoadState(): Promise<void> {
  await nextTick();
  const el = imgRef.value;
  if (el?.complete && el.naturalWidth > 0) {
    loaded.value = true;
  }
}

watch(
  safeSrc,
  (src) => {
    loaded.value = false;
    failed.value = false;
    if (src) {
      void syncLoadState();
    }
  },
  { immediate: true },
);

function onLoad(): void {
  loaded.value = true;
}

function onError(): void {
  failed.value = true;
  loaded.value = false;
}
</script>

<template>
  <div class="relative overflow-hidden" :style="aspectStyle">
    <img
      :src="IMAGE_PLACEHOLDER_SRC"
      alt=""
      aria-hidden="true"
      class="absolute inset-0 h-full w-full object-cover"
    />
    <img
      v-if="safeSrc && !failed"
      ref="imgRef"
      :src="safeSrc"
      :alt="alt"
      :loading="lazy ? 'lazy' : 'eager'"
      decoding="async"
      :width="width"
      :height="height"
      class="relative h-full w-full object-cover transition-opacity duration-150"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="onLoad"
      @error="onError"
    />
  </div>
</template>
