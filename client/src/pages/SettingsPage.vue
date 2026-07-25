<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { EXPENSE_CURRENCIES } from "@/composables/useExpenseFilters";
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
      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>profile</CardTitle>
          </CardHeader>
          <form class="space-y-4" @submit.prevent="saveProfile">
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
            <BaseButton
              type="submit"
              variant="success"
              :loading="savingProfile"
              :disabled="!canSaveProfile"
            >
              {{ savingProfile ? "saving..." : "save profile" }}
            </BaseButton>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>email</CardTitle>
          </CardHeader>
          <form class="space-y-4" @submit.prevent="saveEmail">
            <BaseInput
              v-model="newEmail"
              type="email"
              name="email"
              autocomplete="email"
              placeholder="email address"
              aria-label="email address"
              required
            />
            <BaseInput
              v-model="emailPassword"
              type="password"
              name="current-password-for-email"
              autocomplete="current-password"
              placeholder="current password"
              aria-label="current password"
              required
            />
            <BaseButton
              type="submit"
              variant="success"
              :loading="savingEmail"
              :disabled="!canSaveEmail"
            >
              {{ savingEmail ? "saving..." : "change email" }}
            </BaseButton>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>password</CardTitle>
          </CardHeader>
          <form class="space-y-4" @submit.prevent="savePassword">
            <div class="flex justify-end">
              <RouterLink
                to="/forgot-password"
                class="text-sm text-accent-blue hover:underline focus:underline"
              >
                forgot password?
              </RouterLink>
            </div>
            <BaseInput
              v-model="currentPassword"
              type="password"
              name="current-password"
              autocomplete="current-password"
              placeholder="current password"
              aria-label="current password"
              required
            />
            <BaseInput
              v-model="newPassword"
              type="password"
              name="new-password"
              autocomplete="new-password"
              placeholder="new password"
              aria-label="new password"
              :error="newPassword && !passwordCheck.valid ? passwordCheck.message : undefined"
              required
            />
            <BaseInput
              v-model="newPasswordConfirm"
              type="password"
              name="confirm-new-password"
              autocomplete="new-password"
              placeholder="confirm new password"
              aria-label="confirm new password"
              :error="newPasswordConfirm && !passwordsMatch ? 'Passwords do not match' : undefined"
              required
            />
            <BaseButton
              type="submit"
              variant="success"
              :loading="savingPassword"
              :disabled="!canSavePassword"
            >
              {{ savingPassword ? "saving..." : "change password" }}
            </BaseButton>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>preferences</CardTitle>
          </CardHeader>
          <form class="space-y-4" @submit.prevent="saveCurrency">
            <BaseSelect v-model="displayCurrency" aria-label="display currency">
              <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
                {{ code }}
              </option>
            </BaseSelect>
            <BaseButton
              type="submit"
              variant="success"
              :loading="savingPrefs"
              :disabled="!canSaveCurrency"
            >
              {{ savingPrefs ? "saving..." : "save preferences" }}
            </BaseButton>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <CardHeader>
            <CardTitle>github</CardTitle>
          </CardHeader>
          <div class="space-y-4">
            <p v-if="githubError" class="text-sm text-status-warning">{{ githubError }}</p>
            <div class="flex flex-wrap items-center gap-3">
              <BaseButton
                v-if="!githubStatus.linked"
                variant="primary"
                :disabled="githubLoading"
                @click="connectGithub"
              >
                connect github
              </BaseButton>
              <template v-else>
                <p class="text-sm text-surface-mid">
                  Connected as
                  <span class="text-surface-light font-medium"
                    >@{{ githubStatus.github_username ?? "github" }}</span
                  >
                </p>
                <BaseButton variant="secondary" :disabled="unlinkingGithub" @click="unlinkGithub">
                  {{ unlinkingGithub ? "unlinking..." : "unlink github" }}
                </BaseButton>
              </template>
              <BaseButton
                v-if="githubError"
                variant="ghost"
                :disabled="githubLoading"
                @click="loadGithubStatus"
              >
                retry
              </BaseButton>
            </div>
          </div>
        </CardBody>
      </Card>

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

      <Card tint="danger">
        <CardBody>
          <CardHeader>
            <CardTitle>delete account</CardTitle>
          </CardHeader>
          <form class="space-y-4" @submit.prevent="deleteAccount">
            <BaseInput
              v-model="deletePassword"
              type="password"
              name="delete-current-password"
              autocomplete="current-password"
              placeholder="current password"
              aria-label="current password"
              required
            />
            <label class="flex min-h-11 cursor-pointer items-start gap-3 text-xs text-surface-mid">
              <input v-model="deleteConfirm" type="checkbox" class="mt-1 accent-status-error" />
              <span>I understand this permanently deletes my account.</span>
            </label>
            <BaseButton
              type="submit"
              variant="secondary"
              danger
              :loading="deleting"
              :disabled="!canDeleteAccount"
            >
              {{ deleting ? "deleting..." : "delete account" }}
            </BaseButton>
          </form>
        </CardBody>
      </Card>
    </div>
  </PageShell>
</template>
