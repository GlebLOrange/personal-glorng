/**
 * @vitest-environment jsdom
 */
import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";

import DbMaintenanceTool from "@/pages/admin/tools/DbMaintenanceTool.vue";

const { getMock, postMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
  postMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { get: getMock, post: postMock },
}));

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

vi.mock("@/components/ui/ConfirmDialog.vue", () => ({
  default: {
    name: "ConfirmDialog",
    props: {
      open: Boolean,
      title: String,
      confirmLabel: String,
      loadingLabel: String,
      loading: Boolean,
      danger: Boolean,
    },
    emits: ["confirm", "cancel"],
    template: `
      <div v-if="open" data-testid="confirm-dialog">
        <p>{{ title }}</p>
        <button type="button" data-testid="confirm-run" @click="$emit('confirm')">
          {{ confirmLabel }}
        </button>
        <button type="button" @click="$emit('cancel')">cancel</button>
      </div>
    `,
  },
}));

vi.mock("@/components/admin/TurnstileWidget.vue", () => ({
  default: {
    name: "TurnstileWidget",
    props: { siteKey: { type: String, required: true } },
    emits: ["update:token", "error"],
    methods: {
      reset() {
        this.$emit("update:token", "");
      },
    },
    template:
      '<button type="button" data-testid="fake-captcha" @click="$emit(\'update:token\', \'tok\')">captcha</button>',
  },
}));

afterEach(() => {
  getMock.mockReset();
  postMock.mockReset();
});

describe("DbMaintenanceTool", () => {
  it("keeps start disabled until a captcha token exists", async () => {
    getMock.mockResolvedValue({
      data: {
        site_key: "site",
        enabled: true,
        status: "idle",
        detail: "",
      },
    });

    const wrapper = mount(DbMaintenanceTool);
    await flushPromises();

    const start = wrapper.findAll("button").find((b) => b.text().includes("start maintenance"));
    expect(start).toBeDefined();
    expect(start!.attributes("disabled")).toBeDefined();

    await wrapper.get('[data-testid="fake-captcha"]').trigger("click");
    await flushPromises();

    expect(start!.attributes("disabled")).toBeUndefined();
  });

  it("opens confirm dialog before posting", async () => {
    getMock.mockResolvedValue({
      data: {
        site_key: "site",
        enabled: true,
        status: "idle",
        detail: "",
      },
    });
    postMock.mockResolvedValue({
      data: { status: "running", detail: "maintenance is running" },
    });

    const wrapper = mount(DbMaintenanceTool);
    await flushPromises();
    await wrapper.get('[data-testid="fake-captcha"]').trigger("click");
    await flushPromises();

    const start = wrapper.findAll("button").find((b) => b.text().includes("start maintenance"));
    await start!.trigger("click");
    await flushPromises();

    expect(wrapper.get('[data-testid="confirm-dialog"]').text()).toContain(
      "run database maintenance",
    );
    expect(postMock).not.toHaveBeenCalled();

    await wrapper.get('[data-testid="confirm-run"]').trigger("click");
    await flushPromises();

    expect(postMock).toHaveBeenCalledWith("/admin/maintenance/run", {
      turnstile_token: "tok",
    });
  });
});
