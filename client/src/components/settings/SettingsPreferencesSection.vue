<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";

const timezone = defineModel<string>("timezone", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

defineProps<{
  permissions: string[];
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <CardHeader class="!mb-2">
        <CardTitle>preferences</CardTitle>
      </CardHeader>
      <form class="space-y-2" @submit.prevent="emit('save')">
        <BaseInput
          v-model="timezone"
          name="timezone"
          autocomplete="off"
          placeholder="timezone"
          aria-label="timezone"
          required
        />
        <div class="flex flex-wrap items-end gap-2">
          <BaseSelect
            v-model="displayCurrency"
            compact
            aria-label="display currency"
            class="w-auto min-w-[5.5rem] max-w-[7.5rem]"
          >
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </BaseSelect>
          <BaseButton type="submit" variant="success" size="sm" :loading="saving" :disabled="!canSave">
            {{ saving ? "saving…" : "save" }}
          </BaseButton>
        </div>
        <div>
          <p class="mb-1.5 text-xs text-surface-mid">permissions</p>
          <div v-if="permissions.length" class="flex flex-wrap gap-1.5">
            <span
              v-for="perm in permissions"
              :key="perm"
              class="break-words rounded-full border border-surface-border px-2 py-0.5 text-xs text-surface-muted"
            >
              {{ perm }}
            </span>
          </div>
          <p v-else class="text-xs text-surface-mid">No tool permissions — contact an admin.</p>
        </div>
      </form>
    </CardBody>
  </Card>
</template>
