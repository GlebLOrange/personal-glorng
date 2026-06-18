import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { TIME_DATE_WEATHER_LOCATION_ROUTE_NAME } from "@/constants/timeDateWeatherLocation";
import { useAuthStore } from "@/stores/auth";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";
import { safeRedirectPath } from "@/utils/safeUrl";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "portfolio",
    component: () => import("@/pages/PortfolioPage.vue"),
    beforeEnter: () => {
      void fetch("/api/resume");
      return true;
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/LoginPage.vue"),
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/pages/RegisterPage.vue"),
  },
  {
    path: "/verify-email",
    name: "verify-email",
    component: () => import("@/pages/VerifyEmailPage.vue"),
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    component: () => import("@/pages/ForgotPasswordPage.vue"),
  },
  {
    path: "/reset-password",
    name: "reset-password",
    component: () => import("@/pages/ResetPasswordPage.vue"),
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("@/pages/SettingsPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("@/pages/admin/DashboardPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/users",
    name: "admin-users",
    component: () => import("@/pages/admin/AdminUsersPage.vue"),
    meta: { requiresAuth: true, requiresSuperuser: true },
  },
  {
    path: "/tools",
    name: "tools",
    component: () => import("@/pages/ToolsPage.vue"),
  },
  {
    path: "/calculator",
    name: "calculator",
    component: () => import("@/pages/admin/tools/CalculatorTool.vue"),
  },
  {
    path: "/admin/tools/calculator",
    redirect: { name: "calculator" },
  },
  {
    path: "/password-generator",
    name: "password-generator",
    component: () => import("@/pages/admin/tools/PasswordGeneratorTool.vue"),
  },
  {
    path: "/admin/tools/password-generator",
    redirect: { name: "password-generator" },
  },
  {
    path: "/recipes",
    name: "recipes",
    component: () => import("@/pages/admin/tools/RecipesPage.vue"),
  },
  {
    path: "/admin/tools/recipes",
    redirect: { name: "recipes" },
  },
  {
    path: "/shortener",
    name: "shortener",
    component: () => import("@/pages/admin/tools/UrlShortenerTool.vue"),
  },
  {
    path: "/admin/tools/url-shortener",
    redirect: { name: "shortener" },
  },
  {
    path: "/vid-download",
    name: "vid-download",
    component: () => import("@/pages/admin/tools/VidDownloadTool.vue"),
  },
  {
    path: "/admin/tools/vid-download",
    redirect: { name: "vid-download" },
  },
  {
    path: "/admin/tools/currency",
    redirect: { name: "tool-expenses", query: { tab: "converter" } },
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
    path: "/admin/tools/data-extract",
    name: "tool-data-extract",
    component: () => import("@/pages/admin/tools/DataExtractTool.vue"),
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
    path: "/admin/tools/app-logs",
    name: "tool-app-logs",
    component: () => import("@/pages/admin/tools/AppLogsPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/callback",
    name: "oauth-callback",
    component: () => import("@/pages/CallbackPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/time-date-weather-location",
    name: TIME_DATE_WEATHER_LOCATION_ROUTE_NAME,
    component: () => import("@/pages/WeatherPage.vue"),
  },
  {
    path: "/clocks",
    redirect: { name: TIME_DATE_WEATHER_LOCATION_ROUTE_NAME },
  },
  {
    path: "/weather",
    redirect: { name: TIME_DATE_WEATHER_LOCATION_ROUTE_NAME },
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

const TOOL_ROUTE_SLUGS: Partial<Record<string, string>> = {
  "tool-tasks": "tasks",
  "tool-expenses": "expenses",
  "tool-file-share": "file-share",
  "tool-email": "email",
  "tool-feedback": "feedback",
  "tool-ai-chat": "ai-chat",
  "tool-data-extract": "data-extract",
  "tool-audit": "audit",
  "tool-app-logs": "app-logs",
};

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

router.beforeEach(async (to, _from, next) => {
  if (to.name === "tool-ai-chat" && !isAiChatEnabled()) {
    next({ name: "admin" });
    return;
  }
  const auth = useAuthStore();
  if (!auth.sessionResolved) {
    try {
      await auth.resolveSession();
    } catch {
      // sessionError retained; guards proceed with isAuthenticated
    }
  }
  if (to.name === "login" && auth.isAuthenticated) {
    next({ path: safeRedirectPath(to.query.redirect), replace: true });
    return;
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({
      name: "login",
      query: { redirect: to.fullPath },
      replace: true,
    });
    return;
  }
  if (to.meta.requiresSuperuser && auth.isAuthenticated) {
    const { isSuperuser } = usePermissions();
    if (!isSuperuser.value) {
      next({ name: "admin" });
      return;
    }
  }
  const toolSlug = typeof to.name === "string" ? TOOL_ROUTE_SLUGS[to.name] : undefined;
  if (toolSlug && auth.isAuthenticated) {
    const { can } = usePermissions();
    if (!can(toolSlug, "read")) {
      next({ name: "admin" });
      return;
    }
  }
  next();
});

export default router;
