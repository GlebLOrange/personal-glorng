import { describe, expect, it } from "vitest";

import { buildContactLinks } from "@/constants/contactMeta";

describe("buildContactLinks", () => {
  it("returns links in stable order with mailto inquiry prefills for email", () => {
    const result = buildContactLinks({
      github: "https://github.com/glorange",
      email: "hello@example.com",
      telegram: "https://t.me/glorange",
      linkedin: "https://www.linkedin.com/in/glorange",
    });

    expect(result.map((link) => link.id)).toEqual(["email", "telegram", "linkedin", "github"]);
    expect(result[0]?.id).toBe("email");
    expect(result[0]?.label).toBe("Email");
    expect(result[0]?.href).toMatch(/^mailto:hello@example\.com\?/);
    expect(result[0]?.href).toContain("subject=Work");
    expect(result[0]?.href).toContain("body=");

    expect(result[1]?.href).toContain("t.me/glorange");
    expect(result[1]?.href).toContain("text=");
  });

  it("skips empty or whitespace-only values", () => {
    const result = buildContactLinks({
      email: "hello@example.com",
      telegram: "   ",
      linkedin: "",
      github: "https://github.com/glorange",
    });

    expect(result.map((link) => link.id)).toEqual(["email", "github"]);
  });

  it("skips unsafe contact values", () => {
    const result = buildContactLinks({
      email: "not an email",
      telegram: "javascript:alert(1)",
      linkedin: "http://example.com/profile",
      github: "https://github.com/glorange",
    });

    expect(result.map((link) => link.id)).toEqual(["github"]);
  });
});
