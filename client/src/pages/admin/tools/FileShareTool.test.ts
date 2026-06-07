/**
 * @vitest-environment jsdom
 */
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import FileShareTool from "@/pages/admin/tools/FileShareTool.vue";

const { getMock, toastMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
  toastMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { get: getMock, post: vi.fn(), delete: vi.fn() },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: toastMock }),
}));

vi.mock("@/composables/useClipboard", () => ({
  useClipboard: () => ({ copy: vi.fn() }),
}));

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

vi.mock("@/components/admin/ShareableListItem.vue", () => ({
  default: { template: "<div />" },
}));

describe("FileShareTool", () => {
  it("toasts when file list load fails", async () => {
    getMock.mockRejectedValue(new Error("network down"));

    mount(FileShareTool);
    await vi.waitFor(() => expect(getMock).toHaveBeenCalled());

    expect(toastMock).toHaveBeenCalledWith("network down", "error");
  });
});
