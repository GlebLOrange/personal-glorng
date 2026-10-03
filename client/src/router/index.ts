import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { WEATHER_ROUTE_NAME } from "@/constants/weather";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled, isExpensesEnabled } from "@/utils/featureFlags";
import { installScrollRestore, resolveScrollBehavior } from "@/utils/scrollRestore";
import { applyRouteSeo } from "@/composables/useRouteSeo";
import { safeRedirectPath } from "@/utils/safeUrl";
import { scrubSensitivePath } from "@/utils/sensitiveUrl";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "portfolio",
    component: () => import("@/pages/PortfolioPage.vue"),
    meta: {
      title: "Python Backend / FastAPI Engineer",
      description:
        "Gleb.Y — Python/FastAPI backend engineer. Production platforms: APIs, auth, workers, data stores, and CI/CD. Full-stack capable.",
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/LoginPage.vue"),
    meta: { title: "Login", noindex: true },
  },
  {
    path: "/register",
    redirect: "/login",
  },
  {
    path: "/verify-email",
    name: "verify-email",
    component: () => import("@/pages/VerifyEmailPage.vue"),
    meta: { title: "Verify email", noindex: true },
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    component: () => import("@/pages/ForgotPasswordPage.vue"),
    meta: { title: "Forgot password", noindex: true },
  },
  {
    path: "/reset-password",
    name: "reset-password",
    component: () => import("@/pages/ResetPasswordPage.vue"),
    meta: { title: "Reset password", noindex: true },
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("@/pages/SettingsPage.vue"),
    meta: { requiresAuth: true, title: "Settings", noindex: true },
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("@/pages/admin/DashboardPage.vue"),
    meta: { requiresAuth: true, title: "Admin", noindex: true },
  },
  {
    path: "/admin/users",
    name: "admin-users",
    component: () => import("@/pages/admin/AdminUsersPage.vue"),
    meta: {
      requiresAuth: true,
      requiresSuperuser: true,
      scrollRestore: "volatile",
      title: "Users",
      noindex: true,
    },
  },
  {
    path: "/admin/feedback",
    name: "tool-feedback",
    component: () => import("@/pages/admin/tools/FeedbackPage.vue"),
    meta: { requiresAuth: true, title: "Feedback", noindex: true },
  },
  {
    path: "/admin/audit-logs",
    name: "tool-audit",
    component: () => import("@/pages/admin/tools/AuditPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile", title: "Audit", noindex: true },
  },
  {
    path: "/admin/app-logs",
    name: "tool-app-logs",
    component: () => import("@/pages/admin/tools/AppLogsPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile", title: "App logs", noindex: true },
  },
  {
    path: "/admin/search",
    name: "tool-search",
    component: () => import("@/pages/admin/tools/AdminSearchPage.vue"),
    meta: { requiresAuth: true, title: "Search", noindex: true },
  },
  {
    path: "/admin/ai-chat",
    name: "tool-ai-chat",
    component: () => import("@/pages/admin/tools/AiChatTool.vue"),
    meta: { requiresAuth: true, requiresSuperuser: true, title: "AI chat", noindex: true },
  },
  {
    path: "/admin/db-maintenance",
    name: "tool-db-maintenance",
    component: () => import("@/pages/admin/tools/DbMaintenanceTool.vue"),
    meta: {
      requiresAuth: true,
      requiresSuperuser: true,
      title: "DB maintenance",
      noindex: true,
    },
  },
  {
    path: "/admin/send-email",
    name: "tool-email",
    component: () => import("@/pages/admin/tools/EmailTool.vue"),
    meta: { requiresAuth: true, title: "Send email", noindex: true },
  },
  {
    path: "/admin/news",
    name: "admin-news",
    component: () => import("@/pages/admin/tools/NewsAdminPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile", title: "Manage news", noindex: true },
  },
  {
    path: "/admin/news/sources",
    name: "news-sources",
    component: () => import("@/pages/admin/tools/NewsSourcesPage.vue"),
    meta: {
      requiresAuth: true,
      scrollRestore: "volatile",
      title: "News sources",
      noindex: true,
    },
  },
  {
    path: "/admin/news/sources/:id(\\d+)",
    name: "news-source",
    component: () => import("@/pages/admin/tools/NewsSourcesPage.vue"),
    meta: {
      requiresAuth: true,
      scrollRestore: "volatile",
      title: "News source",
      noindex: true,
    },
  },
  {
    path: "/admin/news/:id(\\d+)",
    name: "news-article-edit",
    component: () => import("@/pages/admin/tools/NewsArticleAdminPage.vue"),
    meta: {
      requiresAuth: true,
      scrollRestore: "volatile",
      title: "Edit news article",
      noindex: true,
    },
  },
  {
    path: "/admin/api/docs",
    name: "admin-api-docs",
    // Swagger is a FastAPI page, not a Vue route — leave the SPA.
    beforeEnter: () => {
      window.location.assign("/api/docs");
      return false;
    },
    component: () => import("@/pages/admin/DashboardPage.vue"),
    meta: { requiresAuth: true, requiresSuperuser: true, noindex: true },
  },
  {
    path: "/tools",
    name: "tools",
    component: () => import("@/pages/ToolsPage.vue"),
    meta: {
      title: "Tools",
      description: "Public utilities — calculator, password generator, recipes, weather, and more.",
    },
  },
  {
    path: "/news",
    name: "news",
    component: () => import("@/pages/NewsPage.vue"),
    meta: {
      resolveSession: true,
      scrollRestore: "volatile",
      title: "News",
      description: "Curated worldwide news digest with source attribution.",
    },
  },
  {
    path: "/news/edit/:id(\\d+)",
    redirect: (to) => ({ name: "news-article-edit", params: { id: to.params.id } }),
  },
  {
    path: "/news/sources/:id(\\d+)",
    redirect: (to) => ({ name: "news-source", params: { id: to.params.id } }),
  },
  {
    path: "/news/sources",
    redirect: { name: "news-sources" },
  },
  {
    path: "/news/:slug",
    name: "news-article",
    component: () => import("@/pages/NewsArticlePage.vue"),
    meta: {
      scrollRestore: "volatile",
      title: "Article",
      description: "Curated news summary with source attribution.",
    },
  },
  {
    path: "/calculator",
    name: "calculator",
    component: () => import("@/pages/tools/CalculatorTool.vue"),
    meta: { title: "Calculator", description: "Quick math calculations.", noindex: true },
  },
  {
    path: "/expense-calculator",
    redirect: { name: "tool-expenses" },
  },
  {
    path: "/password-generator",
    name: "password-generator",
    component: () => import("@/pages/tools/PasswordGeneratorTool.vue"),
    meta: {
      title: "Password generator",
      description: "Generate strong random passwords.",
      noindex: true,
    },
  },
  {
    path: "/qr-generator",
    name: "qr-generator",
    component: () => import("@/pages/tools/QrGeneratorTool.vue"),
    meta: {
      title: "QR generator",
      description: "Generate QR codes as downloadable SVG.",
      noindex: true,
    },
  },
  {
    path: "/recipes",
    name: "recipes",
    component: () => import("@/pages/tools/RecipesPage.vue"),
    meta: {
      scrollRestore: "volatile",
      title: "Recipes",
      description: "Personal recipe book and food notes.",
      noindex: true,
    },
  },
  {
    path: "/shortener",
    name: "shortener",
    component: () => import("@/pages/tools/UrlShortenerTool.vue"),
    meta: { title: "URL shortener", description: "Create and manage short URLs.", noindex: true },
  },
  {
    path: "/vid-download",
    name: "vid-download",
    component: () => import("@/pages/tools/VidDownloadTool.vue"),
    meta: {
      requiresAuth: true,
      title: "Video downloader",
      description: "Download videos with yt-dlp.",
      noindex: true,
    },
  },
  {
    path: "/file-share",
    name: "tool-file-share",
    component: () => import("@/pages/admin/tools/FileShareTool.vue"),
    meta: { requiresAuth: true, title: "File share", noindex: true },
  },
  {
    path: "/tasks",
    name: "tool-tasks",
    component: () => import("@/pages/admin/tools/TasksPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile", title: "Tasks", noindex: true },
  },
  {
    path: "/expenses",
    name: "tool-expenses",
    component: () => import("@/pages/admin/tools/ExpensesTool.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile", title: "Expenses", noindex: true },
  },
  {
    path: "/data-extract",
    name: "tool-data-extract",
    component: () => import("@/pages/admin/tools/DataExtractTool.vue"),
    meta: { requiresAuth: true, title: "Data extract", noindex: true },
  },
  {
    path: "/health-checker",
    name: "tool-health-checker",
    component: () => import("@/pages/tools/HealthCheckerTool.vue"),
    meta: {
      requiresAuth: true,
      title: "Health checker",
      description: "Monitor website and API uptime, latency, SSL, and DNS.",
      noindex: true,
    },
  },
  {
    path: "/callback",
    name: "oauth-callback",
    component: () => import("@/pages/CallbackPage.vue"),
    meta: { requiresAuth: true, title: "GitHub callback", noindex: true },
  },
  {
    path: "/weather",
    name: WEATHER_ROUTE_NAME,
    component: () => import("@/pages/WeatherPage.vue"),
    meta: {
      scrollRestore: "live",
      title: "Weather",
      description: "Weather lookup, saved locations, and local time.",
      noindex: true,
    },
  },
  {
    path: "/time-date-weather-location",
    redirect: { name: WEATHER_ROUTE_NAME },
  },
  {
    path: "/clocks",
    redirect: { name: WEATHER_ROUTE_NAME },
  },
  {
    path: "/privacy",
    name: "privacy",
    component: () => import("@/pages/PrivacyPage.vue"),
    meta: { title: "Privacy policy" },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/pages/NotFoundPage.vue"),
    meta: { title: "Not found", noindex: true },
  },
];

