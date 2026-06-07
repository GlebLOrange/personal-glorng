import { describe, expect, it } from "vitest";

import { PLATFORM_SERVICES } from "@/platform/services";
import router from "@/router";

const ADMIN_TOOL_ROUTE_PREFIX = "/admin/tools/";

describe("platform catalog parity", () => {
  it("admin tool routes reference known registry slugs", () => {
    const registrySlugs = new Set(PLATFORM_SERVICES.map((s) => s.slug));
    const adminToolRoutes = router
      .getRoutes()
      .map((r) => r.path)
      .filter((path) => path.startsWith(ADMIN_TOOL_ROUTE_PREFIX));

    for (const path of adminToolRoutes) {
      const slug = path.slice(ADMIN_TOOL_ROUTE_PREFIX.length).split("/")[0];
      if (slug === "currency") continue;
      expect(registrySlugs.has(slug)).toBe(true);
    }
  });

  it("registry admin routes are registered or public redirects", () => {
    const routePaths = new Set(router.getRoutes().map((r) => r.path));
    for (const service of PLATFORM_SERVICES) {
      if (service.external) continue;
      const normalized = service.adminRoute.replace(/\/$/, "");
      const hasRoute =
        routePaths.has(normalized) ||
        routePaths.has(`${normalized}/`) ||
        router.getRoutes().some((r) => r.redirect === normalized);
      expect(hasRoute, `missing route for ${service.slug}`).toBe(true);
    }
  });
});
