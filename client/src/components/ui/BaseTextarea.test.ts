import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BaseTextarea from "@/components/ui/BaseTextarea.vue";

describe("BaseTextarea", () => {
  it("associates the visible label with the textarea", () => {
    const wrapper = mount(BaseTextarea, {
      props: {
        id: "message",
        label: "Message",
      },
    });

    expect(wrapper.get("label").attributes("for")).toBe("message");
    expect(wrapper.get("textarea").attributes("id")).toBe("message");
  });
});
