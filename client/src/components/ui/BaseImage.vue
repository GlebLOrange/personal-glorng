<script setup lang="ts">
import { nextTick, ref, watch } from "vue";

import { IMAGE_PLACEHOLDER_SRC } from "@/constants/images";

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
  () => props.src,
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
  <div class="relative overflow-hidden">
    <img
      :src="IMAGE_PLACEHOLDER_SRC"
      alt=""
      aria-hidden="true"
      class="absolute inset-0 h-full w-full object-cover"
    />
    <img
      v-if="src && !failed"
      ref="imgRef"
      :src="src"
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
