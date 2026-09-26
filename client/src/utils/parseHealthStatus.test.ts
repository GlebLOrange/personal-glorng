import { describe, expect, it } from "vitest";

import { parseHealthStatusPayload } from "@/utils/parseHealthStatus";

describe("parseHealthStatusPayload", () => {
  it("returns ok for the liveness payload", () => {
    expect(parseHealthStatusPayload({ status: "ok" })).toBe("ok");
  });

  it("returns unexpected for other status values", () => {
    expect(parseHealthStatusPayload({ status: "degraded" })).toBe("unexpected");
  });

  it("returns unexpected for non-objects", () => {
    expect(parseHealthStatusPayload(null)).toBe("unexpected");
    expect(parseHealthStatusPayload("ok")).toBe("unexpected");
  });
});
