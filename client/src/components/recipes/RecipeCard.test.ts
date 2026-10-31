import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ClockIcon from "@/components/icons/ClockIcon.vue";
import TagIcon from "@/components/icons/TagIcon.vue";
import UsersIcon from "@/components/icons/UsersIcon.vue";
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
  it("selects on row click and shows icon-chip meta", async () => {
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

    expect(wrapper.element.tagName).toBe("TR");
    const row = wrapper.get('[aria-label="open recipe Tomato Soup"]');
    await row.trigger("click");
    expect(wrapper.emitted("select")).toEqual([[42]]);

    expect(wrapper.text()).toContain("TS");
    expect(wrapper.text()).toContain("Tomato Soup");

    const prepChip = wrapper.get('[aria-label="10m prep"]');
    expect(prepChip.text()).toContain("10m");
    expect(prepChip.attributes("title")).toBe("10m prep");

    const cookChip = wrapper.get('[aria-label="20m cook"]');
    expect(cookChip.text()).toContain("20m");
    expect(cookChip.attributes("title")).toBe("20m cook");

    const servingsChip = wrapper.get('[aria-label="2 servings"]');
    expect(servingsChip.text()).toContain("2");
    expect(servingsChip.text()).not.toContain("servings");

    expect(wrapper.findAllComponents(ClockIcon)).toHaveLength(2);
    expect(wrapper.findComponent(UsersIcon).exists()).toBe(true);
    expect(wrapper.findComponent(TagIcon).exists()).toBe(true);

    expect(wrapper.text()).toContain("quick");
    expect(wrapper.text()).not.toContain("10m prep");
    expect(wrapper.text()).not.toContain("2 servings");

    const metaCell = wrapper.get("td.min-w-0");
    expect(metaCell.classes()).toContain("min-w-0");
    expect(metaCell.classes()).toContain("max-w-[14rem]");
    expect(metaCell.classes()).toContain("overflow-hidden");
    expect(metaCell.attributes("title")).toBe("10m prep · 20m cook · 2 servings · quick");

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
