import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import ExpenseCurrencyConverter from "@/components/expenses/ExpenseCurrencyConverter.vue";

const { postMock, toastMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
  toastMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: postMock },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: toastMock }),
}));

describe("ExpenseCurrencyConverter", () => {
  it("toasts when conversion fails", async () => {
    postMock.mockRejectedValue(new Error("rate unavailable"));

    const wrapper = mount(ExpenseCurrencyConverter, {
      props: {
        exchangeRates: {
          base: "USD",
          rates: { PLN: "3.64", EUR: "0.92", USD: "1", BYN: "3.2" },
          updated_at: "2026-06-07T00:00:00Z",
          provider: "test",
        },
      },
    });

    const convertBtn = wrapper.find("button");
    await convertBtn.trigger("click");

    await vi.waitFor(() => expect(toastMock).toHaveBeenCalledWith("rate unavailable", "error"));
  });
});
