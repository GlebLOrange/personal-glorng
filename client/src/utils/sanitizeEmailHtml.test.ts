/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";

import { sanitizeEmailHtml } from "@/utils/sanitizeEmailHtml";

describe("sanitizeEmailHtml", () => {
  it("keeps safe email markup", () => {
    const html = "<h1>Hi</h1><p>Hello <strong>world</strong></p>";
    expect(sanitizeEmailHtml(html)).toContain("<p>Hello");
    expect(sanitizeEmailHtml(html)).toContain("<strong>world</strong>");
  });

  it("strips script tags and event handlers", () => {
    const dirty = '<p onclick="alert(1)">x</p><script>alert(1)</script>';
    const clean = sanitizeEmailHtml(dirty);
    expect(clean).not.toContain("<script");
    expect(clean).not.toContain("onclick");
  });

  it("blocks javascript: links", () => {
    const dirty = '<a href="javascript:alert(1)">click</a>';
    const clean = sanitizeEmailHtml(dirty);
    expect(clean).not.toContain("javascript:");
  });

  it("blocks data: URIs in links", () => {
    const dirty = '<a href="data:text/html,<script>alert(1)</script>">x</a>';
    const clean = sanitizeEmailHtml(dirty);
    expect(clean).not.toContain("data:");
  });

  it("strips nested forms", () => {
    const dirty = '<form action="/evil"><input name="x"></form><p>ok</p>';
    const clean = sanitizeEmailHtml(dirty);
    expect(clean).not.toContain("<form");
    expect(clean).toContain("ok");
  });

  it("adds rel noopener on safe https links including single-quoted href", () => {
    const doubleQuoted = sanitizeEmailHtml('<a href="https://example.com">link</a>');
    expect(doubleQuoted).toContain('rel="noopener noreferrer"');
    expect(doubleQuoted).toContain("https://example.com");

    const singleQuoted = sanitizeEmailHtml("<a href='https://example.com'>link</a>");
    expect(singleQuoted).toMatch(/rel="[^"]*noopener/);
    expect(singleQuoted).toMatch(/rel="[^"]*noreferrer/);
  });

  it("merges noopener into existing rel", () => {
    const clean = sanitizeEmailHtml('<a href="https://example.com" rel="nofollow">link</a>');
    expect(clean).toMatch(/rel="[^"]*nofollow/);
    expect(clean).toMatch(/rel="[^"]*noopener/);
    expect(clean).toMatch(/rel="[^"]*noreferrer/);
  });

  it("stays correct under concurrent sanitize calls", async () => {
    const dirty = '<a href="https://example.com">link</a><script>x</script>';
    const results = await Promise.all(
      Array.from({ length: 20 }, () => Promise.resolve(sanitizeEmailHtml(dirty))),
    );
    for (const clean of results) {
      expect(clean).not.toContain("<script");
      expect(clean).toMatch(/rel="[^"]*noopener/);
      expect(clean).toMatch(/rel="[^"]*noreferrer/);
    }
  });
});
