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

  it("uses the role as the page heading and keeps bio out of the hero", () => {
    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Python Backend / FastAPI Engineer",
        tagline: "I build production APIs",
      },
    });

    expect(wrapper.get("h1").text()).toBe("Python Backend / FastAPI Engineer");
    expect(wrapper.text()).toContain("Gleb.Y");
    expect(wrapper.text()).toContain("I build production APIs");
    expect(wrapper.find("img").exists()).toBe(false);
    expect(wrapper.find(".accent-gradient").exists()).toBe(false);
    expect(wrapper.find(".portfolio-link-rail").exists()).toBe(false);
    expect(wrapper.find(".contact-link-chip").exists()).toBe(false);
    expect(wrapper.text()).not.toContain("email");
    expect(wrapper.text()).not.toContain("telegram");
  });

  it("centers the status-rail layout and shows the sample note", () => {
    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Python Backend / FastAPI Engineer",
        tagline: "I build production APIs",
        location: "Wrocław, Poland",
        availability: "open to full-time and contract (remote)",
        sampleNote: "this site is the sample",
        layout: "status-rail",
      },
    });

    expect(wrapper.get("div.py-12").classes()).toContain("text-center");
    expect(wrapper.text()).toContain("this site is the sample");
    expect(wrapper.text()).not.toContain("I build production APIs");
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
