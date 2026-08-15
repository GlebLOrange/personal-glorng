<script setup lang="ts">
import { computed, ref } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { familyBadgeClass } from "@/constants/httpStatusColors";
import { passwordStrength, PASSWORD_MIN_LENGTH } from "@/utils/passwordPolicy";

interface PasswordGeneratorResponse {
  password: string;
  length: number;
}

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

function clearOptions(): void {
  uppercase.value = true;
  lowercase.value = true;
  digits.value = true;
  symbols.value = true;
  excludeAmbiguous.value = false;
}

function resetState(): void {
  clearOptions();
  generated.value = "";
  showPassword.value = false;
}

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
          <!-- Swapped positions: ToolbarPillButton (AdminFilterDropdown) first -->
          <AdminFilterDropdown
            label="options"
            class="shrink-0"
            :match-trigger-width="false"
            :has-active-filters="hasCustomOptions"
            :active-label="optionsActiveLabel"
            @clear="resetState"
          >
            <template #chips>
              <AdminFilterChip
                label="uppercase"
                title="uppercase (A-Z)"
                :active="uppercase"
                :color-class="familyBadgeClass('1xx')"
                @click="uppercase = !uppercase"
              />
              <AdminFilterChip
                label="lowercase"
                title="lowercase (a-z)"
                :active="lowercase"
                :color-class="familyBadgeClass('1xx')"
                @click="lowercase = !lowercase"
              />
              <AdminFilterChip
                label="numbers"
                title="numbers (0-9)"
                :active="digits"
                :color-class="familyBadgeClass('1xx')"
                @click="digits = !digits"
              />
              <AdminFilterChip
                label="symbols"
                title="symbols (!@#$…)"
                :active="symbols"
                :color-class="familyBadgeClass('1xx')"
                @click="symbols = !symbols"
              />
              <AdminFilterChip
                label="exclude ambiguous"
                title="exclude ambiguous (0, O, 1, l, I)"
                :active="excludeAmbiguous"
                :color-class="familyBadgeClass('3xx')"
                @click="excludeAmbiguous = !excludeAmbiguous"
              />
            </template>
          </AdminFilterDropdown>

          <!-- Swapped positions: BaseInput second -->
          <BaseInput
            v-model.number="length"
            type="number"
            :min="PASSWORD_MIN_LENGTH"
            :max="128"
            label="length"
            :placeholder="`${PASSWORD_MIN_LENGTH}–128`"
            class="w-28 shrink-0"
          />
        </div>

        <div class="flex items-center gap-2">
          <BaseButton
            variant="primary"
            type="submit"
            class="w-auto flex-1"
            :disabled="loading || !hasCharset"
          >
            {{ loading ? "generating…" : "generate" }}
          </BaseButton>

          <IconActionButton
            family="1xx"
            :aria-label="'reset options and clear generated password'"
            title="reset state & clear password"
            @click="resetState"
          >
            <RefreshIcon class-name="size-4" />
          </IconActionButton>
        </div>
      </form>

      <div v-if="generated" class="mt-4 space-y-2">
        <div class="flex min-w-0 items-end gap-2">
          <BaseInput
            :model-value="displayPassword"
            readonly
            label="password"
            placeholder="generated password"
            class="min-w-0 flex-1 font-data"
          />
          <div class="flex shrink-0 items-end gap-2">
            <BaseButton variant="ghost" size="field" @click="showPassword = !showPassword">
              <span class="inline-grid justify-items-center">
                <span class="invisible col-start-1 row-start-1" aria-hidden="true">show</span>
                <span class="invisible col-start-1 row-start-1" aria-hidden="true">hide</span>
                <span class="col-start-1 row-start-1">{{ showPassword ? "hide" : "show" }}</span>
              </span>
            </BaseButton>
            <IconCopyButton @click="copy(generated)" />
          </div>
        </div>
        <p v-if="!strength.valid" class="text-xs text-surface-mid">
          {{ strength.message }}
        </p>
      </div>
    </Card>
  </PageShell>
</template>
