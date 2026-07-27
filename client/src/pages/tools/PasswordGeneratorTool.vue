<script setup lang="ts">
import { computed, ref } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { passwordStrength, PASSWORD_MIN_LENGTH } from "@/utils/passwordPolicy";

interface PasswordGeneratorResponse {
  password: string;
  length: number;
}

const OPTION_LABELS = [
  "uppercase",
  "lowercase",
  "numbers",
  "symbols",
  "exclude ambiguous (0, O, 1, l, I)",
] as const;

const length = ref(Math.max(16, PASSWORD_MIN_LENGTH));
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

const hasCustomOptions = computed(
  () =>
    !uppercase.value ||
    !lowercase.value ||
    !digits.value ||
    !symbols.value ||
    excludeAmbiguous.value,
);

const optionsActiveLabel = computed(() => {
  if (!hasCustomOptions.value) return undefined;
  const parts: string[] = [];
  if (uppercase.value) parts.push("uppercase");
  if (lowercase.value) parts.push("lowercase");
  if (digits.value) parts.push("numbers");
  if (symbols.value) parts.push("symbols");
  if (excludeAmbiguous.value) parts.push("exclude ambiguous");
  return parts.length ? parts.join(" · ") : "none";
});

const clampedLength = computed(() =>
  Math.min(128, Math.max(PASSWORD_MIN_LENGTH, Number(length.value) || PASSWORD_MIN_LENGTH)),
);

const strength = computed(() => passwordStrength(generated.value));

const displayPassword = computed(() => {
  if (!generated.value) return "";
  return showPassword.value ? generated.value : "•".repeat(generated.value.length);
});

async function generatePassword(): Promise<void> {
  if (!hasCharset.value) return;
  length.value = clampedLength.value;

  const result = await run(
    () =>
      api.post<PasswordGeneratorResponse>("/tools/password-generator", {
        length: clampedLength.value,
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
    <Card variant="ghost" class="mx-auto w-full max-w-md">
      <form class="space-y-3" @submit.prevent="generatePassword">
        <div class="flex min-w-0 items-end gap-2">
          <BaseInput
            v-model.number="length"
            type="number"
            :min="PASSWORD_MIN_LENGTH"
            :max="128"
            label="length"
            :placeholder="`${PASSWORD_MIN_LENGTH}–128`"
            class="w-28 shrink-0"
          />

          <AdminFilterDropdown
            label="options"
            bare
            match-trigger-width
            class="min-w-0 flex-1 [&_button]:w-full"
            :show-filter-icon="false"
            :show-clear="false"
            :has-active-filters="hasCustomOptions"
            :active-label="optionsActiveLabel"
            :option-labels="[...OPTION_LABELS]"
          >
            <div class="flex flex-col gap-2">
              <label
                class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid"
                title="uppercase (A-Z)"
              >
                <input v-model="uppercase" type="checkbox" class="accent-accent-blue" />
                uppercase
              </label>
              <label
                class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid"
                title="lowercase (a-z)"
              >
                <input v-model="lowercase" type="checkbox" class="accent-accent-blue" />
                lowercase
              </label>
              <label
                class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid"
                title="numbers (0-9)"
              >
                <input v-model="digits" type="checkbox" class="accent-accent-blue" />
                numbers
              </label>
              <label
                class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid"
                title="symbols (!@#$...)"
              >
                <input v-model="symbols" type="checkbox" class="accent-accent-blue" />
                symbols
              </label>
              <label class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid">
                <input v-model="excludeAmbiguous" type="checkbox" class="accent-accent-blue" />
                exclude ambiguous (0, O, 1, l, I)
              </label>
            </div>
          </AdminFilterDropdown>
        </div>

        <BaseButton
          variant="primary"
          type="submit"
          class="w-full"
          :disabled="loading || !hasCharset"
        >
          {{ loading ? "generating..." : "generate" }}
        </BaseButton>
      </form>

      <div v-if="generated" class="mt-4 space-y-2">
        <div class="flex flex-wrap items-end gap-2">
          <BaseInput
            :model-value="displayPassword"
            readonly
            label="password"
            placeholder="generated password"
            class="flex-1 min-w-[12rem] font-data"
          />
          <BaseButton variant="ghost" size="field" class="min-w-[4rem]" @click="showPassword = !showPassword">
            {{ showPassword ? "hide" : "show" }}
          </BaseButton>
          <IconCopyButton @click="copy(generated)" />
        </div>
        <p v-if="!strength.valid" class="text-xs text-surface-mid">
          {{ strength.message }}
        </p>
      </div>
    </Card>
  </PageShell>
</template>
