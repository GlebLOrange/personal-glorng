import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { clearCachedApi } from "@/composables/useCachedApi";
import { isApiError } from "@/types/api";
import type { UserPreferences, UserResponse } from "@/types";
import { tryRefreshSession } from "@/utils/authSession";

export interface UpdateProfilePayload {
  display_name?: string | null;
  timezone?: string;
}

/** ponytail: keep axios out of the App/NavBar import graph until a method runs */
async function getApi() {
  const { api } = await import("@/composables/useApi");
  return api;
}

function httpStatus(err: unknown): number | undefined {
  return isApiError(err) ? err.response?.status : undefined;
}

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserResponse | null>(null);
  const sessionResolved = ref(false);
  const sessionError = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  function clearUser(): void {
    user.value = null;
    clearCachedApi();
    // Platform catalog module imports axios + auth — load it only when clearing.
    void import("@/composables/usePlatformCatalog").then(({ clearPlatformCatalog }) =>
      clearPlatformCatalog(),
    );
  }

  function logout(): void {
    clearUser();
    sessionError.value = null;
    void getApi().then((api) => api.post("/auth/logout").catch(() => undefined));
  }

  async function login(email: string, password: string): Promise<void> {
    const api = await getApi();
    await api.post("/auth/login", {
      email,
      password,
    });
    await fetchUser();
  }

  async function loginWithGoogle(): Promise<void> {
    const { signInWithGooglePopup } = await import("@/services/firebase");
    const credential = await signInWithGooglePopup();
    const idToken = await credential.user.getIdToken();
    const api = await getApi();
    await api.post("/auth/firebase", {
      id_token: idToken,
    });
    await fetchUser();
  }

  async function fetchUser(): Promise<void> {
    const api = await getApi();
    const { data } = await api.get<UserResponse>("/auth/me");
    user.value = data;
    const { syncGuestWeatherLocations } = await import("@/composables/useWeatherLocations");
    await syncGuestWeatherLocations();
  }

  async function updateProfile(payload: UpdateProfilePayload): Promise<void> {
    const api = await getApi();
    const { data } = await api.patch<UserResponse>("/auth/me", payload);
    user.value = data;
  }

  async function changeEmail(email: string, currentPassword: string): Promise<void> {
    const api = await getApi();
    await api.patch("/auth/me/email", {
      email,
      current_password: currentPassword,
    });
    await fetchUser();
  }

  async function changePassword(
    currentPassword: string,
    newPassword: string,
    passwordConfirm: string,
  ): Promise<void> {
    const api = await getApi();
    await api.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
      password_confirm: passwordConfirm,
    });
  }

  async function fetchPreferences(): Promise<UserPreferences> {
    const api = await getApi();
    const { data } = await api.get<UserPreferences>("/auth/me/preferences");
    return data;
  }

  async function updatePreferences(
    preferences: Partial<UserPreferences>,
  ): Promise<UserPreferences> {
    const api = await getApi();
    const { data } = await api.patch<UserPreferences>("/auth/me/preferences", preferences);
    if (user.value) {
      user.value = {
        ...user.value,
        preferences: {
          ...user.value.preferences,
          ...data,
        },
      };
    }
    return data;
  }

  async function deleteAccount(currentPassword: string): Promise<void> {
    const api = await getApi();
    await api.delete("/auth/me", {
      data: {
        current_password: currentPassword,
        confirm: true,
      },
    });
    clearUser();
  }

  function isUnauthorizedError(err: unknown): boolean {
    return httpStatus(err) === 401;
  }

  let resolveInFlight: Promise<void> | null = null;

  async function runResolveSession(): Promise<void> {
    sessionResolved.value = false;
    sessionError.value = null;
    // Keep prior user until auth failure is confirmed (avoids bounce on network/5xx blips).

    try {
      try {
        await fetchUser();
      } catch (err) {
        if (httpStatus(err) !== 401) {
          throw err;
        }
        if (!(await tryRefreshSession())) {
          clearUser();
          return;
        }
        await fetchUser();
      }
    } catch (err) {
      if (isUnauthorizedError(err)) {
        clearUser();
        return;
      }
      sessionError.value =
        err instanceof Error && err.message
          ? err.message
          : "Unable to restore session";
      throw err;
    } finally {
      sessionResolved.value = true;
    }
  }

  /** Restore session from cookies; try refresh before treating user as logged out. */
  async function resolveSession(): Promise<void> {
    if (resolveInFlight) {
      return resolveInFlight;
    }
    resolveInFlight = runResolveSession().finally(() => {
      resolveInFlight = null;
    });
    return resolveInFlight;
  }

  return {
    user,
    sessionResolved,
    sessionError,
    isAuthenticated,
    clearUser,
    logout,
    login,
    loginWithGoogle,
    fetchUser,
    updateProfile,
    changeEmail,
    changePassword,
    fetchPreferences,
    updatePreferences,
    deleteAccount,
    resolveSession,
  };
});
