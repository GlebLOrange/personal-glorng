import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import RecipeCard from "@/components/recipes/RecipeCard.vue";
import type { Recipe } from "@/types";

const recipe: Recipe = {
  id: 42,
  title: "Tomato Soup",
  ingredients: [],
  steps: [],
  notes: null,
  tags: ["quick"],
  image_url: null,
  prep_time: 10,
  cook_time: 20,
  servings: 2,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("RecipeCard", () => {
  it("selects on row click and shows prep/cook meta under the title", async () => {
    const wrapper = mount(RecipeCard, {
      props: {
        recipe,
      },
      global: {
        stubs: {
          BaseImage: true,
        },
      },
    });

    const openBtn = wrapper.get("[data-admin-list-open]");
    expect(openBtn.attributes("aria-label")).toBe("open recipe Tomato Soup");
    await openBtn.trigger("click");
    expect(wrapper.emitted("select")).toEqual([[42]]);

    expect(wrapper.text()).toContain("TS");
    expect(wrapper.text()).toContain("Tomato Soup");
    expect(wrapper.get("[data-admin-list-meta]").text()).toContain("10m prep");
    expect(wrapper.text()).toContain("20m cook");
    expect(wrapper.text()).toContain("2 servings");
    expect(wrapper.text()).toContain("quick");
    expect(wrapper.find('[aria-label="edit recipe"]').exists()).toBe(false);
  });

  it("shows edit and delete actions when canWrite", async () => {
    const wrapper = mount(RecipeCard, {
      props: {
        recipe,
        canWrite: true,
      },
      global: {
        stubs: {
          BaseImage: true,
          IconEditButton: {
            template: `<button type="button" aria-label="edit recipe" @click="$emit('click')" />`,
            emits: ["click"],
          },
          IconCloseButton: {
            template: `<button type="button" aria-label="delete recipe" @click="$emit('click')" />`,
            emits: ["click"],
          },
        },
      },
    });

    expect(wrapper.find('[aria-label="edit recipe"]').exists()).toBe(true);
    expect(wrapper.find('[aria-label="delete recipe"]').exists()).toBe(true);

    await wrapper.get('[aria-label="edit recipe"]').trigger("click");
    expect(wrapper.emitted("edit")?.[0]).toEqual([recipe]);

    await wrapper.get('[aria-label="delete recipe"]').trigger("click");
    expect(wrapper.emitted("delete")?.[0]).toEqual([recipe]);
  });
});
