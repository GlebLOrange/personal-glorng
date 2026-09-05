import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";

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
    expect(success.get("[aria-label='notifications'] > *").classes()).toEqual(
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
    expect(error.get("[aria-label='notifications'] > *").classes()).toEqual(
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
    expect(info.get("[aria-label='notifications'] > *").classes()).toEqual(
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
    expect(wrapper.get("[aria-label='notifications'] > *").classes()).toEqual(
      expect.arrayContaining(["!bg-status-error/10", "!border-status-error/30"]),
    );
  });

  it("renders as a weather-grid tile with type hover tint", () => {
    const { toast } = useNotify();
    toast("failed", "error");

    const wrapper = mount(ToastContainer, { props: { variant: "tile" } });
    const host = wrapper.get('[data-testid="toast-host"]');
    expect(host.classes()).toEqual(
      expect.arrayContaining([
        "page-tile",
        "md:col-start-2",
        "md:h-0",
        "md:min-h-full",
        "md:overflow-hidden",
      ]),
    );
    expect(host.get(".page-weather-tile-card").classes()).toEqual(
      expect.arrayContaining([
        "!bg-status-error/10",
        "!border-status-error/30",
        "hover:!bg-status-error/20",
        "hover:!border-status-error/50",
        "max-h-full",
        "md:overflow-y-auto",
      ]),
    );
  });

  it("shows only the latest toast in the tile slot", () => {
    const { toast } = useNotify();
    toast("location added", "success");
    toast("location removed", "success");

    const wrapper = mount(ToastContainer, { props: { variant: "tile" } });
    const statuses = wrapper.findAll("[role='status']");
    expect(statuses).toHaveLength(1);
    expect(statuses[0].text()).toContain("location removed");
  });

  it("keeps sticky errors in the tile until dismiss", async () => {
    vi.useFakeTimers();
    const { toast, dismiss, toasts } = useNotify();
    toast("failed", "error");
    const id = toasts.value[0]!.id;

    const wrapper = mount(ToastContainer, { props: { variant: "tile" } });
    expect(wrapper.get("[role='alert']").text()).toContain("failed");
    vi.advanceTimersByTime(60_000);
    expect(wrapper.get("[role='alert']").text()).toContain("failed");

    dismiss(id);
    await nextTick();
    expect(wrapper.find("[role='alert']").exists()).toBe(false);
    vi.useRealTimers();
  });

  it("hides overlay when a tile host is claimed", () => {
    const { toast, claimTileHost } = useNotify();
    claimTileHost();
    toast("hello", "info");

    const wrapper = mount(ToastContainer, { props: { variant: "overlay" } });
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(false);
  });
});
