/**
 * @vitest-environment happy-dom
 */
import { afterEach, describe, expect, it } from "vitest";

import {
  EMAIL_DRAFT_STORAGE_KEY,
  consumeEmailDraft,
  parseEmailDraft,
  writeEmailDraft,
} from "@/utils/emailDraft";

afterEach(() => {
  sessionStorage.clear();
});

describe("parseEmailDraft", () => {
  it("accepts a valid draft shape", () => {
    expect(parseEmailDraft({ to: "a@b.c", subject: "Hi", body: "Body" })).toEqual({
      to: "a@b.c",
      subject: "Hi",
      body: "Body",
    });
  });

  it("rejects invalid payloads", () => {
    expect(parseEmailDraft(null)).toBeNull();
    expect(parseEmailDraft({ to: "a@b.c", subject: "Hi" })).toBeNull();
    expect(parseEmailDraft({ to: 1, subject: "Hi", body: "Body" })).toBeNull();
  });
});

describe("writeEmailDraft / consumeEmailDraft", () => {
  it("round-trips and clears storage", () => {
    writeEmailDraft({ to: "a@b.c", subject: "Re: theme", body: "\n\n--- Original ---\nmsg" });
    expect(sessionStorage.getItem(EMAIL_DRAFT_STORAGE_KEY)).toBeTruthy();

    const draft = consumeEmailDraft();
    expect(draft).toEqual({
      to: "a@b.c",
      subject: "Re: theme",
      body: "\n\n--- Original ---\nmsg",
    });
    expect(sessionStorage.getItem(EMAIL_DRAFT_STORAGE_KEY)).toBeNull();
    expect(consumeEmailDraft()).toBeNull();
  });

  it("returns null for corrupt JSON", () => {
    sessionStorage.setItem(EMAIL_DRAFT_STORAGE_KEY, "{not-json");
    expect(consumeEmailDraft()).toBeNull();
    expect(sessionStorage.getItem(EMAIL_DRAFT_STORAGE_KEY)).toBeNull();
  });
});
