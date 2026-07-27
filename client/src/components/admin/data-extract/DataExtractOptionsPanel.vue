<script setup lang="ts">
import { computed } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
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

const optionLabels = computed(() => [
  "auto",
  "csv",
  "JSON",
  "xml",
  "delimited",
  "custom delimiters",
  "pipe embed",
  "rows",
  "tree",
]);
</script>

<template>
  <AdminFilterDropdown
    label="options"
    :show-filter-icon="false"
    :show-clear="false"
    :has-active-filters="hasCustomOptions"
    :active-label="optionsActiveLabel"
    :option-labels="optionLabels"
  >
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
  </AdminFilterDropdown>
</template>
