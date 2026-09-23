import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseRow from "@/components/expenses/ExpenseRow.vue";
import type { Expense } from "@/types";

const sampleExpense: Expense = {
  id: 1,
  tool_name: "Lunch",
  amount: "20.00",
  currency: "EUR",
  category: "Groceries",
  expense_date: "2026-09-20",
  source: "web_admin",
  notes: null,
  created_at: "2026-09-20T12:00:00Z",
  updated_at: "2026-09-20T12:00:00Z",
};

const telegramExpense: Expense = {
  ...sampleExpense,
  id: 2,
  tool_name: "Coffee",
  source: "todobot",
  notes: "morning",
};

const formatMoney = (amount: string | number, currency: string) => `${currency} ${amount}`;
const formatExpenseDate = (iso: string) => iso.slice(0, 10);
const convertAmount = () => 0;
const noopSort = () => "none" as const;
const noopIndicator = () => "";

describe("ExpenseRow table layout", () => {
  it("hides default web source and empty notes clutter", () => {
    const wrapper = mount(ExpenseRow, {
      props: {
        expense: sampleExpense,
        layout: "table",
        displayCurrency: "EUR",
        exchangeRates: null,
        formatMoney,
        formatExpenseDate,
        convertAmount,
      },
    });

    expect(wrapper.text()).toContain("Lunch");
    expect(wrapper.text()).not.toContain("Web");
    expect(wrapper.text()).not.toMatch(/—/);
    expect(wrapper.find('[aria-label="duplicate Lunch"]').exists()).toBe(true);
    expect(wrapper.find('[aria-label="edit Lunch"]').exists()).toBe(true);
    expect(wrapper.find('[aria-label="delete Lunch"]').exists()).toBe(true);
  });

  it("surfaces notes and non-web source under the name", () => {
    const wrapper = mount(ExpenseRow, {
      props: {
        expense: telegramExpense,
        layout: "table",
        displayCurrency: "EUR",
        exchangeRates: null,
        formatMoney,
        formatExpenseDate,
        convertAmount,
      },
    });

    expect(wrapper.text()).toContain("Coffee");
    expect(wrapper.text()).toContain("morning");
    expect(wrapper.text()).toContain("Telegram");
  });
});

describe("ExpenseList desktop headers", () => {
  it("drops dedicated source and notes columns", () => {
    const wrapper = mount(ExpenseList, {
      props: {
        expenses: [sampleExpense],
        loading: false,
        monthLabel: "Sept 2026",
        displayCurrency: "EUR",
        exchangeRates: null,
        formatMoney,
        formatExpenseDate,
        convertAmount,
        sortIndicator: noopIndicator,
        sortAriaSort: noopSort,
      },
    });

    const headers = wrapper.findAll("th").map((th) => th.text().toLowerCase());
    expect(headers.some((h) => h.includes("date"))).toBe(true);
    expect(headers.some((h) => h.includes("name"))).toBe(true);
    expect(headers.some((h) => h.includes("source"))).toBe(false);
    expect(headers.some((h) => h.includes("notes"))).toBe(false);
  });
});
