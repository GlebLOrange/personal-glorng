import { describe, expect, it } from "vitest";

import router from "@/router";

describe("news routes", () => {
  it("resolves digit-only paths as public article slugs", () => {
    expect(router.resolve("/news/2024").name).toBe("news-article");
  });

  it("resolves editorial edit under /news/edit/:id", () => {
    expect(router.resolve("/news/edit/2024").name).toBe("news-article-edit");
  });
});
