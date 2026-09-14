import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import type { ExpenseCategory, ExpenseSummary } from "@/types";

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

const sampleCategories: ExpenseCategory[] = [
  {
    id: 1,
    name: "Groceries",
    sort_order: 0,
    monthly_budget: "100.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Transport",
    sort_order: 1,
    monthly_budget: "50.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

describe("expenses layout restore", () => {
  it("keeps tabs above the period strip in ExpensesTool", () => {
    const tabIdx = expensesToolSource.indexOf("<AdminTabBar");
    const headerIdx = expensesToolSource.indexOf("<ExpenseLedgerHeader");
    expect(tabIdx).toBeGreaterThan(-1);
    expect(headerIdx).toBeGreaterThan(-1);
    expect(tabIdx).toBeLessThan(headerIdx);
  });

  it("renders KPI strip without category breakdown bars", () => {
    const wrapper = mount(ExpenseSummaryCard, {
      props: {
        summary: sampleSummary,
        monthLabel: "this month",
        expenseCategories: sampleCategories,
        periodChange: { delta: 5, increased: true },
        formatMoney: (amount: string | number, currency: string) => `${amount} ${currency}`,
      },
    });

    expect(wrapper.text()).toContain("total");
    expect(wrapper.text()).toContain("period change");
    expect(wrapper.text()).toContain("budget status");
    expect(wrapper.text()).toContain("120.00 PLN");
    // Category bars moved to Insights — not in the ledger KPI strip.
    expect(wrapper.text()).not.toContain("Groceries");
    expect(wrapper.text()).not.toContain("Transport");
    expect(wrapper.findAll('[role="progressbar"]')).toHaveLength(1);
  });

  it("flattens the period strip without a wrapping Card", () => {
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
        expenseCategories: [],
        periodChange: null,
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
    expect(wrapper.html()).not.toMatch(/class="[^"]*card/i);
  });
});
