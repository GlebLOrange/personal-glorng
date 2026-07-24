import { describe, expect, it } from "vitest";

import { PLATFORM_SERVICES } from "@/platform/services";
import router from "@/router";

describe("platform catalog parity", () => {
  it("registry admin routes are registered or public redirects", () => {
    const routePaths = new Set(router.getRoutes().map((r) => r.path));
    for (const service of PLATFORM_SERVICES) {
      if (service.external) {
        expect(
          routePaths.has(service.adminRoute) || service.adminRoute.startsWith("/api/"),
          `missing external route for ${service.slug}`,
        ).toBe(true);
        continue;
      }
      const normalized = service.adminRoute.split("?")[0]!.replace(/\/$/, "");
      const hasRoute =
        routePaths.has(normalized) ||
        routePaths.has(`${normalized}/`) ||
        router.getRoutes().some((r) => {
          if (typeof r.redirect === "string") return r.redirect === normalized;
          return false;
        });
      expect(hasRoute, `missing route for ${service.slug} (${normalized})`).toBe(true);
    }
  });
});
