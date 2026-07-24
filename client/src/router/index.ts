import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { WEATHER_ROUTE_NAME } from "@/constants/weather";
import { useAuthStore } from "@/stores/auth";
import { isCalculatorMode, normalizeCalculatorMode } from "@/composables/useExpenseCalculator";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";
import { installScrollRestore, resolveScrollBehavior } from "@/utils/scrollRestore";
import { applyRouteSeo } from "@/composables/useRouteSeo";
import { safeRedirectPath } from "@/utils/safeUrl";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "portfolio",
    component: () => import("@/pages/PortfolioPage.vue"),
    meta: {
      title: "Developer Portfolio",
      description:
        "Gleb.Y — developer portfolio, tools, and curated news. Full-stack delivery of web apps, APIs, and product platforms.",
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
    name: "register",
    component: () => import("@/pages/RegisterPage.vue"),
    meta: { title: "Create account", noindex: true },
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
    path: "/admin/send-email",
    name: "tool-email",
    component: () => import("@/pages/admin/tools/EmailTool.vue"),
    meta: { requiresAuth: true, title: "Send email", noindex: true },
  },
  {
    path: "/admin/api/docs",
    name: "admin-api-docs",
    redirect: "/api/docs",
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
    component: () => import("@/pages/NewsRoutePage.vue"),
    meta: {
      resolveSession: true,
      scrollRestore: "volatile",
      title: "News",
      description: "Curated worldwide news digest with source attribution.",
    },
  },
  {
    path: "/news/sources",
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
    path: "/news/sources/:id(\\d+)",
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
    path: "/news/edit/:id(\\d+)",
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
    component: () => import("@/pages/admin/tools/CalculatorTool.vue"),
    meta: { title: "Calculator", description: "Quick math calculations." },
  },
  {
    path: "/expense-calculator",
    name: "expense-calculator",
    component: () => import("@/pages/admin/tools/ExpenseCalculatorTool.vue"),
    meta: {
      resolveSession: true,
      title: "Expense calculator",
      description: "Convert currencies, sum line items, and plan budgets.",
    },
  },
  {
    path: "/password-generator",
    name: "password-generator",
    component: () => import("@/pages/admin/tools/PasswordGeneratorTool.vue"),
    meta: { title: "Password generator", description: "Generate strong random passwords." },
  },
  {
    path: "/recipes",
    name: "recipes",
    component: () => import("@/pages/admin/tools/RecipesPage.vue"),
    meta: {
      scrollRestore: "volatile",
      title: "Recipes",
      description: "Personal recipe book and food notes.",
    },
  },
  {
    path: "/shortener",
    name: "shortener",
    component: () => import("@/pages/admin/tools/UrlShortenerTool.vue"),
    meta: { title: "URL shortener", description: "Create and manage short URLs." },
  },
  {
    path: "/vid-download",
    name: "vid-download",
    component: () => import("@/pages/admin/tools/VidDownloadTool.vue"),
    meta: { title: "Video downloader", description: "Download videos with yt-dlp." },
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
  // Legacy /admin/tools/* redirects
  { path: "/admin/tools/calculator", redirect: { name: "calculator" } },
  { path: "/admin/tools/password-generator", redirect: { name: "password-generator" } },
  { path: "/admin/tools/recipes", redirect: { name: "recipes" } },
  { path: "/admin/tools/url-shortener", redirect: { name: "shortener" } },
  { path: "/admin/tools/vid-download", redirect: { name: "vid-download" } },
  {
    path: "/admin/tools/currency",
    redirect: { name: "tool-expenses", query: { tab: "calculator", mode: "convert" } },
  },
  { path: "/admin/tools/file-share", redirect: { name: "tool-file-share" } },
  { path: "/admin/tools/tasks", redirect: { name: "tool-tasks" } },
  { path: "/admin/tools/expenses", redirect: { name: "tool-expenses" } },
  { path: "/admin/tools/email", redirect: { name: "tool-email" } },
  { path: "/admin/tools/data-extract", redirect: { name: "tool-data-extract" } },
  { path: "/admin/tools/feedback", redirect: { name: "tool-feedback" } },
  { path: "/admin/tools/news-sources", redirect: { name: "news-sources" } },
  { path: "/admin/tools/ai-chat", redirect: { name: "tool-ai-chat" } },
  { path: "/admin/tools/audit", redirect: { name: "tool-audit" } },
  { path: "/admin/tools/app-logs", redirect: { name: "tool-app-logs" } },
  { path: "/admin/tools/search", redirect: { name: "tool-search" } },
  { path: "/admin/tools/news", redirect: { name: "news", query: { manage: "1" } } },
  {
    path: "/admin/tools/news/:id",
    redirect: (to) => ({ name: "news-article-edit", params: { id: to.params.id } }),
  },
  {
    path: "/callback",
    name: "oauth-callback",
    component: () => import("@/pages/CallbackPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/weather",
    name: WEATHER_ROUTE_NAME,
    component: () => import("@/pages/WeatherPage.vue"),
    meta: {
      scrollRestore: "live",
      title: "Weather",
      description: "Weather lookup, saved locations, and local time.",
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
  "news-article-edit": "news",
  "news-sources": "news-sources",
  "news-source": "news-sources",
  "tool-data-extract": "data-extract",
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

router.beforeEach(async (to, _from, next) => {
  if (to.name === "tool-ai-chat" && !isAiChatEnabled()) {
    next({ name: "admin" });
    return;
  }
  const auth = useAuthStore();
  const shouldResolveSession =
    to.name === "login" ||
    Boolean(to.meta.resolveSession) ||
    Boolean(to.meta.requiresAuth) ||
    Boolean(to.meta.requiresSuperuser);
  if (shouldResolveSession && !auth.sessionResolved) {
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
  if (to.name === "expense-calculator" && auth.isAuthenticated) {
    const { can } = usePermissions();
    if (can("expenses", "read")) {
      const rawTab =
        typeof to.query.tab === "string"
          ? to.query.tab
          : typeof to.query.mode === "string"
            ? to.query.mode
            : "convert";
      if (rawTab === "converter" || isCalculatorMode(rawTab)) {
        next({
          name: "tool-expenses",
          query: { tab: "calculator", mode: normalizeCalculatorMode(rawTab) },
          replace: true,
        });
        return;
      }
      next({ name: "tool-expenses", query: { tab: rawTab }, replace: true });
      return;
    }
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
    const { canAccess } = usePermissions();
    if (!canAccess(toolSlug)) {
      next({ name: "admin" });
      return;
    }
  }
  next();
});

router.afterEach((to) => {
  applyRouteSeo(to);
});

export default router;
