import type { Page } from "@playwright/test";

const adminEmail = process.env.E2E_EMAIL ?? "admin@glorng.dev";
const adminPassword = process.env.E2E_PASSWORD ?? "MyTestPass123!";

export async function loginAsAdmin(page: Page): Promise<void> {
  await page.goto("/login");
  await page.getByPlaceholder("you@example.com").fill(adminEmail);
  await page.getByPlaceholder("••••••••••••").fill(adminPassword);
  await page.getByRole("button", { name: /^login$/i }).click();
  await page.waitForURL((url) => !url.pathname.startsWith("/login"), { timeout: 10_000 });
}
