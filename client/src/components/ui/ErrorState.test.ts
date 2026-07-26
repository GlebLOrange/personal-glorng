import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ErrorState from "@/components/ui/ErrorState.vue";

describe("ErrorState", () => {
  it("renders alert semantics and message", () => {
    const wrapper = mount(ErrorState, {
      props: { message: "Failed to load items." },
    });

    const alert = wrapper.get('[role="alert"]');
    expect(alert.text()).toContain("Failed to load items.");
    expect(alert.get("p").classes()).toContain("text-status-error");
  });

  it("emits retry when retry button is clicked", async () => {
    const wrapper = mount(ErrorState, {
      props: {
        message: "Network error",
        showRetry: true,
        retryLabel: "try again",
      },
    });

    expect(wrapper.get("button").text()).toContain("try again");
    await wrapper.get("button").trigger("click");
    expect(wrapper.emitted("retry")).toHaveLength(1);
  });
});
