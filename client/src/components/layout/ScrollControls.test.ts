import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import ScrollControls from "@/components/layout/ScrollControls.vue";

const showArrowDown = ref(false);
vi.mock("@/composables/useScrollProgress", () => ({
  useScrollProgress: () => ({ showArrowDown, showToTop: ref(false) }),
}));
vi.mock("@/composables/useNextSectionScroll", () => ({
  useNextSectionScroll: () => ({ scrollToNextSection: vi.fn(), scrollToTop: vi.fn() }),
}));

const stubs = {
  IconActionButton: { template: '<button v-bind="$attrs"><slot /></button>' },
  ScrollArrowIcon: true,
};

afterEach(() => {
  showArrowDown.value = false;
});

describe("ScrollControls", () => {
  it("renders scroll-to-next on the bottom-[8%] band without Back", () => {
    showArrowDown.value = true;
    const wrapper = mount(ScrollControls, { global: { stubs } });
    const btn = wrapper.get('[aria-label="scroll to next section"]');
    expect(btn.element.closest(".bottom-\\[8\\%\\]")).not.toBeNull();
    expect(wrapper.find('[aria-label="back"]').exists()).toBe(false);
  });

  it("renders nothing when there is no next section", () => {
    const wrapper = mount(ScrollControls, { global: { stubs } });
    expect(wrapper.find('[aria-label="scroll to next section"]').exists()).toBe(false);
  });
});
