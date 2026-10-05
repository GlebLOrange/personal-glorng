import { expect, test } from "@playwright/test";

/**
 * Built-shell smoke: vite preview only, no API/Docker.
 * Catches entry-chunk breakage (e.g. forced axios/vue shared chunks).
 */
test.describe("built shell", () => {
  test("home paints nav and has no page error", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (err) => {
      pageErrors.push(err.message);
    });

    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.locator("#app")).not.toBeEmpty();
    await expect(page.getByRole("navigation").first()).toBeVisible();
    expect(pageErrors, `page errors: ${pageErrors.join("; ")}`).toEqual([]);
  });
});
