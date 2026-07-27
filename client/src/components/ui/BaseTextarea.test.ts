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
    expect(wrapper.get('button[aria-label="help"]').exists()).toBe(true);
    expect(wrapper.find("p#message-hint").exists()).toBe(false);
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
    expect(wrapper.get("#notes-tip").classes()).toContain("text-left");
    expect(wrapper.get("#notes-tip").classes()).toContain("left-3");
    expect(wrapper.get("#notes-tip").classes()).toContain("right-11");
    expect(wrapper.get("#notes-tip").attributes("aria-hidden")).toBe("true");
  });

  it("shows overlay tip only when empty and reserves clear slot without jump", async () => {
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

    expect(wrapper.get("#notes-tip").classes()).toContain("right-11");
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(false);
    expect(wrapper.find(".invisible.pointer-events-none").exists()).toBe(true);

    await wrapper.setProps({ modelValue: "hello" });
    expect(wrapper.find("#notes-tip").exists()).toBe(false);
    const clearFilled = wrapper.get('button[aria-label="Clear"]');
    expect(clearFilled.element.closest(".invisible")).toBeNull();
  });

  it("clears the shell value and restores the tip without layout jump", async () => {
    const wrapper = mount(BaseTextarea, {
      props: {
        id: "body",
        placeholder: "body",
        modelValue: "hello",
        "onUpdate:modelValue": (value: string | undefined) =>
          wrapper.setProps({ modelValue: value }),
      },
    });

    expect(wrapper.find("#body-tip").exists()).toBe(false);
    await wrapper.get('button[aria-label="Clear"]').trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
    expect(wrapper.get("#body-tip").text()).toBe("body");
    expect(wrapper.get("#body-tip").classes()).toContain("right-11");
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(false);
  });
});
