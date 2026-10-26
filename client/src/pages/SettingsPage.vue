<script setup lang="ts">
import * as CookieConsent from "vanilla-cookieconsent";
import { computed, defineAsyncComponent, onMounted, onUnmounted, ref } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
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

type SettingsSectionId = "profile" | "account" | "privacy";

interface SettingsNavItem {
  id: SettingsSectionId;
  label: string;
}

const auth = useAuthStore();
const { permissions, canAccess } = usePermissions();
const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

const navItems = computed((): SettingsNavItem[] => [
  { id: "profile", label: "profile" },
  { id: "account", label: "account" },
  { id: "privacy", label: "privacy" },
]);

const activeSection = ref<SettingsSectionId>("profile");
let sectionObserver: IntersectionObserver | null = null;

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

function navClass(id: SettingsSectionId): string {
  const base =
    "shrink-0 rounded-md px-3 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50";
  if (activeSection.value === id) {
    return `${base} bg-surface-card text-accent-coral`;
  }
  return `${base} text-surface-mid hover:text-surface-light`;
}

function observeSections(): void {
  sectionObserver?.disconnect();
  const ids = navItems.value.map((item) => item.id);
  const elements = ids
    .map((id) => document.getElementById(id))
    .filter((el): el is HTMLElement => el !== null);
  if (!elements.length) return;

  sectionObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      const top = visible[0]?.target.id as SettingsSectionId | undefined;
      if (top) activeSection.value = top;
    },
    {
      // Match sticky chip row + fixed site nav so the active link tracks the heading in view.
      rootMargin: "-28% 0px -55% 0px",
      threshold: [0.1, 0.35, 0.6],
    },
  );
  for (const el of elements) sectionObserver.observe(el);
}

onMounted(async () => {
  syncFormFromUser();
  await loadPreferences();
  savedCurrency.value = displayCurrency.value;
  const hash = window.location.hash.replace(/^#/, "") as SettingsSectionId;
  if (navItems.value.some((item) => item.id === hash)) {
    activeSection.value = hash;
  }
  observeSections();
});

onUnmounted(() => {
  sectionObserver?.disconnect();
  sectionObserver = null;
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
    <div class="flex min-w-0 flex-col gap-6 md:flex-row md:items-start md:gap-8">
      <nav
        aria-label="Settings sections"
        class="sticky top-20 z-10 -mx-1 overflow-x-auto bg-surface-dark/90 px-1 py-2 backdrop-blur-md md:top-24 md:w-44 md:shrink-0 md:overflow-visible md:bg-transparent md:px-0 md:py-0 md:backdrop-blur-none"
      >
        <ul class="flex gap-1 md:flex-col">
          <li v-for="item in navItems" :key="item.id">
            <a :href="`#${item.id}`" :class="navClass(item.id)">{{ item.label }}</a>
          </li>
        </ul>
      </nav>

      <div class="flex min-w-0 flex-1 flex-col gap-10">
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
                <BaseButton type="button" variant="secondary" size="sm" @click="openCookiePreferences">
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
    </div>
  </PageShell>
</template>
