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

  it("wires hint text via aria-describedby", () => {
    const wrapper = mount(BaseTextarea, {
      props: {
        id: "message",
        label: "Message",
        hint: "Keep it short",
      },
    });

    expect(wrapper.get("textarea").attributes("aria-describedby")).toBe("message-hint");
    expect(wrapper.get("#message-hint").text()).toBe("Keep it short");
  });

  it("keeps the visual tip out of aria-describedby when label and placeholder are set", () => {
    const wrapper = mount(BaseTextarea, {
      props: {
        id: "notes",
        label: "Notes",
        placeholder: "optional tips",
      },
    });

    expect(wrapper.get("label").attributes("for")).toBe("notes");
    expect(wrapper.get("textarea").attributes("aria-label")).toBeUndefined();
    expect(wrapper.get("textarea").attributes("aria-describedby")).toBeUndefined();
    expect(wrapper.get("#notes-tip").text()).toBe("optional tips");
    expect(wrapper.get("#notes-tip").classes()).toContain("text-right");
    expect(wrapper.get("#notes-tip").attributes("aria-hidden")).toBe("true");
  });

  it("hides the tip and shows Clear when typing", async () => {
    const wrapper = mount(BaseTextarea, {
      props: {
        id: "notes",
        label: "Notes",
        placeholder: "optional tips",
        modelValue: "",
        "onUpdate:modelValue": (value: string | undefined) =>
          wrapper.setProps({ modelValue: value }),
      },
    });

    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(false);
    await wrapper.setProps({ modelValue: "hello" });
    expect(wrapper.find("#notes-tip").exists()).toBe(false);
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(true);
  });
});
