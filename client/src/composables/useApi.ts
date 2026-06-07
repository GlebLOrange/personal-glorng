import axios, { type AxiosRequestConfig } from "axios";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

let isRefreshing = false;
type QueueEntry = {
  resolve: () => void;
  reject: (error: unknown) => void;
};
let pendingQueue: QueueEntry[] = [];

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
      return new Promise((resolve, reject) => {
        pendingQueue.push({
          resolve: () => resolve(api(orig)),
          reject,
        });
      });
    }

    orig._retry = true;
    isRefreshing = true;
    try {
      await api.post("/auth/refresh");
      pendingQueue.forEach(({ resolve }) => resolve());
      return api(orig);
    } catch (refreshError) {
      pendingQueue.forEach(({ reject }) => reject(refreshError));
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
      pendingQueue = [];
    }
  },
);
