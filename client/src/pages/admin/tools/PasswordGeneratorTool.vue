<script setup lang="ts">
import { computed, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
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
  <div class="max-w-md mx-auto px-6 py-10">
    <h1 class="text-3xl font-bold accent-gradient mb-8">password generator</h1>
    <BaseCard>
      <form class="space-y-4" @submit.prevent="generatePassword">
        <BaseInput v-model.number="length" type="number" label="Length" />

        <fieldset class="space-y-2">
          <legend class="text-sm text-surface-mid mb-1">Character sets</legend>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="uppercase" type="checkbox" class="rounded" />
            Uppercase (A–Z)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="lowercase" type="checkbox" class="rounded" />
            Lowercase (a–z)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="digits" type="checkbox" class="rounded" />
            Numbers (0–9)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="symbols" type="checkbox" class="rounded" />
            Symbols (!@#$…)
          </label>
          <label class="flex items-center gap-2 text-sm text-surface-light">
            <input v-model="excludeAmbiguous" type="checkbox" class="rounded" />
            Exclude ambiguous (0, O, 1, l, I)
          </label>
        </fieldset>

        <BaseButton
          variant="primary"
          type="submit"
          class="w-full"
          :disabled="loading || !hasCharset"
        >
          {{ loading ? "Generating..." : "Generate" }}
        </BaseButton>
      </form>

      <div v-if="generated" class="mt-6 space-y-3">
        <div class="flex flex-wrap items-end gap-2">
          <div class="flex flex-col gap-1 flex-1 min-w-[12rem]">
            <label class="text-sm text-surface-mid">Password</label>
            <input
              :value="displayPassword"
              type="text"
              readonly
              class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm font-mono focus:outline-none"
            />
          </div>
          <BaseButton variant="ghost" size="sm" @click="showPassword = !showPassword">
            {{ showPassword ? "Hide" : "Show" }}
          </BaseButton>
          <BaseButton variant="ghost" size="sm" @click="copy(generated)">Copy</BaseButton>
        </div>
        <p class="text-xs" :class="strength.valid ? 'text-green-400' : 'text-surface-mid'">
          {{ strength.message }}
        </p>
      </div>
    </BaseCard>
  </div>
</template>
