import { describe, expect, it } from "vitest";

import { parseSseEvents, normalizeStreamError } from "./useSearchChat";

describe("parseSseEvents", () => {
  it("parses complete SSE frames", () => {
    const buffer = 'data: {"delta":"Hi"}\n\n' + 'data: {"done":true}\n\n';
    const { events, rest } = parseSseEvents(buffer);
    expect(events).toEqual([{ delta: "Hi" }, { done: true }]);
    expect(rest).toBe("");
  });

  it("keeps trailing partial frame in rest buffer", () => {
    const buffer = 'data: {"delta":"Hi"}\n\ndata: {"delta":" there';
    const { events, rest } = parseSseEvents(buffer);
    expect(events).toEqual([{ delta: "Hi" }]);
    expect(rest).toBe('data: {"delta":" there');
  });

  it("ignores malformed JSON chunks", () => {
    const buffer = "data: not-json\n\n" + 'data: {"delta":"ok"}\n\n';
    const { events, rest } = parseSseEvents(buffer);
    expect(events).toEqual([{ delta: "ok" }]);
    expect(rest).toBe("");
  });
});

describe("normalizeStreamError", () => {
  it("maps app rate limit errors for admin chat", () => {
    expect(
      normalizeStreamError("Too many requests. Please try again later.", "/api/tools/ai-chat"),
    ).toBe("You're sending messages too quickly — wait a few minutes");
  });

  it("preserves Gemini retry-after seconds in quota errors", () => {
    expect(
      normalizeStreamError(
        "Google Gemini quota exceeded — try again in ~60s",
        "/api/tools/ai-chat",
      ),
    ).toBe(
      "Google API quota reached — try again in ~60s, or check usage in Google AI Studio",
    );
  });

  it("uses generic quota message when server omits retry-after", () => {
    expect(
      normalizeStreamError("Google Gemini quota exceeded — try again shortly", "/api/tools/ai-chat"),
    ).toBe(
      "Google API quota reached — wait a minute and try again, or check usage in Google AI Studio",
    );
  });
});
