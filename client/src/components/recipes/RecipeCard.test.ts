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
  it("selects via a dedicated button without wrapping tag chips", async () => {
    const wrapper = mount(RecipeCard, {
      props: {
        recipe,
        activeTags: [],
      },
      global: {
        stubs: {
          BaseImage: true,
        },
      },
    });

    expect(wrapper.find('[role="button"]').exists()).toBe(false);

    const openButton = wrapper.get('button[aria-label="Open recipe Tomato Soup"]');
    await openButton.trigger("click");
    expect(wrapper.emitted("select")).toEqual([[42]]);

    const tagChip = wrapper.findAll("button").find((btn) => btn.text() === "quick");
    expect(tagChip).toBeTruthy();
    await tagChip!.trigger("click");
    expect(wrapper.emitted("tagClick")).toEqual([["quick"]]);
    expect(openButton.element.contains(tagChip!.element)).toBe(false);
  });
});
