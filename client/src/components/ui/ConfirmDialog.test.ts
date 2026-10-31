import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";

describe("ConfirmDialog", () => {
  it("renders cancel and confirm with mapped action icons", () => {
    const wrapper = mount(ConfirmDialog, {
      props: {
        open: true,
        title: "delete item",
        message: "are you sure?",
        confirmLabel: "delete",
        danger: true,
      },
      attachTo: document.body,
    });

    const cancel = Array.from(document.body.querySelectorAll("button")).find((el) =>
      el.textContent?.includes("cancel"),
    );
    const confirm = Array.from(document.body.querySelectorAll("button")).find((el) =>
      el.textContent?.includes("delete"),
    );
    expect(cancel).toBeTruthy();
    expect(confirm).toBeTruthy();
    expect(cancel?.querySelector("svg")).toBeTruthy();
    expect(confirm?.querySelector("svg")).toBeTruthy();

    wrapper.unmount();
  });
});
