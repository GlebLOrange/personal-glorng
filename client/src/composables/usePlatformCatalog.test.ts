import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";

import { mapApiPlatformService } from "@/composables/usePlatformCatalog";

const base = {
  slug: "tasks",
  name: "tasks",
  category: "productivity",
  category_label: "productivity",
  description: "Manage tasks",
  api_prefix: "/tasks",
  icon: "☐",
  capabilities: ["read"],
  external: false,
};

describe("mapApiPlatformService", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("keeps relative admin routes", () => {
    const mapped = mapApiPlatformService({ ...base, admin_route: "/tasks" });
    expect(mapped?.adminRoute).toBe("/tasks");
  });

  it("keeps https external admin routes", () => {
    const mapped = mapApiPlatformService({
      ...base,
      slug: "docs",
      admin_route: "https://example.com/docs",
      external: true,
    });
    expect(mapped?.adminRoute).toBe("https://example.com/docs");
  });

  it("drops services with javascript admin routes", () => {
    expect(mapApiPlatformService({ ...base, admin_route: "javascript:alert(1)" })).toBeNull();
  });

  it("drops services with protocol-relative admin routes", () => {
    expect(mapApiPlatformService({ ...base, admin_route: "//evil.example/x" })).toBeNull();
  });

  it("clears unsafe public_route without dropping the service", () => {
    const mapped = mapApiPlatformService({
      ...base,
      admin_route: "/expenses",
      public_route: "javascript:alert(1)",
    });
    expect(mapped?.adminRoute).toBe("/expenses");
    expect(mapped?.publicRoute).toBeUndefined();
  });

  it("keeps safe public_route", () => {
    const mapped = mapApiPlatformService({
      ...base,
      admin_route: "/expenses",
      public_route: "/expense-calculator",
    });
    expect(mapped?.publicRoute).toBe("/expense-calculator");
  });
});
