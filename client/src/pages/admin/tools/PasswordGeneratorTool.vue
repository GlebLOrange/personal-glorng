<script setup lang="ts">
import { computed, ref } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { passwordStrength } from "@/utils/passwordPolicy";

interface PasswordGeneratorResponse {
  password: string;
  length: number;
}

const length = ref(16);
const uppercase = ref(true);
const lowercase = ref(true);
const digits = ref(true);
const symbols = ref(true);
const excludeAmbiguous = ref(false);
const generated = ref("");
const showPassword = ref(false);

const { loading, run } = useApiAction();
const { copy } = useClipboard();

const hasCharset = computed(
  () => uppercase.value || lowercase.value || digits.value || symbols.value,
);

const strength = computed(() => passwordStrength(generated.value));

const displayPassword = computed(() => {
  if (!generated.value) return "";
  return showPassword.value ? generated.value : "•".repeat(generated.value.length);
});

async function generatePassword(): Promise<void> {
  if (!hasCharset.value) return;

  const result = await run(
    () =>
      api.post<PasswordGeneratorResponse>("/tools/password-generator", {
        length: length.value,
        uppercase: uppercase.value,
        lowercase: lowercase.value,
        digits: digits.value,
        symbols: symbols.value,
        exclude_ambiguous: excludeAmbiguous.value,
      }),
    { errorFallback: "Failed to generate password" },
  );

  if (result) {
    generated.value = result.data.password;
    showPassword.value = false;
  }
}
</script>

<template>
  <PageShell
    title="password generator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'password generator' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <Card>
      <form class="space-y-4" @submit.prevent="generatePassword">
        <BaseInput
          v-model.number="length"
          type="number"
          placeholder="length (8–128)"
          aria-label="length (8–128)"
        />

        <fieldset class="space-y-2">
          <legend class="text-sm text-surface-mid mb-1">character sets</legend>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="uppercase" type="checkbox" class="rounded" />
            uppercase (A–Z)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="lowercase" type="checkbox" class="rounded" />
            lowercase (a–z)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="digits" type="checkbox" class="rounded" />
            numbers (0–9)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="symbols" type="checkbox" class="rounded" />
            symbols (!@#$…)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="excludeAmbiguous" type="checkbox" class="rounded" />
            exclude ambiguous (0, O, 1, l, I)
          </label>
        </fieldset>

        <BaseButton
          variant="primary"
          type="submit"
          class="w-full"
          :disabled="loading || !hasCharset"
        >
          {{ loading ? "generating..." : "generate" }}
        </BaseButton>
      </form>

      <div v-if="generated" class="mt-6 space-y-3">
        <div class="flex flex-wrap items-end gap-2">
          <BaseInput
            :model-value="displayPassword"
            readonly
            placeholder="password"
            aria-label="password"
            class="flex-1 min-w-[12rem] font-mono"
          />
          <BaseButton variant="ghost" size="sm" @click="showPassword = !showPassword">
            {{ showPassword ? "hide" : "show" }}
          </BaseButton>
          <BaseButton variant="ghost" size="sm" @click="copy(generated)">copy</BaseButton>
        </div>
        <p class="text-xs" :class="strength.valid ? 'text-status-success' : 'text-surface-mid'">
          {{ strength.message }}
        </p>
      </div>
    </Card>
  </PageShell>
</template>
