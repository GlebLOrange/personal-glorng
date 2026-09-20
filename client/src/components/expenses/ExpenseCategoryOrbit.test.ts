import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseCategoryOrbit from "@/components/expenses/ExpenseCategoryOrbit.vue";
import type { ExpenseSummary } from "@/types";

const formatMoney = (amount: string | number, currency: string): string =>
  `${amount} ${currency}`;

const sampleSummary: ExpenseSummary = {
  total: "100.00",
  currency: "PLN",
  rates_updated_at: null,
  by_month: [],
  by_tool: [],
  by_category: [
    { category: "Groceries", total: "50.00" },
    { category: "Transport", total: "20.00" },
    { category: "Misc", total: "5.00" },
  ],
};

describe("ExpenseCategoryOrbit", () => {
  it("sizes planets by spend share buckets", () => {
    const wrapper = mount(ExpenseCategoryOrbit, {
      props: { summary: sampleSummary, formatMoney },
    });

    const buttons = wrapper.findAll('button[type="button"]');
    expect(buttons).toHaveLength(3);
    // Groceries 50% → lg, Transport 20% → md, Misc 5% → sm
    expect(buttons[0]!.classes()).toContain("size-14");
    expect(buttons[1]!.classes()).toContain("size-12");
    expect(buttons[2]!.classes()).toContain("size-11");
    expect(wrapper.text()).toContain("Groceries");
    expect(wrapper.text()).toContain("50%");
  });

  it("emits selectCategory on planet click", async () => {
    const wrapper = mount(ExpenseCategoryOrbit, {
      props: { summary: sampleSummary, formatMoney },
    });

    await wrapper.findAll('button[type="button"]')[0]!.trigger("click");
    expect(wrapper.emitted("selectCategory")?.[0]).toEqual(["Groceries"]);
  });

  it("shows empty copy only when framed", () => {
    const empty = mount(ExpenseCategoryOrbit, {
      props: { summary: null, formatMoney },
    });
    expect(empty.text()).not.toContain("No data available yet");

    const framed = mount(ExpenseCategoryOrbit, {
      props: { summary: null, formatMoney, framed: true },
      global: { stubs: { Card: { template: "<div><slot /></div>" } } },
    });
    expect(framed.text()).toContain("No data available yet");
  });
});
