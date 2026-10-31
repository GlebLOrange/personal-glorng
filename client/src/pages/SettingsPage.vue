<script setup lang="ts">
import * as CookieConsent from "vanilla-cookieconsent";
import { computed, defineAsyncComponent, onMounted, ref } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import FilterIcon from "@/components/icons/FilterIcon.vue";
import PageShell from "@/components/layout/PageShell.vue";
import SettingsAccountSection from "@/components/settings/SettingsAccountSection.vue";
import SettingsPreferencesSection from "@/components/settings/SettingsPreferencesSection.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody } from "@/components/ui/card";
import { useUserPreferences } from "@/composables/useUserPreferences";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { PLATFORM_SERVICES } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import { passwordStrength } from "@/utils/passwordPolicy";

// ponytail: badge pulls axios — keep it out of the production entry graph
const DevApiStatusBadge = import.meta.env.DEV
  ? defineAsyncComponent(() => import("@/components/dev/DevApiStatusBadge.vue"))
  : null;

const auth = useAuthStore();
const { permissions, canAccess } = usePermissions();
const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

const accessibleTools = computed(() =>
  PLATFORM_SERVICES.filter(
    (service) => Boolean(service.adminRoute) && !service.external && canAccess(service.slug),
  ),
);

const displayName = ref("");
const timezone = ref("UTC");
const savedCurrency = ref(displayCurrency.value);
const newEmail = ref("");
const emailPassword = ref("");
const currentPassword = ref("");
const newPassword = ref("");
const newPasswordConfirm = ref("");
const { run: runProfile, loading: savingProfile } = useApiAction();
const { run: runEmail, loading: savingEmail } = useApiAction();
const { run: runPassword, loading: savingPassword } = useApiAction();

const passwordCheck = computed(() => passwordStrength(newPassword.value));
const profileDisplayName = computed(() => displayName.value.trim() || null);
const isNameUnchanged = computed(
  () => profileDisplayName.value === (auth.user?.display_name ?? null),
);
const isTimezoneUnchanged = computed(
  () => timezone.value.trim() === (auth.user?.timezone ?? "UTC"),
);
const isCurrencyUnchanged = computed(() => displayCurrency.value === savedCurrency.value);
const canSaveProfile = computed(
  () =>
    !!timezone.value.trim() &&
    (!isNameUnchanged.value || !isTimezoneUnchanged.value || !isCurrencyUnchanged.value) &&
    !savingProfile.value,
);
const isEmailUnchanged = computed(
  () => newEmail.value.trim().toLowerCase() === (auth.user?.email ?? "").toLowerCase(),
);
const isEmailValid = computed(() => /^[^\s@]+@[^\s@]+$/.test(newEmail.value.trim()));
const canSaveEmail = computed(
  () =>
    isEmailValid.value && !isEmailUnchanged.value && !!emailPassword.value && !savingEmail.value,
);
const passwordsMatch = computed(
  () => !!newPasswordConfirm.value && newPassword.value === newPasswordConfirm.value,
);
const canSavePassword = computed(
  () =>
    !!currentPassword.value &&
    passwordCheck.value.valid &&
    passwordsMatch.value &&
    !savingPassword.value,
);

function syncFormFromUser(): void {
  displayName.value = auth.user?.display_name ?? "";
  timezone.value = auth.user?.timezone ?? "UTC";
  newEmail.value = auth.user?.email ?? "";
}

function openCookiePreferences(): void {
  CookieConsent.showPreferences();
}

onMounted(async () => {
  syncFormFromUser();
  await loadPreferences();
  savedCurrency.value = displayCurrency.value;
});

async function saveProfile(): Promise<void> {
  if (!canSaveProfile.value) return;
  await runProfile(
    async () => {
      if (!isNameUnchanged.value || !isTimezoneUnchanged.value) {
        await auth.updateProfile({
          ...(!isNameUnchanged.value ? { display_name: profileDisplayName.value } : {}),
          ...(!isTimezoneUnchanged.value ? { timezone: timezone.value.trim() } : {}),
        });
      }
      if (!isCurrencyUnchanged.value) {
        await saveDisplayCurrency(displayCurrency.value);
        savedCurrency.value = displayCurrency.value;
      }
      return true;
    },
    {
      successMessage: "Profile updated",
      errorMessage: "Profile update failed",
    },
  );
}

