import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import type { TokenResponse, UserResponse } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref<string | null>(localStorage.getItem("access_token"));
  const refreshToken = ref<string | null>(
    localStorage.getItem("refresh_token"),
  );
  const user = ref<UserResponse | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value);

  function setTokens(tokens: TokenResponse): void {
    accessToken.value = tokens.access_token;
    refreshToken.value = tokens.refresh_token;
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
  }

  function logout(): void {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  async function login(email: string, password: string): Promise<void> {
    const { data } = await api.post<TokenResponse>("/auth/login", {
      email,
      password,
    });
    setTokens(data);
    await fetchUser();
  }

  async function fetchUser(): Promise<void> {
    if (!accessToken.value) return;
    try {
      const { data } = await api.get<UserResponse>("/auth/me");
      user.value = data;
    } catch {
      logout();
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    setTokens,
    logout,
    login,
    fetchUser,
  };
});
