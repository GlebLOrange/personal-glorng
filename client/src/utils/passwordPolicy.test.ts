import { describe, expect, it } from "vitest";

import { passwordStrength, validatePassword } from "@/utils/passwordPolicy";

describe("validatePassword", () => {
  it("rejects passwords under 12 characters", () => {
    expect(validatePassword("Ab1!")).toMatch(/12\+/);
  });

  it("rejects when a required character class is missing", () => {
    expect(validatePassword("mytestpass123!")).toMatch(/uppercase|Password must/i);
    expect(validatePassword("MYTESTPASS123!")).toMatch(/Password must/);
    expect(validatePassword("MyTestPass!!!!")).toMatch(/Password must/);
    expect(validatePassword("MyTestPass1234")).toMatch(/Password must/);
  });

  it("accepts a valid password", () => {
    expect(validatePassword("MyTestPass123!")).toBeNull();
  });
});

describe("passwordStrength", () => {
  it("returns empty for blank input", () => {
    expect(passwordStrength("")).toEqual({
      score: 0,
      label: "empty",
      valid: false,
      message: "Enter a password",
    });
  });

  it("marks invalid mid-strength passwords as not valid", () => {
    const result = passwordStrength("Short1!");
    expect(result.valid).toBe(false);
    expect(result.message).toMatch(/12\+/);
    expect(["weak", "fair", "good"]).toContain(result.label);
  });

  it("labels a valid 12-char password as good", () => {
    const result = passwordStrength("MyTestPass123!");
    expect(result.valid).toBe(true);
    expect(result.label).toBe("good");
    expect(result.message).toBe("Password meets requirements");
  });

  it("labels a longer valid password as strong", () => {
    const result = passwordStrength("MyTestPass123!abcd");
    expect(result.valid).toBe(true);
    expect(result.label).toBe("strong");
    expect(result.score).toBeGreaterThanOrEqual(6);
  });
});