async function saveEmail(): Promise<void> {
  if (!canSaveEmail.value) return;
  const ok = await runEmail(
    async () => {
      await auth.changeEmail(newEmail.value.trim(), emailPassword.value);
      return true;
    },
    {
      successMessage: "Email updated — verify your new address",
      errorMessage: "Email change failed",
    },
  );
  if (ok) emailPassword.value = "";
}

async function savePassword(): Promise<void> {
  if (!canSavePassword.value) return;
  const ok = await runPassword(
    async () => {
      await auth.changePassword(currentPassword.value, newPassword.value, newPasswordConfirm.value);
      return true;
    },
    {
      successMessage: "Password changed",
      errorMessage: "Password change failed",
    },
  );
  if (ok) {
    currentPassword.value = "";
    newPassword.value = "";
    newPasswordConfirm.value = "";
  }
}
</script>

<template>
  <PageShell
    title="settings"
    :breadcrumbs="[{ label: 'settings', to: '/settings' }]"
    back-to="/"
    max-width="5xl"
    :narrow="false"
  >
    <div class="flex min-w-0 flex-col gap-10">
      <div
        v-if="DevApiStatusBadge"
        class="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border pb-4"
      >
        <p class="text-xs text-surface-mid">development API</p>
        <component :is="DevApiStatusBadge" />
      </div>

      <section id="profile" class="scroll-mt-40 md:scroll-mt-44" aria-label="profile">
        <SettingsPreferencesSection
          v-model:display-name="displayName"
          v-model:timezone="timezone"
          v-model:display-currency="displayCurrency"
          :saving="savingProfile"
          :can-save="canSaveProfile"
          @save="saveProfile"
        />
      </section>

      <section id="account" class="scroll-mt-40 md:scroll-mt-44" aria-label="account">
        <SettingsAccountSection
          v-model:new-email="newEmail"
          v-model:email-password="emailPassword"
          v-model:current-password="currentPassword"
          v-model:new-password="newPassword"
          v-model:new-password-confirm="newPasswordConfirm"
          :permissions="permissions"
          :saving-email="savingEmail"
          :can-save-email="canSaveEmail"
          :saving-password="savingPassword"
          :can-save-password="canSavePassword"
          @save-email="saveEmail"
          @save-password="savePassword"
        />
      </section>

      <section id="privacy" class="scroll-mt-40 md:scroll-mt-44" aria-label="privacy">
        <Card variant="compact">
          <CardBody>
            <div class="flex flex-wrap items-center justify-between gap-3">
              <RouterLink to="/privacy" class="nav-link text-sm">privacy policy</RouterLink>
              <BaseButton
                type="button"
                variant="secondary"
                size="sm"
                :icon="false"
                class="gap-1.5"
                @click="openCookiePreferences"
              >
                <FilterIcon class-name="size-3.5 shrink-0" />
                cookie preferences
              </BaseButton>
            </div>
          </CardBody>
        </Card>
      </section>

      <details
        v-if="accessibleTools.length"
        class="group rounded-lg border border-surface-border bg-surface-card p-4"
      >
        <summary
          id="settings-tools-heading"
          class="flex cursor-pointer list-none items-center justify-between gap-2 rounded text-sm font-medium text-surface-light marker:content-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 [&::-webkit-details-marker]:hidden"
        >
          <span class="underline-offset-2 group-open:underline">tools you can open</span>
          <ChevronIcon class-name="size-3.5 text-surface-mid group-open:rotate-180" />
        </summary>
        <ul class="mt-3 flex flex-wrap gap-x-3 gap-y-2">
          <li v-for="tool in accessibleTools" :key="tool.slug">
            <RouterLink :to="tool.adminRoute" class="nav-link text-sm">
              {{ tool.name }}
            </RouterLink>
          </li>
        </ul>
      </details>
    </div>
  </PageShell>
</template>
