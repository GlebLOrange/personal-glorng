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
    { category: "Groceries", total: "80.00" },
    { category: "Transport", total: "40.00" },
  ],
};

describe("expenses layout restore", () => {
  it("keeps tabs above the dashboard with export in the tab end slot", () => {
    const tabIdx = expensesToolSource.indexOf("<AdminTabBar");
    const endSlotIdx = expensesToolSource.indexOf("#end");
    const exportIdx = expensesToolSource.indexOf("export csv");
    const dashboardIdx = expensesToolSource.indexOf("<ExpenseDashboardPanel");
    const transactionsIdx = expensesToolSource.indexOf("<ExpenseTransactionsPanel");
    const analyticsIdx = expensesToolSource.indexOf('id="expenses-tab-panel-analytics"');
    expect(tabIdx).toBeGreaterThan(-1);
    expect(endSlotIdx).toBeGreaterThan(tabIdx);
    expect(exportIdx).toBeGreaterThan(endSlotIdx);
    expect(dashboardIdx).toBeGreaterThan(exportIdx);
    expect(transactionsIdx).toBeGreaterThan(dashboardIdx);
    expect(analyticsIdx).toBeGreaterThan(transactionsIdx);
    expect(expensesToolSource).toMatch(/activeTab === 'transactions'/);
    expect(expensesToolSource).toMatch(/activeTab === 'breakdown'/);
    expect(expensesToolSource).toMatch(/activeTab === 'analytics'/);
    expect(expensesToolSource).toMatch(/ExpenseCategoryBreakdown/);
    expect(expensesToolSource).toMatch(/id="expenses-tab-panel-breakdown"/);
    expect(expensesToolSource).not.toMatch(/ExpenseOrbitNav/);
    expect(expensesToolSource).not.toMatch(/openCategoryTransactions/);
    expect(expensesToolSource).not.toMatch(/<footer/);
    expect(expensesToolSource).not.toMatch(/>\s*settings\s*</);
    expect(expensesToolSource).not.toMatch(/\+ expense/);
  });

  it("keeps the converter mounted after first visit", () => {
    expect(expensesToolSource).toMatch(/converterMounted/);
    expect(expensesToolSource).toMatch(/v-show="activeTab === 'converter'"/);
  });

  it("defers calculator composable and category settings until those tabs", () => {
    expect(expensesToolSource).not.toMatch(/useExpenseCalculator\(/);
    expect(expensesToolSource).toMatch(
      /defineAsyncComponent\(\s*\(\)\s*=>\s*import\("@\/components\/expenses\/ExpenseCalculatorTab\.vue"\)/,
    );
    expect(expensesToolSource).toMatch(
      /defineAsyncComponent\(\s*\(\)\s*=>\s*import\("@\/components\/expenses\/ExpenseCategorySettings\.vue"\)/,
    );
  });

  it("renders period, total, and clickable transaction count in one summary card", async () => {
    const wrapper = mount(ExpenseLedgerHeader, {
      props: {
        monthPreset: "this_month",
        "onUpdate:monthPreset": () => undefined,
        dateFilterMode: "month",
        "onUpdate:dateFilterMode": () => undefined,
        selectedMonth: "2026-09",
        "onUpdate:selectedMonth": () => undefined,
        dateFrom: "",
        "onUpdate:dateFrom": () => undefined,
        dateTo: "",
        "onUpdate:dateTo": () => undefined,
        monthLabel: "September 2026",
        hasActiveFilters: false,
        rangeError: null,
        summary: sampleSummary,
        expenseTotal: 12,
        summaryError: null,
        ratesError: null,
      },
      global: {
        stubs: {
          ExpenseDateFilters: true,
          RefreshIcon: true,
          BaseButton: true,
        },
      },
    });

    expect(wrapper.text()).toContain("Spent on");
    expect(wrapper.text()).toContain("September 2026");
    expect(wrapper.text()).toContain("total");
    expect(wrapper.text()).toContain("120.00 PLN");
    expect(wrapper.text()).toContain("transactions · 12");
    expect(wrapper.text()).not.toContain("Top Category");

    const txButton = wrapper
      .findAll("button")
      .find((btn) => btn.text().includes("transactions · 12"));
    expect(txButton).toBeTruthy();
    await txButton!.trigger("click");
    expect(wrapper.emitted("openTransactions")).toHaveLength(1);
  });

  it("keeps the period summary inside a single compact card", () => {
    const wrapper = mount(ExpenseLedgerHeader, {
      props: {
        monthPreset: "this_month",
        "onUpdate:monthPreset": () => undefined,
        dateFilterMode: "month",
        "onUpdate:dateFilterMode": () => undefined,
        selectedMonth: "2026-09",
        "onUpdate:selectedMonth": () => undefined,
        dateFrom: "",
        "onUpdate:dateFrom": () => undefined,
        dateTo: "",
        "onUpdate:dateTo": () => undefined,
        monthLabel: "this month",
        hasActiveFilters: false,
        rangeError: null,
        summary: null,
        expenseTotal: 0,
        summaryError: null,
        ratesError: null,
      },
      global: {
        stubs: {
          ExpenseDateFilters: true,
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
