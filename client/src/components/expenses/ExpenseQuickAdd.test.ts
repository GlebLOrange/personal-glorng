import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";

describe("ExpenseQuickAdd", () => {
  it("exposes name, amount, optional category, and date fields", () => {
    const wrapper = mount(ExpenseQuickAdd, {
      props: {
        loading: false,
        categoryOptions: ["Food", "Transport"],
        productSuggestions: ["coffee"],
        category: "",
        "onUpdate:category": () => undefined,
        product: "",
        "onUpdate:product": () => undefined,
        price: "",
        "onUpdate:price": () => undefined,
        expenseDate: "2026-09-20",
        "onUpdate:expenseDate": () => undefined,
        currency: "PLN",
        "onUpdate:currency": () => undefined,
        nameError: null,
        "onUpdate:nameError": () => undefined,
        amountError: null,
        "onUpdate:amountError": () => undefined,
      },
    });

    expect(wrapper.text()).toContain("name");
    expect(wrapper.text()).toContain("amount");
    expect(wrapper.text()).toContain("date");
    expect(wrapper.text()).toContain("category");
    const select = wrapper.find("select");
    expect(select.find('option[value=""]').exists()).toBe(true);
    expect(wrapper.find('input[type="date"]').element).toHaveProperty("value", "2026-09-20");
  });
});
