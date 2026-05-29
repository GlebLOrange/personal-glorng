import axios, { type AxiosRequestConfig } from "axios";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

function isAuthRefreshRequest(url: string | undefined): boolean {
  return typeof url === "string" && url.includes("/auth/refresh");
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const orig: AxiosRequestConfig & { _retry?: boolean } = error.config;
    if (error.response?.status !== 401 || orig._retry) {
      return Promise.reject(error);
    }
    if (isAuthRefreshRequest(orig.url)) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingQueue.push(() => resolve(api(orig)));
      });
    }

    orig._retry = true;
    isRefreshing = true;
    try {
      await axios.post("/api/auth/refresh", undefined, { withCredentials: true });
      pendingQueue.forEach((cb) => cb());
      return api(orig);
    } catch {
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
      pendingQueue = [];
    }
  },
);
