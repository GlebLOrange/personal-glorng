import { describe, expect, it } from "vitest";

import { buildContactLinks } from "@/constants/contactMeta";

describe("buildContactLinks", () => {
  it("returns links in stable order with mailto for email", () => {
    const result = buildContactLinks({
      github: "https://github.com/glorange",
      email: "hello@example.com",
      telegram: "https://t.me/glorange",
      linkedin: "https://www.linkedin.com/in/glorange",
    });

    expect(result.map((link) => link.id)).toEqual(["email", "telegram", "linkedin", "github"]);
    expect(result[0]).toEqual({
      id: "email",
      label: "Email",
      href: "mailto:hello@example.com",
    });
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
});
