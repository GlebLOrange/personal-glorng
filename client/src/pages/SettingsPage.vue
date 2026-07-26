<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import SettingsCurrencySection from "@/components/settings/SettingsCurrencySection.vue";
import SettingsDeleteSection from "@/components/settings/SettingsDeleteSection.vue";
import SettingsEmailSection from "@/components/settings/SettingsEmailSection.vue";
import SettingsGithubSection from "@/components/settings/SettingsGithubSection.vue";
import SettingsPasswordSection from "@/components/settings/SettingsPasswordSection.vue";
import SettingsProfileSection from "@/components/settings/SettingsProfileSection.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { useUserPreferences } from "@/composables/useUserPreferences";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import type { GitHubStatus } from "@/types";
import { passwordStrength } from "@/utils/passwordPolicy";

const auth = useAuthStore();
const router = useRouter();
const { permissions } = usePermissions();
const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

const displayName = ref("");
const timezone = ref("UTC");
const newEmail = ref("");
const emailPassword = ref("");
const currentPassword = ref("");
const newPassword = ref("");
const newPasswordConfirm = ref("");
const deletePassword = ref("");
const deleteConfirm = ref(false);
const githubStatus = ref<GitHubStatus>({ linked: false, github_username: null });
const githubLoading = ref(false);
const githubError = ref<string | null>(null);
const { run: runProfile, loading: savingProfile } = useApiAction();
const { run: runEmail, loading: savingEmail } = useApiAction();
const { run: runPassword, loading: savingPassword } = useApiAction();
const { run: runPrefs, loading: savingPrefs } = useApiAction();
const { run: runUnlinkGithub, loading: unlinkingGithub } = useApiAction();
const { run: runDelete, loading: deleting } = useApiAction();

const passwordCheck = computed(() => passwordStrength(newPassword.value));
const profilePayload = computed(() => ({
  display_name: displayName.value.trim() || null,
  timezone: timezone.value.trim(),
}));
const isProfileUnchanged = computed(
  () =>
    profilePayload.value.display_name === (auth.user?.display_name ?? null) &&
    profilePayload.value.timezone === (auth.user?.timezone ?? "UTC"),
);
const canSaveProfile = computed(
  () => !!profilePayload.value.timezone && !isProfileUnchanged.value && !savingProfile.value,
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
const canSaveCurrency = computed(() => !!displayCurrency.value && !savingPrefs.value);
const canDeleteAccount = computed(
  () => !!deletePassword.value && deleteConfirm.value && !deleting.value,
);

function syncFormFromUser(): void {
  displayName.value = auth.user?.display_name ?? "";
  timezone.value = auth.user?.timezone ?? "UTC";
  newEmail.value = auth.user?.email ?? "";
}

async function loadGithubStatus(): Promise<void> {
  githubLoading.value = true;
  githubError.value = null;
  try {
    const { data } = await api.get<GitHubStatus>("/auth/github/status");
    githubStatus.value = data;
  } catch (err) {
    githubError.value = getApiErrorMessage(err, "Unable to load GitHub status");
  } finally {
    githubLoading.value = false;
  }
}

onMounted(async () => {
  syncFormFromUser();
  await Promise.all([loadPreferences(), loadGithubStatus()]);
});

async function saveProfile(): Promise<void> {
  if (!canSaveProfile.value) return;
  await runProfile(() => auth.updateProfile(profilePayload.value), {
    successMessage: "Profile updated",
    errorMessage: "Profile update failed",
  });
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

async function saveCurrency(): Promise<void> {
  if (!canSaveCurrency.value) return;
  await runPrefs(() => saveDisplayCurrency(displayCurrency.value), {
    successMessage: "Preferences saved",
    errorMessage: "Preferences update failed",
  });
}

function connectGithub(): void {
  window.location.href = "/api/auth/github/authorize";
}

async function unlinkGithub(): Promise<void> {
  const data = await runUnlinkGithub(
    async () => {
      const response = await api.delete<GitHubStatus>("/auth/github");
      return response.data;
    },
    {
      successMessage: "GitHub unlinked",
      errorMessage: "Failed to unlink GitHub",
    },
  );
  if (data) githubStatus.value = data;
}

async function deleteAccount(): Promise<void> {
  if (!canDeleteAccount.value) return;
  const ok = await runDelete(
    async () => {
      await auth.deleteAccount(deletePassword.value);
      return true;
    },
    {
      successMessage: "Account deleted",
      errorMessage: "Account deletion failed",
    },
  );
  if (ok) router.push("/");
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
    <div class="grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2">
      <SettingsProfileSection
        v-model:display-name="displayName"
        v-model:timezone="timezone"
        :saving="savingProfile"
        :can-save="canSaveProfile"
        @save="saveProfile"
      />

      <SettingsEmailSection
        v-model:new-email="newEmail"
        v-model:email-password="emailPassword"
        :saving="savingEmail"
        :can-save="canSaveEmail"
        @save="saveEmail"
      />

      <SettingsPasswordSection
        v-model:current-password="currentPassword"
        v-model:new-password="newPassword"
        v-model:new-password-confirm="newPasswordConfirm"
        :saving="savingPassword"
        :can-save="canSavePassword"
        @save="savePassword"
      />

      <SettingsCurrencySection
        v-model:display-currency="displayCurrency"
        :saving="savingPrefs"
        :can-save="canSaveCurrency"
        @save="saveCurrency"
      />

      <SettingsGithubSection
        :status="githubStatus"
        :loading="githubLoading"
        :error="githubError"
        :unlinking="unlinkingGithub"
        @connect="connectGithub"
        @unlink="unlinkGithub"
        @retry="loadGithubStatus"
      />

      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>permissions</CardTitle>
          </CardHeader>
          <div class="space-y-4">
            <div v-if="permissions.length" class="flex flex-wrap gap-2">
              <span
                v-for="perm in permissions"
                :key="perm"
                class="break-words rounded-full border border-surface-border px-2 py-1 text-xs text-surface-muted"
              >
                {{ perm }}
              </span>
            </div>
            <p v-else class="text-sm text-surface-mid">No tool permissions — contact an admin.</p>
          </div>
        </CardBody>
      </Card>

      <SettingsDeleteSection
        v-model:delete-password="deletePassword"
        v-model:delete-confirm="deleteConfirm"
        :deleting="deleting"
        :can-delete="canDeleteAccount"
        @delete="deleteAccount"
      />
    </div>
  </PageShell>
</template>
