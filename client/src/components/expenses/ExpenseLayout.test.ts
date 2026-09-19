import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
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
  it("keeps tabs above the dashboard panel and footer export/settings", () => {
    const tabIdx = expensesToolSource.indexOf("<AdminTabBar");
    const dashboardIdx = expensesToolSource.indexOf("<ExpenseDashboardPanel");
    const footerIdx = expensesToolSource.indexOf("<footer");
    const exportIdx = expensesToolSource.indexOf("export csv");
    const settingsIdx = expensesToolSource.indexOf("settings");
    expect(tabIdx).toBeGreaterThan(-1);
    expect(dashboardIdx).toBeGreaterThan(-1);
    expect(footerIdx).toBeGreaterThan(-1);
    expect(tabIdx).toBeLessThan(dashboardIdx);
    expect(dashboardIdx).toBeLessThan(footerIdx);
    expect(exportIdx).toBeGreaterThan(footerIdx);
    expect(settingsIdx).toBeGreaterThan(footerIdx);
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

  it("renders a single total with transaction count", () => {
    const wrapper = mount(ExpenseSummaryCard, {
      props: {
        summary: sampleSummary,
        expenseTotal: 12,
        formatMoney: (amount: string | number, currency: string) => `${amount} ${currency}`,
      },
    });

    expect(wrapper.text()).toContain("Total");
    expect(wrapper.text()).toContain("120.00 PLN");
    expect(wrapper.text()).toContain("12 transactions");
    expect(wrapper.text()).not.toContain("Top Category");
  });

  it("flattens the period strip without a wrapping Card on the section", () => {
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
        formatMoney: (amount: string | number, currency: string) => `${amount} ${currency}`,
        summaryError: null,
        ratesError: null,
      },
      global: {
        stubs: {
          ExpenseDateFilters: true,
          ExpenseSummaryCard: true,
          RefreshIcon: true,
          BaseButton: true,
        },
      },
    });

    expect(wrapper.find("section[aria-label='expense period summary']").exists()).toBe(true);
    expect(wrapper.text()).toContain("Expenses");
    expect(wrapper.html()).not.toMatch(/class="[^"]*card/i);
  });
});
