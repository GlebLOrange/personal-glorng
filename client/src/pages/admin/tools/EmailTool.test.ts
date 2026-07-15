import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import EmailTool from "@/pages/admin/tools/EmailTool.vue";

const { postMock, toastMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
  toastMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: postMock },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: toastMock }),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ query: {} }),
}));

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

describe("EmailTool", () => {
  it("sanitizes preview HTML before rendering", async () => {
    postMock.mockResolvedValue({
      data: {
        html: '<p>Safe</p><script>alert("x")</script>',
      },
    });

    const wrapper = mount(EmailTool);
    await wrapper.find('input[placeholder="subject"]').setValue("Subject");
    await wrapper.find("textarea").setValue("Body text");

    const previewBtn = wrapper.findAll("button").find((b) => b.text().trim() === "preview");
    expect(previewBtn).toBeDefined();
    await previewBtn!.trigger("click");

    expect(postMock).toHaveBeenCalledWith(
      "/tools/email/preview",
      expect.objectContaining({ subject: "Subject", body: "Body text" }),
    );
    await vi.waitFor(() => expect(wrapper.html()).toContain("Safe"));
    expect(wrapper.html()).not.toContain("<script");
  });
});
