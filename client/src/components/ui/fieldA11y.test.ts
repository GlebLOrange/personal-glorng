import { describe, expect, it } from "vitest";

import { resolveFieldCopy } from "@/components/ui/fieldA11y";

describe("resolveFieldCopy", () => {
  it("uses label as name and omits tip when placeholder is absent", () => {
    expect(resolveFieldCopy("email")).toEqual({ name: "email", tip: undefined });
  });

  it("omits tip when placeholder equals label", () => {
    expect(resolveFieldCopy("password", "password")).toEqual({
      name: "password",
      tip: undefined,
    });
  });

  it("keeps a distinct placeholder as the overlay tip", () => {
    expect(resolveFieldCopy("email", "you@example.com")).toEqual({
      name: "email",
      tip: "you@example.com",
    });
  });

  it("leaves placeholder-only fields as tip-only", () => {
    expect(resolveFieldCopy(undefined, "title")).toEqual({
      name: undefined,
      tip: "title",
    });
  });

  it("returns empty copy when both are absent", () => {
    expect(resolveFieldCopy()).toEqual({ name: undefined, tip: undefined });
  });
});
