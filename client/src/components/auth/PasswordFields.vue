<script setup lang="ts">
import { computed, useId } from "vue";

import BaseInput from "@/components/ui/BaseInput.vue";
import { passwordStrength } from "@/utils/passwordPolicy";

const password = defineModel<string>("password", { required: true });
const passwordConfirm = defineModel<string>("passwordConfirm", { required: true });

const props = withDefaults(
  defineProps<{
    passwordLabel?: string;
    passwordPlaceholder?: string;
    strengthId?: string;
  }>(),
  {
    passwordLabel: "password",
    passwordPlaceholder: "password",
  },
);

const fallbackId = useId();
const describedById = computed(() => props.strengthId ?? `password-strength-${fallbackId}`);

const strength = computed(() => passwordStrength(password.value));
const passwordsMatch = computed(
  () => !!passwordConfirm.value && password.value === passwordConfirm.value,
);
const valid = computed(() => strength.value.valid && passwordsMatch.value);

defineExpose({ strength, passwordsMatch, valid });
</script>

<template>
  <BaseInput
    v-model="password"
    type="password"
    name="password"
    autocomplete="new-password"
    :label="passwordLabel"
    :placeholder="passwordPlaceholder"
    :aria-describedby="describedById"
    required
  />
  <p
    :id="describedById"
    class="text-xs"
    :class="strength.valid ? 'text-status-success' : 'text-surface-mid'"
  >
    {{ strength.message }}
  </p>
  <BaseInput
    v-model="passwordConfirm"
    type="password"
    name="password-confirm"
    autocomplete="new-password"
    label="confirm password"
    placeholder="confirm password"
    :error="passwordConfirm && !passwordsMatch ? 'Passwords do not match' : undefined"
    required
  />
</template>
