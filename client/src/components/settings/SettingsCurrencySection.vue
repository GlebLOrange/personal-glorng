<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";

const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

defineProps<{
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();
</script>

<template>
  <Card>
    <CardBody>
      <CardHeader>
        <CardTitle>preferences</CardTitle>
      </CardHeader>
      <form class="space-y-4" @submit.prevent="emit('save')">
        <BaseSelect v-model="displayCurrency" aria-label="display currency">
          <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
            {{ code }}
          </option>
        </BaseSelect>
        <BaseButton type="submit" variant="success" :loading="saving" :disabled="!canSave">
          {{ saving ? "saving..." : "save preferences" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
