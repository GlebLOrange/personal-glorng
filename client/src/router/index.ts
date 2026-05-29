import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { isAiChatEnabled } from "@/utils/featureFlags";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "portfolio",
    component: () => import("@/pages/PortfolioPage.vue"),
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/LoginPage.vue"),
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("@/pages/admin/DashboardPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/weather",
    name: "tool-weather",
    component: () => import("@/pages/admin/tools/WeatherTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/calculator",
    name: "tool-calculator",
    component: () => import("@/pages/admin/tools/CalculatorTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/currency",
    name: "tool-currency",
    component: () => import("@/pages/admin/tools/CurrencyConverterTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/url-shortener",
    name: "tool-url-shortener",
    component: () => import("@/pages/admin/tools/UrlShortenerTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/vid-download",
    name: "tool-vid-download",
    component: () => import("@/pages/admin/tools/VidDownloadTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/file-share",
    name: "tool-file-share",
    component: () => import("@/pages/admin/tools/FileShareTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/tasks",
    name: "tool-tasks",
    component: () => import("@/pages/admin/tools/TasksPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/recipes",
    name: "tool-recipes",
    component: () => import("@/pages/admin/tools/RecipesPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/expenses",
    name: "tool-expenses",
    component: () => import("@/pages/admin/tools/ExpensesTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/email",
    name: "tool-email",
    component: () => import("@/pages/admin/tools/EmailTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/feedback",
    name: "tool-feedback",
    component: () => import("@/pages/admin/tools/FeedbackPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/ai-chat",
    name: "tool-ai-chat",
    component: () => import("@/pages/admin/tools/AiChatTool.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/audit",
    name: "tool-audit",
    component: () => import("@/pages/admin/tools/AuditPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/callback",
    name: "oauth-callback",
    component: () => import("@/pages/CallbackPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/privacy",
    name: "privacy",
    component: () => import("@/pages/PrivacyPage.vue"),
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/pages/NotFoundPage.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

router.beforeEach((to, _from, next) => {
  if (to.name === "tool-ai-chat" && !isAiChatEnabled()) {
    next({ name: "admin" });
    return;
  }
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({
      name: "not-found",
      params: { pathMatch: to.path.split("/").filter(Boolean) },
      replace: true,
    });
    return;
  }
  next();
});

export function initAnalytics(id: string): void {
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${id}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function (...args: unknown[]) {
    window.dataLayer!.push(args);
  };
  window.gtag("js", new Date());
  window.gtag("config", id, { send_page_view: false });

  router.afterEach((to) => {
    window.gtag!("event", "page_view", {
      page_path: to.fullPath,
      page_title: to.name?.toString(),
    });
  });
}

export default router;
