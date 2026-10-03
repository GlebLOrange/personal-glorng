import { mount, flushPromises } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import HeroBlock from "@/components/resume/HeroBlock.vue";
import type { ContactLink } from "@/constants/contactMeta";

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

const contactLinks: ContactLink[] = [
  { id: "email", label: "email", href: "mailto:test@example.com" },
  { id: "telegram", label: "telegram", href: "https://t.me/example" },
  { id: "github", label: "github", href: "https://github.com/example" },
];

describe("HeroBlock", () => {
  beforeEach(() => {
    toast.mockReset();
    apiGet.mockReset();
  });

  it("keeps bio out of the hero and shows email/telegram chips only", () => {
    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Python Backend / FastAPI Engineer",
        tagline: "I build production APIs",
        contactLinks,
      },
    });

    expect(wrapper.text()).toContain("I build production APIs");
    expect(wrapper.text()).not.toContain("Backend-first");
    expect(wrapper.text()).toContain("email");
    expect(wrapper.text()).toContain("telegram");
    expect(wrapper.text()).not.toContain("github");
  });

  it("offers print fallback instead of auto-printing when PDF fails", async () => {
    window.print = window.print ?? (() => {});
    const printSpy = vi.spyOn(window, "print").mockImplementation(() => {});
    apiGet.mockRejectedValue(new Error("network"));

    const wrapper = mount(HeroBlock, {
      props: {
        name: "Gleb.Y",
        title: "Engineer",
        contactLinks,
      },
    });

    await wrapper.get("button.cta-secondary").trigger("click");
    await flushPromises();

    expect(printSpy).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalled();
    expect(wrapper.text()).toContain("print page instead");

    const printBtn = wrapper
      .findAll("button")
      .find((b) => b.text().includes("print page instead"));
    expect(printBtn).toBeTruthy();
    await printBtn!.trigger("click");
    expect(printSpy).toHaveBeenCalledTimes(1);

    printSpy.mockRestore();
  });
});
