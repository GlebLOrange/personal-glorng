import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { clearCachedApi } from "@/composables/useCachedApi";
import { syncGuestWeatherLocations } from "@/composables/useWeatherLocations";
import { tryRefreshSession } from "@/utils/authSession";
import type { UserPreferences, UserResponse } from "@/types";

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  display_name?: string;
  timezone?: string;
  accept_terms: boolean;
}

export interface UpdateProfilePayload {
  display_name?: string | null;
  timezone?: string;
}

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserResponse | null>(null);
  const sessionResolved = ref(false);
  const sessionError = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  function clearUser(): void {
    user.value = null;
    clearCachedApi();
  }

  function logout(): void {
    clearUser();
    sessionError.value = null;
    void api.post("/auth/logout").catch(() => undefined);
  }

  async function login(email: string, password: string): Promise<void> {
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
    await api.post("/auth/firebase", {
      id_token: idToken,
    });
    await fetchUser();
  }

  async function register(payload: RegisterPayload): Promise<void> {
    await api.post("/auth/register", payload);
  }

  async function fetchUser(): Promise<void> {
    const { data } = await api.get<UserResponse>("/auth/me");
    user.value = data;
    await syncGuestWeatherLocations();
  }

  async function updateProfile(payload: UpdateProfilePayload): Promise<void> {
    const { data } = await api.patch<UserResponse>("/auth/me", payload);
    user.value = data;
  }

  async function changeEmail(email: string, currentPassword: string): Promise<void> {
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
    await api.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
      password_confirm: passwordConfirm,
    });
  }

  async function fetchPreferences(): Promise<UserPreferences> {
    const { data } = await api.get<UserPreferences>("/auth/me/preferences");
    return data;
  }

  async function updatePreferences(
    preferences: Partial<UserPreferences>,
  ): Promise<UserPreferences> {
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
    await api.delete("/auth/me", {
      data: {
        current_password: currentPassword,
        confirm: true,
      },
    });
    clearUser();
  }

  function isUnauthorizedError(err: unknown): boolean {
    return axios.isAxiosError(err) && err.response?.status === 401;
  }

  /** Restore session from cookies; try refresh before treating user as logged out. */
  async function resolveSession(): Promise<void> {
    sessionResolved.value = false;
    sessionError.value = null;
    clearUser();

    try {
      try {
        await fetchUser();
      } catch (err) {
        const status = axios.isAxiosError(err) ? err.response?.status : undefined;
        if (status !== 401) {
          throw err;
        }
        if (!(await tryRefreshSession())) {
          return;
        }
        await fetchUser();
      }
    } catch (err) {
      if (isUnauthorizedError(err)) {
        clearUser();
        return;
      }
      sessionError.value = axios.isAxiosError(err)
        ? err.message || "Unable to restore session"
        : "Unable to restore session";
      throw err;
    } finally {
      sessionResolved.value = true;
    }
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
    register,
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
