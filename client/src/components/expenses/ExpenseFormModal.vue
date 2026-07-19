<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { EXPENSE_CURRENCIES, type CurrencyCode } from "@/composables/useExpenseFilters";

defineProps<{
  open: boolean;
  loading: boolean;
  title: string;
  categoryOptions: string[];
}>();

const category = defineModel<string>("category", { required: true });
const toolName = defineModel<string>("toolName", { required: true });
const amount = defineModel<string>("amount", { required: true });
const currency = defineModel<CurrencyCode>("currency", { required: true });
const expenseDate = defineModel<string>("expenseDate", { required: true });
const notes = defineModel<string>("notes", { required: true });

const emit = defineEmits<{ submit: []; close: [] }>();
</script>

<template>
  <BaseModal v-if="open" :title="title" @close="emit('close')">
    <form class="space-y-4" @submit.prevent="emit('submit')">
      <BaseSelect v-model="category" label="category">
        <option value="">—</option>
        <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
      </BaseSelect>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <BaseInput
          v-model="toolName"
          label="product"
          placeholder="milk, dinner, shell..."
        />
        <BaseInput
          v-model="amount"
          type="number"
          step="0.01"
          min="0.01"
          label="price"
          placeholder="0.00"
        />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <BaseInput v-model="expenseDate" type="date" label="date" />
        <BaseSelect v-model="currency" label="currency">
          <option v-for="c in EXPENSE_CURRENCIES" :key="c" :value="c">{{ c }}</option>
        </BaseSelect>
      </div>

      <BaseTextarea
        v-model="notes"
        :rows="3"
        label="notes"
        placeholder="invoice ref, billing period..."
      />

      <div class="flex gap-3 pt-2">
        <BaseButton type="submit" variant="primary" :disabled="loading">
          {{ loading ? "saving..." : "save" }}
        </BaseButton>
        <BaseButton variant="ghost" type="button" @click="emit('close')">cancel</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
