<script setup lang="ts">
import { computed, ref, useId, useTemplateRef } from "vue";

const props = withDefaults(
  defineProps<{
    /** Accessible name for the drop zone control. */
    ariaLabel?: string;
    /** Optional accept attribute for the hidden file input (e.g. ".csv,.json"). */
    accept?: string;
    /** Optional hint shown under the browse copy; wired via aria-describedby. */
    hint?: string;
    /** Selected file display name (empty when none). */
    selectedName?: string;
    /** Extra class on the outer drop zone. */
    class?: string;
  }>(),
  {
    ariaLabel: "choose a file",
  },
);

const emit = defineEmits<{
  select: [file: File];
}>();

const dragOver = ref(false);
const fileInputRef = useTemplateRef<HTMLInputElement>("fileInput");
const hintId = useId();
const describedBy = computed(() => (props.selectedName || !props.hint ? undefined : hintId));

function openPicker(): void {
  fileInputRef.value?.click();
}

function onFileSelect(event: Event): void {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) emit("select", file);
}

function onDrop(event: DragEvent): void {
  dragOver.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) emit("select", file);
}

function clear(): void {
  if (fileInputRef.value) fileInputRef.value.value = "";
}

defineExpose({ clear });
</script>

<template>
  <div
    role="button"
    tabindex="0"
    :aria-label="ariaLabel"
    :aria-describedby="describedBy"
    :class="[
      'cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors',
      dragOver
        ? 'border-accent-blue bg-accent-blue/10'
        : 'border-surface-border hover:border-accent-blue',
      props.class,
    ]"
    @dragover.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="onDrop"
    @click="openPicker"
    @keydown.enter.prevent="openPicker"
    @keydown.space.prevent="openPicker"
  >
    <input ref="fileInput" type="file" class="hidden" :accept="accept" @change="onFileSelect" />
    <p v-if="selectedName" class="text-sm text-surface-light">{{ selectedName }}</p>
    <template v-else>
      <p class="text-sm text-surface-mid">drop a file here or click to browse</p>
      <p v-if="hint" :id="hintId" class="mt-1 text-xs text-surface-mid">{{ hint }}</p>
    </template>
  </div>
</template>
