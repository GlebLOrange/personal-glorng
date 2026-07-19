import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { WEATHER_ROUTE_NAME } from "@/constants/weather";
import { useAuthStore } from "@/stores/auth";
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
    path: "/admin/tools/calculator",
    redirect: { name: "calculator" },
  },
  {
    path: "/password-generator",
    name: "password-generator",
    component: () => import("@/pages/admin/tools/PasswordGeneratorTool.vue"),
    meta: { title: "Password generator", description: "Generate strong random passwords." },
  },
  {
    path: "/admin/tools/password-generator",
    redirect: { name: "password-generator" },
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
    path: "/admin/tools/recipes",
    redirect: { name: "recipes" },
  },
  {
    path: "/shortener",
    name: "shortener",
    component: () => import("@/pages/admin/tools/UrlShortenerTool.vue"),
    meta: { title: "URL shortener", description: "Create and manage short URLs." },
  },
  {
    path: "/admin/tools/url-shortener",
    redirect: { name: "shortener" },
  },
  {
    path: "/vid-download",
    name: "vid-download",
    component: () => import("@/pages/admin/tools/VidDownloadTool.vue"),
    meta: { title: "Video downloader", description: "Download videos with yt-dlp." },
  },
  {
    path: "/admin/tools/vid-download",
    redirect: { name: "vid-download" },
  },
  {
    path: "/admin/tools/currency",
    redirect: { name: "tool-expenses", query: { tab: "convert" } },
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
    meta: { requiresAuth: true, scrollRestore: "volatile" },
  },
  {
    path: "/admin/tools/expenses",
    name: "tool-expenses",
    component: () => import("@/pages/admin/tools/ExpensesTool.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile" },
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
    path: "/admin/tools/news-sources",
    name: "tool-news-sources",
    component: () => import("@/pages/admin/tools/NewsSourcesPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/ai-chat",
    name: "tool-ai-chat",
    component: () => import("@/pages/admin/tools/AiChatTool.vue"),
    meta: { requiresAuth: true, requiresSuperuser: true },
  },
  {
    path: "/admin/tools/audit",
    name: "tool-audit",
    component: () => import("@/pages/admin/tools/AuditPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile" },
  },
  {
    path: "/admin/tools/app-logs",
    name: "tool-app-logs",
    component: () => import("@/pages/admin/tools/AppLogsPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile" },
  },
  {
    path: "/admin/tools/search",
    name: "tool-search",
    component: () => import("@/pages/admin/tools/AdminSearchPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/tools/news",
    name: "tool-news",
    component: () => import("@/pages/admin/tools/NewsAdminPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile" },
  },
  {
    path: "/admin/tools/news/:id",
    name: "tool-news-article",
    component: () => import("@/pages/admin/tools/NewsArticleAdminPage.vue"),
    meta: { requiresAuth: true, scrollRestore: "volatile" },
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
  "tool-news": "news",
  "tool-news-article": "news",
  "tool-news-sources": "news-sources",
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
      const tab = rawTab === "converter" ? "convert" : rawTab;
      next({ name: "tool-expenses", query: { tab }, replace: true });
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
    const { can } = usePermissions();
    if (!can(toolSlug, "read")) {
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
