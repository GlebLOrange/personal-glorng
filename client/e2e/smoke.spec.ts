import { expect, test } from "@playwright/test";

const adminEmail = process.env.E2E_EMAIL ?? "admin@glorng.dev";
const adminPassword = process.env.E2E_PASSWORD ?? "MyTestPass123!";

test.describe("public pages", () => {
  test("portfolio page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /back to portfolio/i })).toHaveCount(0);
    await expect(page.locator("body")).toBeVisible();
  });

  test("login page shows form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /login/i })).toBeVisible();
    await expect(page.getByPlaceholder("admin@glorng.dev")).toBeVisible();
    await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
  });

  test("guest sees tools nav and public tools catalog", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /^tools$/i })).toBeVisible();

    await page.getByRole("link", { name: /^tools$/i }).click();
    await expect(page).toHaveURL(/\/tools$/);
    await expect(page.getByRole("heading", { name: /^tools$/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /^calculator$/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /^recipes$/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /url shortener/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /video download/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /date & time & location/i })).toBeVisible();
  });

  test("guest sees clocks bar on portfolio", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("complementary", { name: /date & time & location/i })).toBeVisible();
  });

  test("guest can use public calculator", async ({ page }) => {
    await page.goto("/calculator");
    await expect(page.getByRole("heading", { name: /^calculator$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "7" })).toBeVisible();
  });

  test("old calculator admin URL redirects to public route", async ({ page }) => {
    await page.goto("/admin/tools/calculator");
    await expect(page).toHaveURL(/\/calculator$/);
  });

  test("guest can open public recipes page", async ({ page }) => {
    await page.goto("/recipes");
    await expect(page.getByRole("heading", { name: /^recipes$/i })).toBeVisible();
  });

  test("guest can open public shortener page", async ({ page }) => {
    await page.goto("/shortener");
    await expect(page.getByRole("heading", { name: /url-shortener/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /shorten/i })).toBeVisible();
  });

  test("guest can open public video download page", async ({ page }) => {
    await page.goto("/vid-download");
    await expect(page.getByRole("heading", { name: /vid-download/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /download/i })).toBeVisible();
  });

  test("old admin tool URLs redirect to public routes", async ({ page }) => {
    await page.goto("/admin/tools/recipes");
    await expect(page).toHaveURL(/\/recipes$/);

    await page.goto("/admin/tools/url-shortener");
    await expect(page).toHaveURL(/\/shortener$/);

    await page.goto("/admin/tools/vid-download");
    await expect(page).toHaveURL(/\/vid-download$/);
  });

  test("guest can add a city on date-time page", async ({ page }) => {
    await page.goto("/time-date-weather-location");
    await expect(page.getByText(/\d+\/8 cities saved in your browser/i)).toBeVisible();
    await page.getByRole("textbox", { name: /search city to add/i }).fill("London");
    await page.getByRole("button", { name: /^add$/i }).click();
    await expect(page.getByText(/location added/i)).toBeVisible();
    await expect(page.getByRole("timer").first()).toHaveText(/\d{2}:\d{2}:\d{2}/);
  });
});

test.describe("auth guards", () => {
  test("admin redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/login/);
    expect(new URL(page.url()).searchParams.get("redirect")).toBe("/admin");
  });
});

test.describe("authenticated admin", () => {
  test("calculator tool loads after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("admin@glorng.dev").fill(adminEmail);
    await page.getByPlaceholder("••••••••").fill(adminPassword);
    await page.getByRole("button", { name: /^login$/i }).click();

    await page.goto("/calculator");
    await expect(page.getByRole("heading", { name: /^calculator$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "7" })).toBeVisible();
  });
});
