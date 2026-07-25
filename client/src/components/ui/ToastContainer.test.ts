import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";

import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useNotify } from "@/composables/useNotify";

function clearToasts(): void {
  const { toasts, dismiss, releaseTileHost } = useNotify();
  for (const t of [...toasts.value]) {
    dismiss(t.id);
  }
  releaseTileHost();
}

describe("ToastContainer", () => {
  afterEach(() => {
    clearToasts();
  });

  it("tints the card border and background from toast type", async () => {
    const { toast } = useNotify();

    toast("saved", "success");
    const success = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(success.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-success/10",
        "!border-status-success/30",
        "text-status-success",
        "hover:!bg-status-success/20",
        "hover:!border-status-success/50",
      ]),
    );
    expect(success.get("[role='status']").classes()).toContain("text-status-success");
    success.unmount();
    clearToasts();

    toast("failed", "error");
    const error = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(error.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-error/10",
        "!border-status-error/30",
        "text-status-error",
        "hover:!bg-status-error/20",
        "hover:!border-status-error/50",
      ]),
    );
    expect(error.get("[role='alert']").classes()).toContain("text-status-error");
    error.unmount();
    clearToasts();

    toast("hello", "info");
    const info = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(info.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining([
        "!bg-accent-blue/10",
        "!border-accent-blue/30",
        "text-accent-blue",
        "hover:!bg-accent-blue/20",
        "hover:!border-accent-blue/50",
      ]),
    );
    expect(info.get("[role='status']").classes()).toContain("text-accent-blue");
    info.unmount();
  });

  it("prefers error surface when the queue is mixed", () => {
    const { toast } = useNotify();
    toast("ok", "success");
    toast("nope", "error");

    const wrapper = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(wrapper.get("[aria-label='Notifications'] > *").classes()).toEqual(
      expect.arrayContaining(["!bg-status-error/10", "!border-status-error/30"]),
    );
  });

  it("renders as a weather-grid tile with type hover tint", () => {
    const { toast } = useNotify();
    toast("failed", "error");

    const wrapper = mount(ToastContainer, { props: { variant: "tile" } });
    const host = wrapper.get('[data-testid="toast-host"]');
    expect(host.classes()).toEqual(expect.arrayContaining(["page-tile", "md:col-start-2"]));
    expect(host.get(".page-weather-tile-card").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-error/10",
        "!border-status-error/30",
        "hover:!bg-status-error/20",
        "hover:!border-status-error/50",
      ]),
    );
  });

  it("hides overlay when a tile host is claimed", () => {
    const { toast, claimTileHost } = useNotify();
    claimTileHost();
    toast("hello", "info");

    const wrapper = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(false);
  });
});
