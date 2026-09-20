import { mount, type VueWrapper } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";

type QuickAddProps = {
  loading: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  category: string;
  product: string;
  price: string;
  expenseDate: string;
  currency: "PLN";
  smartTextOpen: boolean;
  nameError: string | null;
  amountError: string | null;
  "onUpdate:category": (value: string) => void;
  "onUpdate:product": (value: string) => void;
  "onUpdate:price": (value: string) => void;
  "onUpdate:expenseDate": (value: string) => void;
  "onUpdate:currency": (value: string) => void;
  "onUpdate:smartTextOpen": (value: boolean) => void;
  "onUpdate:nameError": (value: string | null) => void;
  "onUpdate:amountError": (value: string | null) => void;
};

function mountQuickAdd(
  overrides: Partial<QuickAddProps> = {},
): VueWrapper {
  return mount(ExpenseQuickAdd, {
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
      smartTextOpen: false,
      "onUpdate:smartTextOpen": () => undefined,
      nameError: null,
      "onUpdate:nameError": () => undefined,
      amountError: null,
      "onUpdate:amountError": () => undefined,
      ...overrides,
    },
  });
}

describe("ExpenseQuickAdd", () => {
  it("exposes name, amount, optional category, and date fields", () => {
    const wrapper = mountQuickAdd();

    expect(wrapper.text()).toContain("quick add");
    expect(wrapper.text()).toContain("smart text");
    expect(wrapper.text()).toContain("goods or services?");
    expect(wrapper.text()).toContain("amount");
    expect(wrapper.text()).toContain("date");
    expect(wrapper.text()).toContain("category");
    expect(wrapper.text()).toContain("save");
    expect(wrapper.find("#expense-quick-add-panel").attributes("style") ?? "").not.toMatch(
      /display:\s*none/,
    );
    expect(wrapper.find("#expense-smart-text").attributes("style") ?? "").toMatch(
      /display:\s*none/,
    );
    const select = wrapper.find("select");
    expect(select.find('option[value=""]').exists()).toBe(true);
    expect(wrapper.find('input[type="date"]').element).toHaveProperty("value", "2026-09-20");
    expect(wrapper.find("datalist").exists()).toBe(false);
  });

  it("anchors product suggestions under the goods field", async () => {
    let product = "";
    const wrapper = mountQuickAdd({
      categoryOptions: ["Food"],
      productSuggestions: ["Cocoa", "test coffee", "bread"],
      product,
      "onUpdate:product": (value: string) => {
        product = value;
        void wrapper.setProps({ product: value });
      },
    });

    const nameInput = wrapper.get("#expense-quick-name");
    await nameInput.setValue("o");
    await nameInput.trigger("focus");

    const list = wrapper.get("#expense-product-suggestions");
    expect(list.attributes("role")).toBe("listbox");
    expect(list.text()).toContain("Cocoa");
    expect(list.text()).toContain("test coffee");
    expect(list.text()).not.toContain("bread");

    const options = list.findAll('[role="option"]');
    expect(options).toHaveLength(2);
    await options[0]!.trigger("mousedown");
    expect(product).toBe("Cocoa");
  });
});
