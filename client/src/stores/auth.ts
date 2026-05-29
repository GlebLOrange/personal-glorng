import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import type { UserResponse } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserResponse | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  function logout(): void {
    user.value = null;
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
    try {
      const { data } = await api.get<UserResponse>("/auth/me");
      user.value = data;
    } catch (err) {
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      if (status === 401 || status === 403) {
        logout();
      }
    }
  }

  return {
    user,
    isAuthenticated,
    logout,
    login,
    fetchUser,
  };
});
