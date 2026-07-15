import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ErrorState from "@/components/ui/ErrorState.vue";

describe("ErrorState", () => {
  it("renders alert semantics and message", () => {
    const wrapper = mount(ErrorState, {
      props: { message: "Failed to load items." },
    });

    expect(wrapper.get('[role="alert"]').text()).toContain("Failed to load items.");
  });

  it("emits retry when retry button is clicked", async () => {
    const wrapper = mount(ErrorState, {
      props: {
        message: "Network error",
        showRetry: true,
        retryLabel: "Try again",
      },
    });

    await wrapper.get("button").trigger("click");
    expect(wrapper.emitted("retry")).toHaveLength(1);
  });
});
