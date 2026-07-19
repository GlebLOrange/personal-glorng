import { describe, expect, it } from "vitest";

import { sourceFromUrl } from "./newsForms";

describe("sourceFromUrl", () => {
  it("derives a name from a normal feed host", () => {
    expect(sourceFromUrl("https://www.reuters.com/world/rss")).toBe("Reuters");
    expect(sourceFromUrl("https://feeds.bbci.co.uk/news/rss.xml")).toBe("BBC News");
    expect(sourceFromUrl("dw.com/rss/rss-en-all")).toBe("DW");
  });

  it("supports {{marker}} hosts", () => {
    expect(sourceFromUrl("https://{{the-guardian}}.com/rss")).toBe("The Guardian");
  });

  it("title-cases unknown hosts", () => {
    expect(sourceFromUrl("https://example-news.org/feed.xml")).toBe("Example News");
  });
});
