<script setup lang="ts">
import { ref, useTemplateRef } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { TOOLBAR_POPOVER_PANEL_CHROME_CLASS, TOOLBAR_POPOVER_WIDTH_CLASS } from "@/constants/toolbarPopover";
import { useToolbarOptionsPopover } from "@/composables/useToolbarOptionsPopover";
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
const optionsTrigger = useTemplateRef<InstanceType<typeof ToolbarPillButton>>("optionsTrigger");

const { toggle: toggleOptions } = useToolbarOptionsPopover({
  open: optionsOpen,
  rootRef: optionsRoot,
  panelRef: optionsPanel,
  triggerRef: optionsTrigger,
});
</script>

<template>
  <div
    ref="optionsRoot"
    class="relative inline-flex flex-col"
    :class="[TOOLBAR_POPOVER_WIDTH_CLASS, optionsOpen ? 'z-40' : undefined]"
  >
    <ToolbarPillButton
      ref="optionsTrigger"
      family="1xx"
      type="button"
      class="w-full"
      :selected="optionsOpen || hasCustomOptions"
      aria-haspopup="dialog"
      :aria-expanded="optionsOpen"
      aria-controls="data-extract-options-dialog"
      @click.stop="toggleOptions"
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
      class="absolute left-0 top-full z-10 mt-1 w-full space-y-3"
      :class="TOOLBAR_POPOVER_PANEL_CHROME_CLASS"
      @click.stop
    >
      <h2 id="data-extract-options-title" class="sr-only">extract options</h2>

      <BaseSelect
        id="data-extract-format"
        v-model="formatChoice"
        name="format"
        label="format"
        hint="auto detects from the file extension"
        compact
      >
        <option value="auto">auto</option>
        <option value="csv">CSV</option>
        <option value="json">JSON</option>
        <option value="xml">XML</option>
        <option value="delimited">delimited</option>
      </BaseSelect>

      <BaseSelect
        v-if="showDelimitedOptions"
        id="data-extract-profile"
        v-model="profileChoice"
        name="profile"
        label="profile"
        hint="pipe embed: | fields with ; lists inside cells"
        compact
      >
        <option value="custom">custom delimiters</option>
        <option value="pipe_embed">pipe embed</option>
      </BaseSelect>

      <BaseInput
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        id="data-extract-field-delimiter"
        v-model="fieldDelimiter"
        name="field_delimiter"
        label="field delimiter"
        hint="character between columns"
        maxlength="4"
        placeholder="|"
        compact
      />

      <BaseInput
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        id="data-extract-list-delimiter"
        v-model="listDelimiter"
        name="list_delimiter"
        label="list delimiter"
        hint="character between values inside one cell"
        maxlength="4"
        placeholder=";"
        compact
      />

      <BaseInput
        v-if="showXmlOptions"
        id="data-extract-row-tag"
        v-model="rowTag"
        name="row_tag"
        label="xml row tag"
        hint="repeating element name, e.g. item or row"
        compact
      />

      <BaseSelect
        v-if="showXmlOptions"
        id="data-extract-xml-mode"
        v-model="xmlMode"
        name="xml_mode"
        label="xml mode"
        hint="rows = flat table; tree = nested JSON"
        compact
      >
        <option value="rows">rows</option>
        <option value="tree">tree</option>
      </BaseSelect>
    </div>
  </div>
</template>
