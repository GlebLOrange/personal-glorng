import { describe, expect, it } from "vitest";

import {
  classesForActionButton,
  httpFamilyForSemanticAction,
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
    expect(httpFamilyForSemanticAction("delete")).toBe("4xx");
  });

  it("paints create/add like solid primary (1xx)", () => {
    for (const variant of ["create", "add"] as const) {
      const classes = classesForActionButton({ variant });
      expect(classes).toContain("bg-accent-blue");
      expect(classes).toContain("text-on-accent");
    }
  });

  it("paints save and success alias as 2xx wash", () => {
    expect(classesForActionButton({ variant: "save" })).toContain("text-status-success");
    expect(classesForActionButton({ variant: "success" })).toContain("text-status-success");
  });

  it("paints cancel as 5xx and delete as 4xx", () => {
    expect(classesForActionButton({ variant: "cancel" })).toContain("text-status-critical");
    expect(classesForActionButton({ variant: "delete" })).toContain("text-status-error");
  });
});
