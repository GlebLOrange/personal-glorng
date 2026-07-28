import { describe, expect, it } from "vitest";

import router from "@/router";

describe("news routes", () => {
  it("resolves digit-only paths as public article slugs", () => {
    expect(router.resolve("/news/2024").name).toBe("news-article");
  });

  it("resolves editorial edit under /admin/news/:id", () => {
    expect(router.resolve("/admin/news/2024").name).toBe("news-article-edit");
  });

  it("resolves admin list and sources under /admin/news", () => {
    expect(router.resolve("/admin/news").name).toBe("admin-news");
    expect(router.resolve("/admin/news/sources").name).toBe("news-sources");
    expect(router.resolve("/admin/news/sources/3").name).toBe("news-source");
  });

  it("registers redirects from legacy public admin paths", () => {
    const byPath = Object.fromEntries(router.getRoutes().map((r) => [r.path, r]));
    expect(byPath["/news/edit/:id(\\d+)"]?.redirect).toBeTruthy();
    expect(byPath["/news/sources"]?.redirect).toEqual({ name: "news-sources" });
    expect(byPath["/news/sources/:id(\\d+)"]?.redirect).toBeTruthy();
    expect(byPath["/admin/tools/news"]?.redirect).toEqual({ name: "admin-news" });
  });

  it("keeps public list on /news", () => {
    expect(router.resolve("/news").name).toBe("news");
  });
});
