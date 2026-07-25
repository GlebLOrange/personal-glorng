import axios, { type AxiosRequestConfig } from "axios";

import { tryRefreshSession } from "@/utils/authSession";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

let isRefreshing = false;
type QueueEntry = {
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
  config: AxiosRequestConfig & { _retry?: boolean };
};
let pendingQueue: QueueEntry[] = [];

function isAuthRefreshRequest(url: string | undefined): boolean {
  return typeof url === "string" && url.includes("/auth/refresh");
}

function flushQueue(error: unknown | null): void {
  const queue = pendingQueue;
  pendingQueue = [];
  for (const entry of queue) {
    if (error) {
      entry.reject(error);
      continue;
    }
    entry.config._retry = true;
    entry.resolve(api(entry.config));
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const orig: AxiosRequestConfig & { _retry?: boolean } | undefined = error.config;
    if (error.response?.status !== 401 || !orig || orig._retry) {
      return Promise.reject(error);
    }
    if (isAuthRefreshRequest(orig.url)) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({
          resolve,
          reject,
          config: orig,
        });
      });
    }

    orig._retry = true;
    isRefreshing = true;
    try {
      const refreshed = await tryRefreshSession();
      if (!refreshed) {
        flushQueue(error);
        return Promise.reject(error);
      }
      flushQueue(null);
      return api(orig);
    } catch (refreshError) {
      flushQueue(refreshError);
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);
