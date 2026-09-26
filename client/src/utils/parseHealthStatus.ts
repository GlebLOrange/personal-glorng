export type HealthUiStatus = "ok" | "unexpected" | "unreachable";

export function parseHealthStatusPayload(data: unknown): HealthUiStatus {
  if (data && typeof data === "object" && "status" in data) {
    const status = (data as { status: unknown }).status;
    if (status === "ok") {
      return "ok";
    }
    return "unexpected";
  }
  return "unexpected";
}
