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
  it("is keyboard-selectable", async () => {
    const wrapper = mount(RecipeCard, {
      props: {
        recipe,
        activeTags: [],
      },
      global: {
        stubs: {
          BaseImage: true,
          RecipeTagChip: true,
        },
      },
    });

    const card = wrapper.get('[role="button"]');
    expect(card.attributes("tabindex")).toBe("0");

    await card.trigger("keydown.enter");

    expect(wrapper.emitted("select")).toEqual([[42]]);
  });
});
