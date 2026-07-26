/**
 * @vitest-environment jsdom
 */
import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";

import EmailTool from "@/pages/admin/tools/EmailTool.vue";
import { EMAIL_DRAFT_STORAGE_KEY, writeEmailDraft } from "@/utils/emailDraft";

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

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

afterEach(() => {
  sessionStorage.clear();
  postMock.mockReset();
  toastMock.mockReset();
});

describe("EmailTool", () => {
  it("sanitizes preview HTML before rendering", async () => {
    postMock.mockResolvedValue({
      data: {
        html: '<p>Safe</p><script>alert("x")</script>',
      },
    });

    const wrapper = mount(EmailTool);
    await wrapper.get("#email-subject").setValue("Subject");
    await wrapper.get("#email-body").setValue("Body text");

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

  it("consumes a sessionStorage draft on mount and clears it", async () => {
    writeEmailDraft({
      to: "user@example.com",
      subject: "Re: theme",
      body: "\n\n--- Original ---\nhello",
    });

    const wrapper = mount(EmailTool);
    await vi.waitFor(() => {
      expect((wrapper.get("#email-to").element as HTMLInputElement).value).toBe("user@example.com");
    });
    expect((wrapper.get("#email-subject").element as HTMLInputElement).value).toBe("Re: theme");
    expect((wrapper.get("#email-body").element as HTMLTextAreaElement).value).toContain("hello");
    expect(sessionStorage.getItem(EMAIL_DRAFT_STORAGE_KEY)).toBeNull();
  });
});
