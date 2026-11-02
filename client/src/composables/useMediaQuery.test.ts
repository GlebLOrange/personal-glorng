import { mount } from "@vue/test-utils";
import { defineComponent, nextTick } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useMediaQuery } from "@/composables/useMediaQuery";

describe("useMediaQuery", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("tracks matchMedia and cleans up the listener", async () => {
    const listeners = new Set<(event: MediaQueryListEvent) => void>();
    const media = {
      matches: true,
      media: "(max-width: 767px)",
      addEventListener: vi.fn((_type: string, listener: (event: MediaQueryListEvent) => void) => {
        listeners.add(listener);
      }),
      removeEventListener: vi.fn((_type: string, listener: (event: MediaQueryListEvent) => void) => {
        listeners.delete(listener);
      }),
    };
    vi.stubGlobal(
      "matchMedia",
      vi.fn(() => media),
    );

    const Host = defineComponent({
      setup() {
        const isNarrow = useMediaQuery("(max-width: 767px)");
        return { isNarrow };
      },
      template: "<div>{{ isNarrow }}</div>",
    });
    const wrapper = mount(Host);
    await nextTick();
    expect(wrapper.text()).toBe("true");

    media.matches = false;
    for (const listener of listeners) {
      listener({ matches: false } as MediaQueryListEvent);
    }
    await nextTick();
    expect(wrapper.text()).toBe("false");

    wrapper.unmount();
    expect(media.removeEventListener).toHaveBeenCalled();
  });
});
