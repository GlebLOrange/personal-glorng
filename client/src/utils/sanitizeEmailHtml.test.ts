/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";

import { addLinkRelAttributes, sanitizeEmailHtml } from "@/utils/sanitizeEmailHtml";

describe("addLinkRelAttributes", () => {
  it("adds rel noopener on links without rel", () => {
    const html = '<a href="https://example.com">link</a>';
    expect(addLinkRelAttributes(html)).toContain('rel="noopener noreferrer"');
  });

  it("does not duplicate rel when already set", () => {
    const html = '<a href="https://example.com" rel="nofollow">link</a>';
    expect(addLinkRelAttributes(html)).toBe(html);
  });
});

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

  it("adds rel noopener on safe https links", () => {
    const html = '<a href="https://example.com">link</a>';
    const clean = sanitizeEmailHtml(html);
    expect(clean).toContain('rel="noopener noreferrer"');
    expect(clean).toContain("https://example.com");
  });
});
