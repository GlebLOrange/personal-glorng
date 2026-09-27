import { describe, expect, it } from "vitest";

import {
  classesForActionButton,
  SEMANTIC_ACTION_HTTP_FAMILY,
} from "@/constants/actionButtonVariants";

describe("actionButtonVariants", () => {
  it("maps semantic actions to HTTP families", () => {
    expect(SEMANTIC_ACTION_HTTP_FAMILY).toEqual({
      create: "1xx",
      add: "1xx",
      save: "2xx",
      edit: "3xx",
      remove: "4xx",
      delete: "4xx",
      cancel: "5xx",
    });
    expect(SEMANTIC_ACTION_HTTP_FAMILY.delete).toBe("4xx");
  });

  it("paints create/add like pale primary (1xx wash)", () => {
    for (const variant of ["create", "add", "primary"] as const) {
      const classes = classesForActionButton({ variant });
      expect(classes).toContain("bg-accent-blue/10");
      expect(classes).toContain("text-accent-blue/88");
    }
  });

  it("paints save and success alias as 2xx wash", () => {
    expect(classesForActionButton({ variant: "save" })).toContain("text-status-success/88");
    expect(classesForActionButton({ variant: "success" })).toContain("text-status-success/88");
  });

  it("paints cancel as 5xx and delete as 4xx", () => {
    expect(classesForActionButton({ variant: "cancel" })).toContain("text-status-critical/88");
    expect(classesForActionButton({ variant: "delete" })).toContain("text-status-error/88");
  });
});
