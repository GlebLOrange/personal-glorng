import { describe, expect, it } from "vitest";

import { scrubSensitivePath, scrubSensitiveSearch, scrubSensitiveUrl } from "@/utils/sensitiveUrl";

describe("scrubSensitiveSearch", () => {
  it("strips token/code/state and keeps other params", () => {
    expect(scrubSensitiveSearch("?token=secret&tab=1")).toBe("?tab=1");
    expect(scrubSensitiveSearch("code=abc&state=xyz")).toBe("");
    expect(scrubSensitiveSearch("?foo=bar")).toBe("?foo=bar");
  });
});

describe("scrubSensitivePath", () => {
  it("scrubs query keys and preserves pathname/hash", () => {
    expect(scrubSensitivePath("/verify-email?token=abc#x")).toBe("/verify-email#x");
    expect(scrubSensitivePath("/callback?code=1&state=2&next=1")).toBe("/callback?next=1");
  });
});

describe("scrubSensitiveUrl", () => {
  it("scrubs absolute URLs", () => {
    expect(scrubSensitiveUrl("https://example.com/reset-password?token=t")).toBe(
      "https://example.com/reset-password",
    );
  });
});
