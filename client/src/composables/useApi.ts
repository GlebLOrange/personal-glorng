import axios, { type AxiosRequestConfig } from "axios";

import { useAuthStore } from "@/stores/auth";
import type { TokenResponse } from "@/types";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const orig: AxiosRequestConfig & { _retry?: boolean } = error.config;
    if (error.response?.status !== 401 || orig._retry) {
      return Promise.reject(error);
    }

    const auth = useAuthStore();
    if (!auth.refreshToken) {
      auth.logout();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingQueue.push((token: string) => {
          orig.headers = { ...orig.headers, Authorization: `Bearer ${token}` };
          resolve(api(orig));
        });
      });
    }

    orig._retry = true;
    isRefreshing = true;
    try {
      const { data } = await axios.post<TokenResponse>("/api/auth/refresh", {
        refresh_token: auth.refreshToken,
      });
      auth.setTokens(data);
      pendingQueue.forEach((cb) => cb(data.access_token));
      orig.headers = {
        ...orig.headers,
        Authorization: `Bearer ${data.access_token}`,
      };
      return api(orig);
    } catch {
      auth.logout();
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
      pendingQueue = [];
    }
  },
);
