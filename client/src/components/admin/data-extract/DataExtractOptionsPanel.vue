<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, useTemplateRef, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { trapTabKeyInRoot } from "@/composables/useOverlayShell";
import { FIELD_INPUT_CLASS, SELECT_CLASS } from "@/constants/formClasses";
import type { FormatChoice } from "@/composables/useDataExtractTool";
import type { DelimitedProfile, XmlExtractMode } from "@/types/dataExtract";

const formatChoice = defineModel<FormatChoice>("formatChoice", { required: true });
const profileChoice = defineModel<DelimitedProfile>("profileChoice", { required: true });
const fieldDelimiter = defineModel<string>("fieldDelimiter", { required: true });
const listDelimiter = defineModel<string>("listDelimiter", { required: true });
const rowTag = defineModel<string>("rowTag", { required: true });
const xmlMode = defineModel<XmlExtractMode>("xmlMode", { required: true });

defineProps<{
  hasCustomOptions: boolean;
  optionsActiveLabel?: string;
  showDelimitedOptions: boolean;
  showXmlOptions: boolean;
}>();

const optionsOpen = ref(false);
const optionsRoot = useTemplateRef<HTMLElement>("optionsRoot");
const optionsPanel = useTemplateRef<HTMLElement>("optionsPanel");

const LABEL_CLASS = "text-xs font-medium text-surface-mid";
const HINT_CLASS = "col-start-2 text-xs text-surface-mid";
const FIELD_ROW_CLASS = "grid grid-cols-[7rem_minmax(0,1fr)] items-center gap-x-2 gap-y-1";

function closeOptions(): void {
  optionsOpen.value = false;
}

function onDocumentClick(event: MouseEvent): void {
  if (!optionsOpen.value) return;
  const root = optionsRoot.value;
  if (root && !root.contains(event.target as Node)) closeOptions();
}

function onOptionsKeydown(event: KeyboardEvent): void {
  if (!optionsOpen.value) return;
  if (event.key === "Escape") {
    event.stopPropagation();
    event.preventDefault();
    closeOptions();
    return;
  }
  trapTabKeyInRoot(event, optionsPanel.value);
}

watch(optionsOpen, async (isOpen) => {
  if (!isOpen) return;
  await nextTick();
  optionsPanel.value?.focus();
});

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onOptionsKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onOptionsKeydown);
});
</script>

<template>
  <div ref="optionsRoot" class="relative inline-flex" :class="optionsOpen ? 'z-40' : undefined">
    <ToolbarPillButton
      family="1xx"
      type="button"
      :selected="optionsOpen || hasCustomOptions"
      aria-haspopup="dialog"
      :aria-expanded="optionsOpen"
      aria-controls="data-extract-options-dialog"
      @click.stop="optionsOpen = !optionsOpen"
    >
      options
      <span v-if="optionsActiveLabel" class="text-surface-muted"> · {{ optionsActiveLabel }} </span>
      <ChevronIcon :open="optionsOpen" />
    </ToolbarPillButton>

    <div
      v-if="optionsOpen"
      id="data-extract-options-dialog"
      ref="optionsPanel"
      role="dialog"
      aria-labelledby="data-extract-options-title"
      tabindex="-1"
      class="absolute left-0 top-full z-10 mt-1 w-max min-w-[18rem] max-w-[min(100vw-2rem,28rem)] space-y-3 rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg"
      @click.stop
    >
      <h2 id="data-extract-options-title" class="sr-only">extract options</h2>

      <div :class="FIELD_ROW_CLASS">
        <label for="data-extract-format" :class="LABEL_CLASS">format</label>
        <select
          id="data-extract-format"
          v-model="formatChoice"
          name="format"
          aria-describedby="data-extract-format-hint"
          :class="SELECT_CLASS"
        >
          <option value="auto">auto</option>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="xml">XML</option>
          <option value="delimited">delimited</option>
        </select>
        <p id="data-extract-format-hint" :class="HINT_CLASS">
          auto detects from the file extension
        </p>
      </div>

      <div v-if="showDelimitedOptions" :class="FIELD_ROW_CLASS">
        <label for="data-extract-profile" :class="LABEL_CLASS">profile</label>
        <select
          id="data-extract-profile"
          v-model="profileChoice"
          name="profile"
          aria-describedby="data-extract-profile-hint"
          :class="SELECT_CLASS"
        >
          <option value="custom">custom delimiters</option>
          <option value="pipe_embed">pipe embed</option>
        </select>
        <p id="data-extract-profile-hint" :class="HINT_CLASS">
          pipe embed: | fields with ; lists inside cells
        </p>
      </div>

      <div
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        :class="FIELD_ROW_CLASS"
      >
        <label for="data-extract-field-delimiter" :class="LABEL_CLASS">field delimiter</label>
        <input
          id="data-extract-field-delimiter"
          v-model="fieldDelimiter"
          name="field_delimiter"
          type="text"
          maxlength="4"
          placeholder="|"
          aria-describedby="data-extract-field-delimiter-hint"
          :class="[FIELD_INPUT_CLASS, 'min-w-0']"
        />
        <p id="data-extract-field-delimiter-hint" :class="HINT_CLASS">
          character between columns
        </p>
      </div>

      <div
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        :class="FIELD_ROW_CLASS"
      >
        <label for="data-extract-list-delimiter" :class="LABEL_CLASS">list delimiter</label>
        <input
          id="data-extract-list-delimiter"
          v-model="listDelimiter"
          name="list_delimiter"
          type="text"
          maxlength="4"
          placeholder=";"
          aria-describedby="data-extract-list-delimiter-hint"
          :class="[FIELD_INPUT_CLASS, 'min-w-0']"
        />
        <p id="data-extract-list-delimiter-hint" :class="HINT_CLASS">
          character between values inside one cell
        </p>
      </div>

      <div v-if="showXmlOptions" :class="FIELD_ROW_CLASS">
        <label for="data-extract-row-tag" :class="LABEL_CLASS">xml row tag</label>
        <input
          id="data-extract-row-tag"
          v-model="rowTag"
          name="row_tag"
          type="text"
          aria-describedby="data-extract-row-tag-hint"
          :class="[FIELD_INPUT_CLASS, 'min-w-0']"
        />
        <p id="data-extract-row-tag-hint" :class="HINT_CLASS">
          repeating element name, e.g. item or row
        </p>
      </div>

      <div v-if="showXmlOptions" :class="FIELD_ROW_CLASS">
        <label for="data-extract-xml-mode" :class="LABEL_CLASS">xml mode</label>
        <select
          id="data-extract-xml-mode"
          v-model="xmlMode"
          name="xml_mode"
          aria-describedby="data-extract-xml-mode-hint"
          :class="SELECT_CLASS"
        >
          <option value="rows">rows</option>
          <option value="tree">tree</option>
        </select>
        <p id="data-extract-xml-mode-hint" :class="HINT_CLASS">
          rows = flat table; tree = nested JSON
        </p>
      </div>
    </div>
  </div>
</template>
