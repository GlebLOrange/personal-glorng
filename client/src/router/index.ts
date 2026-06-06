import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";

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
    path: "/admin",
    name: "admin",
    component: () => import("@/pages/admin/DashboardPage.vue"),
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
    path: "/weather",
    name: "weather",
    component: () => import("@/pages/WeatherPage.vue"),
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
  "tool-recipes": "recipes",
  "tool-file-share": "file-share",
  "tool-url-shortener": "url-shortener",
  "tool-calculator": "calculator",
  "tool-currency": "currency",
  "tool-vid-download": "vid-download",
  "tool-email": "email",
  "tool-feedback": "feedback",
  "tool-ai-chat": "ai-chat",
  "tool-audit": "audit",
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
    const redirect = to.query.redirect;
    const target =
      typeof redirect === "string" && redirect.startsWith("/") && !redirect.startsWith("//")
        ? redirect
        : "/admin";
    next({ path: target, replace: true });
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
