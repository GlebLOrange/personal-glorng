import { mount, flushPromises } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import HeroBlock from "@/components/resume/HeroBlock.vue";

const toast = vi.fn();
const apiGet = vi.fn();

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast }),
}));

vi.mock("@/composables/useApi", () => ({
  api: {
    get: (...args: unknown[]) => apiGet(...args),
  },
}));

describe("HeroBlock", () => {
  beforeEach(() => {
    toast.mockReset();
    apiGet.mockReset();
  });

  it("keeps bio out of the hero and does not show contact chips", () => {
    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Python Backend / FastAPI Engineer",
        tagline: "I build production APIs",
      },
    });

    expect(wrapper.text()).toContain("Gleb.Y");
    expect(wrapper.text()).toContain("I build production APIs");
    expect(wrapper.find("h1 .sr-only").exists()).toBe(false);
    expect(wrapper.text()).not.toContain("Backend-first");
    expect(wrapper.find(".contact-link-chip").exists()).toBe(false);
    expect(wrapper.text()).not.toContain("email");
    expect(wrapper.text()).not.toContain("telegram");
  });

  it("offers print fallback instead of auto-printing when PDF fails", async () => {
    window.print = window.print ?? (() => {});
    const printSpy = vi.spyOn(window, "print").mockImplementation(() => {});
    apiGet.mockRejectedValue(new Error("network"));

    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Engineer",
      },
    });

    await wrapper.get("button.cta-secondary").trigger("click");
    await flushPromises();

    expect(printSpy).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalled();
    expect(wrapper.text()).toContain("print page instead");

    const printBtn = wrapper.findAll("button").find((b) => b.text().includes("print page instead"));
    expect(printBtn).toBeTruthy();
    await printBtn!.trigger("click");
    expect(printSpy).toHaveBeenCalledTimes(1);

    printSpy.mockRestore();
  });
});
