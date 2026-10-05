export type HealthUiStatus = "ok" | "unexpected";

export function parseHealthStatusPayload(data: unknown): HealthUiStatus {
  if (typeof data === "object" && data !== null && "status" in data && data.status === "ok") {
    return "ok";
  }
  return "unexpected";
}
