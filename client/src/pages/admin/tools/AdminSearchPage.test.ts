/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AdminSearchPage from "@/pages/admin/tools/AdminSearchPage.vue";

const { getMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: { get: getMock },
}));

vi.mock("@/components/layout/AdminPageLayout.vue", () => ({
  default: { template: "<div><slot /></div>" },
}));

describe("AdminSearchPage", () => {
  beforeEach(() => {
    getMock.mockReset();
  });

  it("links only safe hit URLs and drops malicious ones", async () => {
    getMock.mockResolvedValue({
      data: {
        query: "safe",
        hits: [
          {
            id: 1,
            title: "Safe task",
            url: "/tasks",
            source_type: "task",
            snippet: "ok",
            visibility: "admin",
          },
          {
            id: 2,
            title: "JS payload",
            url: "javascript:alert(1)",
            source_type: "task",
            snippet: "bad",
            visibility: "admin",
          },
          {
            id: 3,
            title: "Protocol relative",
            url: "//evil.example",
            source_type: "url",
            snippet: "bad",
            visibility: "admin",
          },
          {
            id: 4,
            title: "External https",
            url: "https://evil.example/x",
            source_type: "url",
            snippet: "bad",
            visibility: "admin",
          },
        ],
      },
    });

    const wrapper = mount(AdminSearchPage, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a class="router-link" :data-to="to"><slot /></a>',
          },
        },
      },
    });

    await wrapper.get('input[aria-label="search admin content"]').setValue("safe");
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(getMock).toHaveBeenCalledWith(
      "/tools/search",
      expect.objectContaining({ params: expect.objectContaining({ q: "safe" }) }),
    );

    const links = wrapper.findAll("a.router-link");
    expect(links).toHaveLength(1);
    expect(links[0]!.attributes("data-to")).toBe("/tasks");
    expect(links[0]!.text()).toBe("Safe task");

    expect(wrapper.text()).toContain("JS payload");
    expect(wrapper.text()).toContain("Protocol relative");
    expect(wrapper.text()).toContain("External https");
    expect(wrapper.html()).not.toContain("javascript:alert");
    expect(wrapper.html()).not.toContain("//evil.example");
    expect(wrapper.html()).not.toContain("https://evil.example/x");
  });

  it("does not search until the query has at least 3 characters", async () => {
    const wrapper = mount(AdminSearchPage, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a class="router-link" :data-to="to"><slot /></a>',
          },
        },
      },
    });

    const submit = wrapper.get('button[type="submit"]');
    expect(submit.attributes("disabled")).toBeDefined();

    await wrapper.get('input[aria-label="search admin content"]').setValue("ab");
    expect(submit.attributes("disabled")).toBeDefined();
    await wrapper.get("form").trigger("submit");
    await flushPromises();
    expect(getMock).not.toHaveBeenCalled();

    await wrapper.get('input[aria-label="search admin content"]').setValue("abc");
    expect(submit.attributes("disabled")).toBeUndefined();
  });
});
