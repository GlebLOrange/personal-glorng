import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import ScrollControls from "@/components/layout/ScrollControls.vue";
import { usePageBackTo } from "@/composables/usePageBackTo";

const showArrowDown = ref(false);
vi.mock("@/composables/useScrollProgress", () => ({
  useScrollProgress: () => ({ showArrowDown, showToTop: ref(false) }),
}));
vi.mock("@/composables/useNextSectionScroll", () => ({
  useNextSectionScroll: () => ({ scrollToNextSection: vi.fn(), scrollToTop: vi.fn() }),
}));

const stubs = {
  BackLink: { props: ["to"], template: '<a data-testid="back" :href="to" aria-label="back" />' },
  IconActionButton: { template: "<button v-bind=\"$attrs\"><slot /></button>" },
  ScrollArrowIcon: true,
};

afterEach(() => {
  usePageBackTo().backTo.value = undefined;
  showArrowDown.value = false;
});

describe("ScrollControls bottom rail", () => {
  it("puts Back and scroll-to-next on one bottom-[8%] band aligned with the shell", () => {
    usePageBackTo().backTo.value = "/admin";
    showArrowDown.value = true;
    const wrapper = mount(ScrollControls, { global: { stubs } });

    const rails = wrapper.findAll('[data-testid="page-bottom-rail"]');
    expect(rails).toHaveLength(1);
    const rail = rails[0]!;
    expect(rail.classes()).toEqual(expect.arrayContaining(["fixed", "bottom-[8%]", "inset-x-0"]));
    const inner = rail.element.firstElementChild as HTMLElement;
    expect(inner.className).toContain("max-w-5xl");
    expect(inner.className).toContain("px-6");
    expect(inner.className).toContain("h-11");
    expect(rail.get('[data-testid="back"]').attributes("href")).toBe("/admin");
    expect(rail.get('[aria-label="scroll to next section"]').exists()).toBe(true);
  });

  it("renders Back alone when there is nothing to scroll to", () => {
    usePageBackTo().backTo.value = "/tools";
    const wrapper = mount(ScrollControls, { global: { stubs } });
    expect(wrapper.find('[data-testid="back"]').exists()).toBe(true);
    expect(wrapper.find('[aria-label="scroll to next section"]').exists()).toBe(false);
  });

  it("omits the rail when there is no Back and no next section", () => {
    const wrapper = mount(ScrollControls, { global: { stubs } });
    expect(wrapper.find('[data-testid="page-bottom-rail"]').exists()).toBe(false);
  });
});
