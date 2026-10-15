/**
 * @vitest-environment jsdom
 */
import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AiChatTool from "@/pages/admin/tools/AiChatTool.vue";

const { getMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { get: getMock },
}));

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

describe("AiChatTool", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    getMock.mockReset();
    getMock.mockResolvedValue({
      data: {
        enabled: true,
        configured: true,
        model: "openai/gpt-oss-120b",
        provider: "groq",
        base_url: null,
      },
    });
  });

  it("shows current setup on the settings tab and no setup-help button on chat", async () => {
    const wrapper = mount(AiChatTool);
    await flushPromises();

    expect(wrapper.get("#ai-chat-panel-chat").exists()).toBe(true);
    expect(wrapper.find("#ai-chat-panel-settings").exists()).toBe(false);
    expect(wrapper.findAll("button").some((button) => /setup[-\s]?help/i.test(button.text()))).toBe(
      false,
    );

    await wrapper.get("#ai-chat-tab-settings").trigger("click");

    expect(wrapper.text()).toContain("current setup");
    expect(wrapper.find("#ai-chat-panel-chat").exists()).toBe(false);
    expect(wrapper.get("#ai-chat-panel-settings").exists()).toBe(true);
  });
});
