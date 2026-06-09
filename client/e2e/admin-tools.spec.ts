import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "./helpers/auth";

test.describe("admin tools", () => {
  test("create task appears in queue after login", async ({ page }) => {
    const uniqueTitle = `E2E task ${Date.now()}`;
    await loginAsAdmin(page);

    await page.goto("/admin/tools/tasks");
    await expect(page.getByRole("heading", { name: /^tasks$/i })).toBeVisible();

    await page.getByRole("button", { name: /\+ new task/i }).click();
    await expect(page.getByRole("heading", { name: /new task/i })).toBeVisible();

    await page.getByPlaceholder("What needs doing?").fill(uniqueTitle);
    await page.getByLabel("Scheduled at").fill("2026-12-15T10:00");
    await page.getByRole("button", { name: /^create$/i }).click();

    await expect(page.getByText(uniqueTitle)).toBeVisible({ timeout: 10_000 });
  });

  test("audit log shows login success after admin login", async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto("/admin/tools/audit");
    await expect(page.getByRole("heading", { name: /audit log/i })).toBeVisible();

    await page.getByPlaceholder("e.g. auth.login_success").fill("auth.login_success");
    await page.getByRole("button", { name: /^filter$/i }).click();

    await expect(page.getByText("auth.login_success")).toBeVisible({ timeout: 10_000 });
  });

  test("app logs page shows persisted entries after API traffic", async ({ page }) => {
    await loginAsAdmin(page);

    await page.evaluate(async () => {
      await fetch("/api/resume");
      await fetch("/api/platform/services");
    });

    await page.goto("/admin/tools/app-logs");
    await expect(page.getByRole("heading", { name: /app logs/i })).toBeVisible();

    await expect
      .poll(
        async () => {
          const totalLine = page.getByText(/\d+ entries total/);
          if ((await totalLine.count()) === 0) {
            return 0;
          }
          const match = (await totalLine.first().textContent())?.match(/(\d+)/);
          return match ? Number.parseInt(match[1], 10) : 0;
        },
        { timeout: 15_000 },
      )
      .toBeGreaterThan(0);
  });
});
