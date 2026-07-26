<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";

const displayName = defineModel<string>("displayName", { required: true });
const timezone = defineModel<string>("timezone", { required: true });

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
        <CardTitle>profile</CardTitle>
      </CardHeader>
      <form class="space-y-4" @submit.prevent="emit('save')">
        <BaseInput
          v-model="displayName"
          name="display-name"
          autocomplete="name"
          placeholder="display name"
          aria-label="display name"
        />
        <BaseInput
          v-model="timezone"
          name="timezone"
          autocomplete="off"
          placeholder="timezone"
          aria-label="timezone"
          required
        />
        <BaseButton type="submit" variant="success" :loading="saving" :disabled="!canSave">
          {{ saving ? "saving..." : "save profile" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
