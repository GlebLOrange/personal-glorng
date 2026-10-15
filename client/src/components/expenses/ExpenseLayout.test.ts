import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import type { ExpenseSummary } from "@/types";

const expensesToolSource = readFileSync(
  resolve(__dirname, "../../pages/admin/tools/ExpensesTool.vue"),
  "utf8",
);

const sampleSummary: ExpenseSummary = {
  total: "120.00",
  currency: "PLN",
  rates_updated_at: null,
  by_month: [],
  by_tool: [],
  by_category: [
    { category: "Food", total: "80.00" },
    { category: "Transport", total: "40.00" },
  ],
};

describe("expenses layout restore", () => {
  it("keeps five tabs above the dashboard with export in the tab end slot", () => {
    const tabIdx = expensesToolSource.indexOf("<AdminTabBar");
    const endSlotIdx = expensesToolSource.indexOf("#end");
    const exportIdx = expensesToolSource.indexOf("export csv");
    const dashboardIdx = expensesToolSource.indexOf("<ExpenseDashboardPanel");
    const activityIdx = expensesToolSource.indexOf("<ExpenseTransactionsPanel");
    const insightsIdx = expensesToolSource.indexOf('id="expenses-tab-panel-insights"');
    const categoriesIdx = expensesToolSource.indexOf('id="expenses-tab-panel-categories"');
    const converterIdx = expensesToolSource.indexOf('id="expenses-tab-panel-converter"');
    expect(tabIdx).toBeGreaterThan(-1);
    expect(endSlotIdx).toBeGreaterThan(tabIdx);
    expect(exportIdx).toBeGreaterThan(endSlotIdx);
    expect(dashboardIdx).toBeGreaterThan(exportIdx);
    expect(activityIdx).toBeGreaterThan(dashboardIdx);
    expect(insightsIdx).toBeGreaterThan(activityIdx);
    expect(categoriesIdx).toBeGreaterThan(insightsIdx);
    expect(converterIdx).toBeGreaterThan(categoriesIdx);
    expect(expensesToolSource).toMatch(/activeTab === 'today'/);
    expect(expensesToolSource).toMatch(/activeTab === 'activity'/);
    expect(expensesToolSource).toMatch(/activeTab === 'insights'/);
    expect(expensesToolSource).toMatch(/activeTab === 'categories'/);
    expect(expensesToolSource).toMatch(/activeTab === 'converter'/);
    expect(expensesToolSource).not.toMatch(/expenses-tab-panel-currency/);
    expect(expensesToolSource).not.toMatch(/activeTab === 'currency'/);
    expect(expensesToolSource).not.toMatch(/BaseDropdownMenu/);
    expect(expensesToolSource).not.toMatch(/openOverflow/);
    expect(expensesToolSource).not.toMatch(/expense settings/);
    expect(expensesToolSource).not.toMatch(/ExpenseOrbitNav/);
    expect(expensesToolSource).not.toMatch(/openCategoryTransactions/);
    expect(expensesToolSource).not.toMatch(/<footer/);
    expect(expensesToolSource).not.toMatch(/\+ expense/);
  });

  it("keeps the converter mounted after first open as a tab panel", () => {
    expect(expensesToolSource).toMatch(/converterMounted/);
    expect(expensesToolSource).toMatch(/activeTab === 'converter'/);
    expect(expensesToolSource).toMatch(/ExpenseCalculatorTab/);
    expect(expensesToolSource).not.toMatch(/overflowPanel/);
    expect(expensesToolSource).not.toMatch(/BaseDrawer/);
  });

  it("defers calculator composable and category settings until those surfaces", () => {
    expect(expensesToolSource).not.toMatch(/useExpenseCalculator\(/);
    expect(expensesToolSource).toMatch(
      /defineAsyncComponent\(\s*\(\)\s*=>\s*import\("@\/components\/expenses\/ExpenseCalculatorTab\.vue"\)/,
    );
    expect(expensesToolSource).toMatch(
      /defineAsyncComponent\(\s*\(\)\s*=>\s*import\("@\/components\/expenses\/ExpenseCategorySettings\.vue"\)/,
    );
  });

  it("renders period, total, and clickable activity count in one summary card", async () => {
    const wrapper = mount(ExpenseLedgerHeader, {
      props: {
        monthLabel: "September 2026",
        summary: sampleSummary,
        expenseTotal: 12,
        summaryError: null,
        ratesError: null,
      },
      global: {
        stubs: {
          RefreshIcon: true,
          BaseButton: true,
        },
      },
    });

    expect(wrapper.text()).toContain("Spent on");
    expect(wrapper.text()).toContain("September 2026");
    expect(wrapper.text()).toContain("total");
    expect(wrapper.text()).toContain("120.00 PLN");
    expect(wrapper.text()).toContain("activity · 12");
    expect(wrapper.text()).not.toContain("Top Category");

    const activityButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("activity · 12"));
    expect(activityButton).toBeTruthy();
    await activityButton!.trigger("click");
    expect(wrapper.emitted("openActivity")).toHaveLength(1);
  });

  it("keeps the period summary inside a single compact card", () => {
    const wrapper = mount(ExpenseLedgerHeader, {
      props: {
        monthLabel: "this month",
        summary: null,
        expenseTotal: 0,
        summaryError: null,
        ratesError: null,
      },
      global: {
        stubs: {
          RefreshIcon: true,
          BaseButton: true,
        },
      },
    });

    expect(wrapper.find("section[aria-label='expense period summary']").exists()).toBe(true);
    expect(wrapper.text()).toContain("Spent on");
    expect(wrapper.text()).toContain("this month");
  });
});
