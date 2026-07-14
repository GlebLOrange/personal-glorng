<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { EXPENSE_CURRENCIES } from "@/composables/useExpenseFilters";
import { useUserPreferences } from "@/composables/useUserPreferences";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { PLATFORM_SERVICES } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import type { GitHubStatus } from "@/types";
import { passwordStrength } from "@/utils/passwordPolicy";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

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
const permissionSummary = computed(() => {
  if (permissions.value.includes(SUPERUSER_PERMISSION)) {
    return "Platform superuser: full access to admin tools and user management.";
  }

  const serviceNames = new Set<string>();
  for (const permission of permissions.value) {
    const [serviceSlug] = permission.split(":");
    const service = PLATFORM_SERVICES.find((item) => item.slug === serviceSlug);
    if (service) serviceNames.add(service.name);
  }

  if (serviceNames.size === 0) {
    return "No tool permissions assigned yet.";
  }

  return `Access to ${Array.from(serviceNames).join(", ")}.`;
});

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
    <header class="page-intro">
      <p class="text-sm text-surface-mid">
        Manage your profile, security, preferences, and connected accounts.
      </p>
    </header>

    <div class="min-w-0 space-y-8">
      <section class="space-y-5">
        <h2 class="mb-3 text-xs uppercase tracking-wider text-surface-muted">Account</h2>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Set how your name and local time appear across the app.</CardDescription>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveProfile">
          <BaseInput
            v-model="displayName"
            label="Display name"
            name="display-name"
            autocomplete="name"
            placeholder="How should we call you?"
          />
          <div class="space-y-1">
            <BaseInput
              v-model="timezone"
              label="Timezone"
              name="timezone"
              autocomplete="off"
              placeholder="Europe/Warsaw"
              aria-describedby="timezone-help"
              required
            />
            <p id="timezone-help" class="text-xs text-surface-muted">
              Use an IANA timezone such as Europe/Warsaw or America/New_York.
            </p>
          </div>
          <BaseButton type="submit" variant="primary" :disabled="!canSaveProfile">
            {{ savingProfile ? "Saving..." : "Save profile" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Email</CardTitle>
          <CardDescription>
            Signed in as
            <span class="text-surface-light">{{ auth.user?.email }}</span>
            <span v-if="auth.user?.is_verified" class="text-status-success"> · verified</span>
            <span v-else class="text-yellow-300"> · unverified</span>
          </CardDescription>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveEmail">
          <BaseInput
            v-model="newEmail"
            type="email"
            label="Email address"
            name="email"
            autocomplete="email"
            required
          />
          <div class="space-y-1">
            <BaseInput
              v-model="emailPassword"
              type="password"
              label="Current password"
              name="current-password-for-email"
              autocomplete="current-password"
              aria-describedby="email-help"
              required
            />
            <p id="email-help" class="text-xs text-surface-muted">
              Changing email requires your current password and may ask you to verify the new
              address.
            </p>
          </div>
          <BaseButton type="submit" variant="secondary" :disabled="!canSaveEmail">
            {{ savingEmail ? "Saving..." : "Change email" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Password</CardTitle>
          <CardDescription>Keep your account protected with a strong password.</CardDescription>
          <template #actions>
            <RouterLink to="/forgot-password" class="text-sm text-accent-blue hover:underline">
              Forgot password?
            </RouterLink>
          </template>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="savePassword">
          <BaseInput
            v-model="currentPassword"
            type="password"
            label="Current password"
            name="current-password"
            autocomplete="current-password"
            required
          />
          <div class="space-y-1">
            <BaseInput
              v-model="newPassword"
              type="password"
              label="New password"
              name="new-password"
              autocomplete="new-password"
              aria-describedby="password-help"
              required
            />
            <p
              id="password-help"
              class="text-xs"
              :class="passwordCheck.valid ? 'text-status-success' : 'text-surface-mid'"
            >
              {{ passwordCheck.message }}
            </p>
          </div>
          <div class="space-y-1">
            <BaseInput
              v-model="newPasswordConfirm"
              type="password"
              label="Confirm new password"
              name="confirm-new-password"
              autocomplete="new-password"
              aria-describedby="password-confirm-help"
              required
            />
            <p
              v-if="newPasswordConfirm && !passwordsMatch"
              id="password-confirm-help"
              class="text-xs text-yellow-300"
            >
              Passwords do not match yet.
            </p>
          </div>
          <BaseButton type="submit" variant="primary" :disabled="!canSavePassword">
            {{ savingPassword ? "Saving..." : "Change password" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>
      </section>

      <section class="space-y-5">
        <h2 class="mb-3 text-xs uppercase tracking-wider text-surface-muted">
          Preferences & connections
        </h2>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>Choose defaults that make tools feel local to you.</CardDescription>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="saveCurrency">
          <BaseSelect v-model="displayCurrency" label="Expense display currency">
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </BaseSelect>
          <BaseButton type="submit" variant="secondary" :disabled="!canSaveCurrency">
            {{ savingPrefs ? "Saving..." : "Save preferences" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Integrations</CardTitle>
          <CardDescription>Connect external accounts used by tools.</CardDescription>
        </CardHeader>
        <CardBody>
        <section class="space-y-4">
          <p v-if="githubLoading" class="text-sm text-surface-mid">Checking GitHub status...</p>
          <p v-else-if="githubError" class="text-sm text-yellow-300">{{ githubError }}</p>
          <p v-else-if="githubStatus.linked" class="text-sm text-surface-mid">
            GitHub linked as
            <span
              class="rounded border border-surface-border bg-surface-dark/60 px-2 py-0.5 font-medium text-surface-light"
            >
              {{ githubStatus.github_username }}
            </span>
          </p>
          <p v-else class="text-sm text-surface-mid">GitHub is not linked.</p>
          <div class="flex flex-wrap gap-3">
            <BaseButton
              v-if="!githubStatus.linked"
              variant="primary"
              :disabled="githubLoading"
              @click="connectGithub"
            >
              Connect GitHub
            </BaseButton>
            <BaseButton
              v-else
              variant="secondary"
              :disabled="unlinkingGithub"
              @click="unlinkGithub"
            >
              {{ unlinkingGithub ? "Unlinking..." : "Unlink GitHub" }}
            </BaseButton>
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
        <CardHeader>
          <CardTitle>Access</CardTitle>
          <CardDescription>
            Tool permissions are managed by an administrator. Contact them if you need access.
          </CardDescription>
        </CardHeader>
        <CardBody>
        <section class="space-y-4">
          <p class="text-sm text-surface-light">{{ permissionSummary }}</p>
          <div v-if="permissions.length" class="flex flex-wrap gap-2">
            <span
              v-for="perm in permissions"
              :key="perm"
              class="break-words rounded-full border border-surface-border px-2 py-1 text-xs text-surface-muted"
            >
              {{ perm }}
            </span>
          </div>
        </section>
        </CardBody>
      </Card>
      </section>

      <section class="mt-4 space-y-5">
        <h2 class="mb-3 text-xs uppercase tracking-wider text-status-error/80">Danger zone</h2>

      <Card tint="danger">
        <CardHeader>
          <h2 class="card-title text-status-error">Delete account</h2>
          <CardDescription>
            Account deletion is permanent. Your password and confirmation are required.
          </CardDescription>
        </CardHeader>
        <CardBody>
        <form class="space-y-4" @submit.prevent="deleteAccount">
          <BaseInput
            v-model="deletePassword"
            type="password"
            label="Current password"
            name="delete-current-password"
            autocomplete="current-password"
            required
          />
          <label class="flex items-start gap-2 text-xs text-surface-mid">
            <input v-model="deleteConfirm" type="checkbox" class="mt-0.5 accent-red-500" />
            <span>I understand this permanently deletes my account.</span>
          </label>
          <BaseButton type="submit" variant="secondary" :disabled="!canDeleteAccount">
            {{ deleting ? "Deleting..." : "Delete account" }}
          </BaseButton>
        </form>
        </CardBody>
      </Card>
      </section>
    </div>
  </PageShell>
</template>
