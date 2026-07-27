import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "@/types/api";

describe("getApiErrorMessage", () => {
  it("lowercases generic axios request-failed messages", () => {
    expect(getApiErrorMessage(new Error("Request failed with status code 504"))).toBe(
      "request failed with status code 504",
    );
  });

  it("keeps custom api detail messages unchanged", () => {
    expect(
      getApiErrorMessage(
        {
          response: {
            data: {
              detail: "Superuser access required",
            },
          },
        },
        "Request failed",
      ),
    ).toBe("Superuser access required");
  });
});
