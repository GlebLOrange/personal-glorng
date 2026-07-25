import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";

import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useNotify } from "@/composables/useNotify";

function clearToasts(): void {
  const { toasts, dismiss } = useNotify();
  for (const t of [...toasts.value]) {
    dismiss(t.id);
  }
}

describe("ToastContainer", () => {
  afterEach(() => {
    clearToasts();
  });

  it("tints the card border and background from toast type", async () => {
    const { toast } = useNotify();

    toast("saved", "success");
    const success = mount(ToastContainer);
    expect(success.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-success/10",
        "!border-status-success/30",
        "text-status-success",
      ]),
    );
    expect(success.get("[role='status']").classes()).toContain("text-status-success");
    success.unmount();
    clearToasts();

    toast("failed", "error");
    const error = mount(ToastContainer);
    expect(error.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-error/10",
        "!border-status-error/30",
        "text-status-error",
      ]),
    );
    expect(error.get("[role='alert']").classes()).toContain("text-status-error");
    error.unmount();
    clearToasts();

    toast("hello", "info");
    const info = mount(ToastContainer);
    expect(info.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining(["!bg-accent-blue/10", "!border-accent-blue/30", "text-accent-blue"]),
    );
    expect(info.get("[role='status']").classes()).toContain("text-accent-blue");
    info.unmount();
  });

  it("prefers error surface when the queue is mixed", () => {
    const { toast } = useNotify();
    toast("ok", "success");
    toast("nope", "error");

    const wrapper = mount(ToastContainer);
    expect(wrapper.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining(["!bg-status-error/10", "!border-status-error/30"]),
    );
  });
});
