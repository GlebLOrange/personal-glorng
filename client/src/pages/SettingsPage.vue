<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import SettingsAccountSection from "@/components/settings/SettingsAccountSection.vue";
import SettingsDeleteSection from "@/components/settings/SettingsDeleteSection.vue";
import SettingsGithubSection from "@/components/settings/SettingsGithubSection.vue";
import SettingsPreferencesSection from "@/components/settings/SettingsPreferencesSection.vue";
import SettingsProfileSection from "@/components/settings/SettingsProfileSection.vue";
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
const savedCurrency = ref(displayCurrency.value);
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
const profileDisplayName = computed(() => displayName.value.trim() || null);
const isProfileUnchanged = computed(
  () => profileDisplayName.value === (auth.user?.display_name ?? null),
);
const canSaveProfile = computed(() => !isProfileUnchanged.value && !savingProfile.value);
const isTimezoneUnchanged = computed(
  () => timezone.value.trim() === (auth.user?.timezone ?? "UTC"),
);
const isCurrencyUnchanged = computed(() => displayCurrency.value === savedCurrency.value);
const canSavePrefs = computed(
  () =>
    !!timezone.value.trim() &&
    (!isTimezoneUnchanged.value || !isCurrencyUnchanged.value) &&
    !savingPrefs.value,
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
  savedCurrency.value = displayCurrency.value;
});

async function saveProfile(): Promise<void> {
  if (!canSaveProfile.value) return;
  await runProfile(() => auth.updateProfile({ display_name: profileDisplayName.value }), {
    successMessage: "Profile updated",
    errorMessage: "Profile update failed",
  });
}

async function savePreferences(): Promise<void> {
  if (!canSavePrefs.value) return;
  await runPrefs(
    async () => {
      if (!isTimezoneUnchanged.value) {
        await auth.updateProfile({ timezone: timezone.value.trim() });
      }
      if (!isCurrencyUnchanged.value) {
        await saveDisplayCurrency(displayCurrency.value);
        savedCurrency.value = displayCurrency.value;
      }
      return true;
    },
    {
      successMessage: "Preferences saved",
      errorMessage: "Preferences update failed",
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
    <div class="grid min-w-0 grid-cols-1 gap-3 md:grid-cols-2">
      <SettingsProfileSection
        v-model:display-name="displayName"
        :saving="savingProfile"
        :can-save="canSaveProfile"
        @save="saveProfile"
      />

      <SettingsPreferencesSection
        v-model:timezone="timezone"
        v-model:display-currency="displayCurrency"
        :permissions="permissions"
        :saving="savingPrefs"
        :can-save="canSavePrefs"
        @save="savePreferences"
      />

      <SettingsAccountSection
        v-model:new-email="newEmail"
        v-model:email-password="emailPassword"
        v-model:current-password="currentPassword"
        v-model:new-password="newPassword"
        v-model:new-password-confirm="newPasswordConfirm"
        :saving-email="savingEmail"
        :can-save-email="canSaveEmail"
        :saving-password="savingPassword"
        :can-save-password="canSavePassword"
        @save-email="saveEmail"
        @save-password="savePassword"
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
