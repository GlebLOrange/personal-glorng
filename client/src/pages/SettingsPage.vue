<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
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
const savingProfile = ref(false);
const savingEmail = ref(false);
const savingPassword = ref(false);
const savingPrefs = ref(false);
const deleting = ref(false);

const passwordCheck = computed(() => passwordStrength(newPassword.value));

function syncFormFromUser(): void {
  displayName.value = auth.user?.display_name ?? "";
  timezone.value = auth.user?.timezone ?? "UTC";
  newEmail.value = auth.user?.email ?? "";
}

async function loadGithubStatus(): Promise<void> {
  try {
    const { data } = await api.get<GitHubStatus>("/auth/github/status");
    githubStatus.value = data;
  } catch {
    githubStatus.value = { linked: false, github_username: null };
  }
}

onMounted(async () => {
  syncFormFromUser();
  await Promise.all([loadPreferences(), loadGithubStatus()]);
});

async function saveProfile(): Promise<void> {
  savingProfile.value = true;
  try {
    await auth.updateProfile({
      display_name: displayName.value.trim() || null,
      timezone: timezone.value.trim(),
    });
    toast("Profile updated", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Profile update failed"), "error");
  } finally {
    savingProfile.value = false;
  }
}

async function saveEmail(): Promise<void> {
  savingEmail.value = true;
  try {
    await auth.changeEmail(newEmail.value, emailPassword.value);
    toast("Email updated — verify your new address", "success");
    emailPassword.value = "";
  } catch (err) {
    toast(getApiErrorMessage(err, "Email change failed"), "error");
  } finally {
    savingEmail.value = false;
  }
}

async function savePassword(): Promise<void> {
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
  try {
    const { data } = await api.delete<GitHubStatus>("/auth/github");
    githubStatus.value = data;
    toast("GitHub unlinked", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to unlink GitHub"), "error");
  }
}

async function deleteAccount(): Promise<void> {
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
  <AdminPageLayout title="settings" max-width="md">
    <div class="space-y-10">
      <section class="space-y-4">
        <h2 class="text-lg font-bold text-surface-light">Profile</h2>
        <BaseInput v-model="displayName" label="Display name" />
        <BaseInput v-model="timezone" label="Timezone" placeholder="Europe/Warsaw" />
        <BaseButton variant="primary" :disabled="savingProfile" @click="saveProfile">
          {{ savingProfile ? "Saving..." : "Save profile" }}
        </BaseButton>
      </section>

      <section class="space-y-4">
        <h2 class="text-lg font-bold text-surface-light">Security</h2>
        <p class="text-xs text-surface-mid">
          Signed in as {{ auth.user?.email }}.
          <RouterLink to="/forgot-password" class="text-accent-blue hover:underline">
            Forgot password?
          </RouterLink>
        </p>
        <BaseInput v-model="newEmail" type="email" label="Email" />
        <BaseInput
          v-model="emailPassword"
          type="password"
          label="Current password (required to change email)"
        />
        <BaseButton variant="secondary" :disabled="savingEmail" @click="saveEmail">
          {{ savingEmail ? "Saving..." : "Change email" }}
        </BaseButton>

        <BaseInput v-model="currentPassword" type="password" label="Current password" />
        <BaseInput v-model="newPassword" type="password" label="New password" />
        <p class="text-xs" :class="passwordCheck.valid ? 'text-green-400' : 'text-surface-mid'">
          {{ passwordCheck.message }}
        </p>
        <BaseInput v-model="newPasswordConfirm" type="password" label="Confirm new password" />
        <BaseButton
          variant="primary"
          :disabled="savingPassword || !passwordCheck.valid"
          @click="savePassword"
        >
          {{ savingPassword ? "Saving..." : "Change password" }}
        </BaseButton>
      </section>

      <section class="space-y-4">
        <h2 class="text-lg font-bold text-surface-light">Preferences</h2>
        <label class="block text-sm text-surface-mid">
          Expense display currency
          <select
            v-model="displayCurrency"
            class="mt-1 w-full rounded border border-surface-border bg-surface-dark px-3 py-2 text-surface-light"
          >
            <option v-for="code in EXPENSE_CURRENCIES" :key="code" :value="code">
              {{ code }}
            </option>
          </select>
        </label>
        <BaseButton variant="secondary" :disabled="savingPrefs" @click="saveCurrency">
          {{ savingPrefs ? "Saving..." : "Save preferences" }}
        </BaseButton>
      </section>

      <section class="space-y-4">
        <h2 class="text-lg font-bold text-surface-light">Integrations</h2>
        <p v-if="githubStatus.linked" class="text-sm text-surface-mid">
          GitHub linked as <strong class="text-surface-light">{{ githubStatus.github_username }}</strong>
        </p>
        <p v-else class="text-sm text-surface-mid">GitHub is not linked.</p>
        <div class="flex gap-3">
          <BaseButton v-if="!githubStatus.linked" variant="primary" @click="connectGithub">
            Connect GitHub
          </BaseButton>
          <BaseButton v-else variant="secondary" @click="unlinkGithub">Unlink GitHub</BaseButton>
        </div>
      </section>

      <section class="space-y-4">
        <h2 class="text-lg font-bold text-surface-light">Access</h2>
        <p class="text-sm text-surface-mid">
          Tool permissions are managed by an administrator. Contact them if you need access.
        </p>
        <ul v-if="permissions.length" class="text-xs text-surface-muted space-y-1">
          <li v-for="perm in permissions" :key="perm">{{ perm }}</li>
        </ul>
        <p v-else class="text-xs text-surface-muted">No tool permissions assigned yet.</p>
      </section>

      <section class="space-y-4 border-t border-surface-border pt-8">
        <h2 class="text-lg font-bold text-red-400">Delete account</h2>
        <BaseInput v-model="deletePassword" type="password" label="Current password" />
        <label class="flex items-center gap-2 text-xs text-surface-mid">
          <input v-model="deleteConfirm" type="checkbox" />
          I understand this permanently deletes my account
        </label>
        <BaseButton
          variant="secondary"
          :disabled="deleting || !deleteConfirm"
          @click="deleteAccount"
        >
          {{ deleting ? "Deleting..." : "Delete account" }}
        </BaseButton>
      </section>
    </div>
  </AdminPageLayout>
</template>