const TOOL_ROUTE_SLUGS: Partial<Record<string, string>> = {
  "tool-tasks": "tasks",
  "tool-expenses": "expenses",
  "tool-file-share": "file-share",
  "tool-email": "email",
  "tool-feedback": "feedback",
  "admin-news": "news",
  "news-article-edit": "news",
  "news-sources": "news-sources",
  "news-source": "news-sources",
  "tool-data-extract": "data-extract",
  "tool-health-checker": "health-checker",
  "vid-download": "vid-download",
  "tool-audit": "audit",
  "tool-app-logs": "app-logs",
  "tool-search": "search",
};

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (to.hash) {
      return { el: to.hash, behavior: "smooth" };
    }
    return resolveScrollBehavior(to, savedPosition);
  },
});

installScrollRestore(router);

router.beforeEach(async (to, _from) => {
  if (to.name === "news" && String(to.query.manage ?? "") === "1") {
    return { name: "admin-news", replace: true };
  }
  if (to.name === "tool-ai-chat" && !isAiChatEnabled()) {
    return { name: "admin", query: { aichat: "off" }, replace: true };
  }
  if (!isExpensesEnabled() && to.name === "tool-expenses") {
    return { name: "tools", query: { expenses: "off" }, replace: true };
  }
  const shouldResolveSession =
    to.name === "login" ||
    Boolean(to.meta.resolveSession) ||
    Boolean(to.meta.requiresAuth) ||
    Boolean(to.meta.requiresSuperuser);
  const needsAuthState =
    shouldResolveSession ||
    Boolean(to.meta.requiresAuth) ||
    Boolean(to.meta.requiresSuperuser) ||
    (typeof to.name === "string" && to.name in TOOL_ROUTE_SLUGS);
  if (!needsAuthState) {
    return;
  }
  const { useAuthStore } = await import("@/stores/auth");
  const auth = useAuthStore();
  if (shouldResolveSession && !auth.sessionResolved) {
    try {
      await auth.resolveSession();
    } catch {
      // sessionError retained; guards proceed with isAuthenticated
    }
  }
  if (to.name === "login" && auth.isAuthenticated) {
    return { path: safeRedirectPath(to.query.redirect), replace: true };
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return {
      name: "login",
      query: { redirect: scrubSensitivePath(to.fullPath) },
      replace: true,
    };
  }
  if (to.meta.requiresSuperuser && auth.isAuthenticated) {
    const { isSuperuser } = usePermissions();
    if (!isSuperuser.value) {
      return { name: "admin", query: { access: "denied" }, replace: true };
    }
  }
  const toolSlug = typeof to.name === "string" ? TOOL_ROUTE_SLUGS[to.name] : undefined;
  if (toolSlug && auth.isAuthenticated) {
    const { canAccess } = usePermissions();
    if (!canAccess(toolSlug)) {
      return { name: "admin", query: { access: "denied" }, replace: true };
    }
  }
});

router.afterEach((to) => {
  applyRouteSeo(to);
});

export default router;
