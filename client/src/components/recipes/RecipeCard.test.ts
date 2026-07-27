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
  it("selects on row click and shows monogram without meta pills", async () => {
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

    const row = wrapper.get('[aria-label="open recipe Tomato Soup"]');
    await row.trigger("click");
    expect(wrapper.emitted("select")).toEqual([[42]]);
    expect(wrapper.text()).toContain("TS");
    expect(wrapper.text()).toContain("Tomato Soup");
    expect(wrapper.text()).not.toContain("prep 10m");
    expect(wrapper.text()).not.toContain("cook 20m");
    expect(wrapper.text()).not.toContain("2 servings");
    expect(wrapper.text()).not.toContain("no image");
    expect(wrapper.text()).not.toContain("quick");
    expect(wrapper.find('[aria-label="edit recipe"]').exists()).toBe(false);
  });

  it("emits edit and delete when canWrite", async () => {
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

    await wrapper.get('[aria-label="edit recipe"]').trigger("click");
    expect(wrapper.emitted("edit")?.[0]).toEqual([recipe]);

    await wrapper.get('[aria-label="delete recipe"]').trigger("click");
    expect(wrapper.emitted("delete")?.[0]).toEqual([recipe]);
  });
});
