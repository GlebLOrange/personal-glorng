import { describe, expect, it } from "vitest";

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("expenses bootstrap deferrals", () => {
  it("boots list+summary first without waiting on previous summary or rates", () => {
    const source = readFileSync(
      resolve(__dirname, "./useExpenseSummary.ts"),
      "utf8",
    );
    expect(source).toMatch(/async function bootstrapListAndSummary/);
    expect(source).toMatch(
      /await Promise\.all\(\[loadExpenses\(\), loadSummary\(\)\]\)/,
    );
    expect(source).toMatch(/void loadPreviousSummary\(\)/);
    expect(source).toMatch(/void loadRates\(\)/);
  });

  it("useExpensesTool mounts via bootstrapListAndSummary, not reloadListAndSummary", () => {
    const source = readFileSync(resolve(__dirname, "./useExpensesTool.ts"), "utf8");
    const mountBlock = source.slice(source.indexOf("onMounted("));
    expect(mountBlock).toMatch(/bootstrapListAndSummary\(\)/);
    expect(mountBlock).not.toMatch(/transactions\.loadRates\(/);
    expect(mountBlock).not.toMatch(/reloadListAndSummary\(/);
  });
});
