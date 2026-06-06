import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { syncGuestWeatherLocations } from "@/composables/useWeatherLocations";
import type { UserResponse } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserResponse | null>(null);
  const sessionResolved = ref(false);
  const sessionError = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  function clearUser(): void {
    user.value = null;
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

  async function fetchUser(): Promise<void> {
    const { data } = await api.get<UserResponse>("/auth/me");
    user.value = data;
    await syncGuestWeatherLocations();
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
        await api.post("/auth/refresh");
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
    fetchUser,
    resolveSession,
  };
});
