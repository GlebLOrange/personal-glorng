import { describe, expect, it } from "vitest";

import { parseSseEvents } from "./useSearchChat";

describe("parseSseEvents", () => {
  it("parses complete SSE frames", () => {
    const buffer =
      'data: {"delta":"Hi"}\n\n' + 'data: {"done":true}\n\n';
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
