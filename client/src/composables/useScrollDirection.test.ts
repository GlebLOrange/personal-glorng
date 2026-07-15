import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import { defineComponent, nextTick } from "vue";

import { useScrollDirection } from "@/composables/useScrollDirection";

function mountHarness(options?: Parameters<typeof useScrollDirection>[0]) {
  let api: ReturnType<typeof useScrollDirection> | null = null;

  const Harness = defineComponent({
    setup() {
      api = useScrollDirection(options);
      return () => null;
    },
  });

  const wrapper = mount(Harness);
  return { wrapper, getApi: () => api! };
}

describe("useScrollDirection", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("show() forces header visible", () => {
    const { getApi } = mountHarness();
    getApi().isHidden.value = true;
    getApi().show();
    expect(getApi().isHidden.value).toBe(false);
  });

  it("does not hide when disabled", async () => {
    let scrollHandler: (() => void) | undefined;
    vi.spyOn(window, "addEventListener").mockImplementation((type, listener) => {
      if (type === "scroll") scrollHandler = listener as () => void;
    });

    const rafQueue: FrameRequestCallback[] = [];
    vi.spyOn(window, "requestAnimationFrame").mockImplementation((cb) => {
      rafQueue.push(cb);
      return rafQueue.length;
    });

    Object.defineProperty(window, "scrollY", { configurable: true, value: 0, writable: true });

    const { getApi } = mountHarness({ disabled: () => true });

    window.scrollY = 200;
    scrollHandler?.();
    rafQueue.at(-1)?.(0);
    await nextTick();

    expect(getApi().isHidden.value).toBe(false);
  });

  it("cancels pending rAF on unmount", () => {
    vi.spyOn(window, "requestAnimationFrame").mockReturnValue(42);
    const cancelSpy = vi.spyOn(window, "cancelAnimationFrame");

    let scrollHandler: (() => void) | undefined;
    vi.spyOn(window, "addEventListener").mockImplementation((type, listener) => {
      if (type === "scroll") scrollHandler = listener as () => void;
    });

    const { wrapper } = mountHarness();
    scrollHandler?.();
    wrapper.unmount();

    expect(cancelSpy).toHaveBeenCalledWith(42);
  });
});
