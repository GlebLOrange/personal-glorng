import { expect, test } from "@playwright/test";

test.describe("portfolio contact journey", () => {
  test("mobile hero CTA opens a usable inquiry dialog on the first click", async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await page.getByRole("button", { name: /get in touch/i }).click();

    const dialog = page.getByRole("dialog", { name: /get in touch/i });
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("textbox", { name: /email/i })).toBeVisible();
    await expect(dialog.getByRole("textbox", { name: /subject/i })).toHaveValue("work inquiry");
    await expect(dialog.getByRole("textbox", { name: /message/i })).toBeVisible();
    await expect(dialog.getByRole("button", { name: /send inquiry/i })).toBeDisabled();

    // Attach a current viewport capture alongside the round-2 persona screenshots.
    await testInfo.attach("mobile-contact-dialog-current", {
      body: await page.screenshot(),
      contentType: "image/png",
    });
  });

  test("mobile contact-section inquiry CTA opens the dialog after scrolling", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.locator("#contacts").scrollIntoViewIfNeeded();

    await page.getByRole("button", { name: /send inquiry/i }).click();

    await expect(page.getByRole("dialog", { name: /get in touch/i })).toBeVisible();
  });

  test("invalid email keeps send disabled and displays validation feedback", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.getByRole("button", { name: /get in touch/i }).click();

    const dialog = page.getByRole("dialog", { name: /get in touch/i });
    const email = dialog.getByRole("textbox", { name: /email/i });
    await email.fill("not-an-email");

    await expect(dialog.getByRole("alert")).toContainText(/full address like name@example\.com/i);
    await expect(dialog.getByRole("button", { name: /send inquiry/i })).toBeDisabled();
  });

  test("valid inquiry draft becomes submittable without sending it", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.getByRole("button", { name: /get in touch/i }).click();

    const dialog = page.getByRole("dialog", { name: /get in touch/i });
    await dialog.getByRole("textbox", { name: /email/i }).fill("qa@example.test");
    await dialog.getByRole("textbox", { name: /message/i }).fill("QA draft only; do not submit.");

    await expect(dialog.getByRole("button", { name: /send inquiry/i })).toBeEnabled();
  });
});
