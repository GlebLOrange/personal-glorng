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
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import type { GitHubStatus } from "@/types";
import { passwordStrength } from "@/utils/passwordPolicy";

const auth = useAuthStore();
const router = useRouter();
const { toast } = useNotify();
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
const unlinkingGithub = ref(false);
const savingProfile = ref(false);
const savingEmail = ref(false);
const savingPassword = ref(false);
const savingPrefs = ref(false);
const deleting = ref(false);

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
  savingProfile.value = true;
  try {
    await auth.updateProfile(profilePayload.value);
    toast("Profile updated", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Profile update failed"), "error");
  } finally {
    savingProfile.value = false;
  }
}

async function saveEmail(): Promise<void> {
  if (!canSaveEmail.value) return;
  savingEmail.value = true;
  try {
    await auth.changeEmail(newEmail.value.trim(), emailPassword.value);
    toast("Email updated — verify your new address", "success");
    emailPassword.value = "";
  } catch (err) {
    toast(getApiErrorMessage(err, "Email change failed"), "error");
  } finally {
    savingEmail.value = false;
  }
}

async function savePassword(): Promise<void> {
  if (!canSavePassword.value) return;
  savingPassword.value = true;
  try {
    await auth.changePassword(currentPassword.value, newPassword.value, newPasswordConfirm.value);
    currentPassword.value = "";
    newPassword.value = "";
    newPasswordConfirm.value = "";
    toast("Password changed", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Password change failed"), "error");
  } finally {
    savingPassword.value = false;
  }
}

async function saveCurrency(): Promise<void> {
  if (!canSaveCurrency.value) return;
  savingPrefs.value = true;
  try {
    await saveDisplayCurrency(displayCurrency.value);
    toast("Preferences saved", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Preferences update failed"), "error");
  } finally {
    savingPrefs.value = false;
  }
}

function connectGithub(): void {
  window.location.href = "/api/auth/github/authorize";
}

async function unlinkGithub(): Promise<void> {
  unlinkingGithub.value = true;
  try {
    const { data } = await api.delete<GitHubStatus>("/auth/github");
    githubStatus.value = data;
    toast("GitHub unlinked", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to unlink GitHub"), "error");
  } finally {
    unlinkingGithub.value = false;
  }
}

async function deleteAccount(): Promise<void> {
  if (!canDeleteAccount.value) return;
  deleting.value = true;
  try {
    await auth.deleteAccount(deletePassword.value);
    toast("Account deleted", "success");
    router.push("/");
  } catch (err) {
    toast(getApiErrorMessage(err, "Account deletion failed"), "error");
  } finally {
    deleting.value = false;
  }
}
</script>

<template>
  <PageShell
    title="settings"
    :breadcrumbs="[{ label: 'settings' }]"
    max-width="5xl"
    :narrow="false"
  >
    <div class="min-w-0 space-y-8">
      <section class="space-y-5">
        <h2 class="mb-3 text-sm font-medium text-surface-sage">Account</h2>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveProfile">
          <BaseInput
            v-model="displayName"
            name="display-name"
            autocomplete="name"
            label="Display name"
            placeholder="optional"
          />
          <BaseInput
            v-model="timezone"
            name="timezone"
            autocomplete="off"
            label="Timezone"
            placeholder="e.g. Europe/Warsaw"
            required
          />
          <BaseButton type="submit" variant="primary" :loading="savingProfile" :disabled="!canSaveProfile">
            {{ savingProfile ? "saving..." : "save profile" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Email</CardTitle>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveEmail">
          <BaseInput
            v-model="newEmail"
            type="email"
            name="email"
            autocomplete="email"
            label="Email address"
            placeholder="you@example.com"
            required
          />
          <BaseInput
            v-model="emailPassword"
            type="password"
            name="current-password-for-email"
            autocomplete="current-password"
            label="Current password"
            placeholder="••••••••"
            required
          />
          <BaseButton type="submit" variant="secondary" :loading="savingEmail" :disabled="!canSaveEmail">
            {{ savingEmail ? "saving..." : "change email" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Password</CardTitle>
          <template #actions>
            <RouterLink to="/forgot-password" class="text-sm text-accent-blue hover:underline">
              forgot password?
            </RouterLink>
          </template>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="savePassword">
          <BaseInput
            v-model="currentPassword"
            type="password"
            name="current-password"
            autocomplete="current-password"
            label="current password"
            placeholder="current password"
            required
          />
          <BaseInput
            v-model="newPassword"
            type="password"
            name="new-password"
            autocomplete="new-password"
            label="New password"
            placeholder="••••••••"
            :hint="newPassword && passwordCheck.valid ? passwordCheck.message : undefined"
            :error="newPassword && !passwordCheck.valid ? passwordCheck.message : undefined"
            required
          />
          <BaseInput
            v-model="newPasswordConfirm"
            type="password"
            name="confirm-new-password"
            autocomplete="new-password"
            label="Confirm new password"
            placeholder="••••••••"
            :error="newPasswordConfirm && !passwordsMatch ? 'Passwords do not match' : undefined"
            required
          />
          <BaseButton type="submit" variant="primary" :loading="savingPassword" :disabled="!canSavePassword">
            {{ savingPassword ? "saving..." : "change password" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>
      </section>

      <section class="space-y-5">
        <h2 class="mb-3 text-sm font-medium text-surface-sage">
          Preferences & connections
        </h2>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveCurrency">
          <BaseSelect v-model="displayCurrency" label="Expense display currency">
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </BaseSelect>
          <BaseButton type="submit" variant="secondary" :loading="savingPrefs" :disabled="!canSaveCurrency">
            {{ savingPrefs ? "saving..." : "save preferences" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Integrations</CardTitle>
        </CardHeader>
        <CardBody>
        <section class="space-y-4">
          <p v-if="githubError" class="text-sm text-status-warning">{{ githubError }}</p>
          <div class="flex flex-wrap items-center gap-3">
            <BaseButton
              v-if="!githubStatus.linked"
              variant="primary"
              :disabled="githubLoading"
              @click="connectGithub"
            >
              Connect GitHub
            </BaseButton>
            <template v-else>
              <p class="text-sm text-surface-mid">
                Connected as
                <span class="text-surface-light font-medium"
                  >@{{ githubStatus.github_username ?? "github" }}</span
                >
              </p>
              <BaseButton variant="secondary" :disabled="unlinkingGithub" @click="unlinkGithub">
                {{ unlinkingGithub ? "Unlinking..." : "Unlink GitHub" }}
              </BaseButton>
            </template>
            <BaseButton
              v-if="githubError"
              variant="ghost"
              :disabled="githubLoading"
              @click="loadGithubStatus"
            >
              Retry
            </BaseButton>
          </div>
        </section>
        </CardBody>
      </Card>
      </section>

      <section class="space-y-5">
        <h2 class="mb-3 text-xs uppercase tracking-wider text-surface-muted">Access</h2>

      <Card>
        <CardBody>
        <section class="space-y-4">
          <div v-if="permissions.length" class="flex flex-wrap gap-2">
            <span
              v-for="perm in permissions"
              :key="perm"
              class="break-words rounded-full border border-surface-border px-2 py-1 text-xs text-surface-muted"
            >
              {{ perm }}
            </span>
          </div>
          <p v-else class="text-sm text-surface-mid">
            No tool permissions — contact an admin.
          </p>
        </section>
        </CardBody>
      </Card>
      </section>

      <section class="mt-4 space-y-5">
        <h2 class="mb-3 text-sm font-medium text-status-error">Danger zone</h2>

      <Card tint="danger">
        <CardHeader>
          <h2 class="card-title text-status-error">Delete account</h2>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="deleteAccount">
          <BaseInput
            v-model="deletePassword"
            type="password"
            name="delete-current-password"
            autocomplete="current-password"
            label="Current password"
            placeholder="••••••••"
            required
          />
          <label class="flex items-start gap-2 text-xs text-surface-mid">
            <input v-model="deleteConfirm" type="checkbox" class="mt-0.5 accent-status-error" />
            <span>I understand this permanently deletes my account.</span>
          </label>
          <BaseButton type="submit" variant="secondary" :loading="deleting" :disabled="!canDeleteAccount">
            {{ deleting ? "deleting..." : "delete account" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>
      </section>
    </div>
  </PageShell>
</template>
