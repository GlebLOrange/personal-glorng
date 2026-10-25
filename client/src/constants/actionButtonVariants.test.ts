import { describe, expect, it } from "vitest";

import {
  classesForActionButton,
  SEMANTIC_ACTION_HTTP_FAMILY,
} from "@/constants/actionButtonVariants";

describe("actionButtonVariants", () => {
  it("maps semantic actions to HTTP families for pill/icon chrome", () => {
    expect(SEMANTIC_ACTION_HTTP_FAMILY).toEqual({
      create: "1xx",
      add: "1xx",
      save: "1xx",
      edit: "1xx",
      remove: "4xx",
      delete: "4xx",
      cancel: "5xx",
    });
    expect(SEMANTIC_ACTION_HTTP_FAMILY.delete).toBe("4xx");
  });

  it("paints create/add like pale primary (1xx wash)", () => {
    for (const variant of ["create", "add", "primary"] as const) {
      const classes = classesForActionButton({ variant });
      expect(classes).toContain("bg-accent-coral/10");
      expect(classes).toContain("text-accent-coral/88");
    }
  });

  it("paints save and success as primary wash", () => {
    expect(classesForActionButton({ variant: "save" })).toContain("text-accent-coral/88");
    expect(classesForActionButton({ variant: "success" })).toContain("text-accent-coral/88");
  });

  it("paints cancel as ghost, edit as secondary, delete as 4xx", () => {
    expect(classesForActionButton({ variant: "cancel" })).toContain("bg-transparent");
    expect(classesForActionButton({ variant: "edit" })).toContain("bg-surface-card");
    expect(classesForActionButton({ variant: "delete" })).toContain("text-status-error/88");
  });

  it("gives secondary a resting grayscale fill distinct from ghost", () => {
    const secondary = classesForActionButton({ variant: "secondary" });
    const ghost = classesForActionButton({ variant: "ghost" });
    expect(secondary).toContain("bg-surface-card");
    expect(secondary).toContain("border-surface-border");
    expect(ghost).toContain("bg-transparent");
    expect(ghost).not.toContain("bg-surface-card");
  });
});
