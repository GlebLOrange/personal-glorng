<script setup lang="ts">
import { computed } from "vue";

import RecipeIngredientFields from "@/components/recipes/RecipeIngredientFields.vue";
import RecipeStepFields from "@/components/recipes/RecipeStepFields.vue";
import RecipeTagFields from "@/components/recipes/RecipeTagFields.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import type { RecipeFormData } from "@/composables/useRecipes";

const props = defineProps<{
  open: boolean;
  form: RecipeFormData;
  formTitle: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:form": [value: RecipeFormData];
}>();

const showImagePreview = computed(() => Boolean(props.form.image_url.trim()));

function patch(patch: Partial<RecipeFormData>): void {
  emit("update:form", { ...props.form, ...patch });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}

function toNullableNumber(value: string | number | null | undefined): number | null {
  if (value === "" || value == null) return null;
  return Number(value);
}
</script>

<template>
  <BaseDrawer :open="open" :title="formTitle" max-width="lg" @close="emit('close')">
    <form id="recipe-form-drawer-form" class="space-y-3" @submit.prevent="emit('save')">
      <div class="space-y-2">
        <BaseInput
          compact
          :model-value="form.title"
          placeholder="enter title"
          @update:model-value="patch({ title: toStringValue($event) })"
        />
        <BaseInput
          compact
          :model-value="form.image_url"
          placeholder="image url"
          @update:model-value="patch({ image_url: toStringValue($event) })"
        />
        <BaseImage
          v-if="showImagePreview"
          :src="form.image_url"
          :alt="form.title || 'Recipe preview'"
          class="h-24 w-full rounded-md object-cover"
        />

        <div class="grid grid-cols-3 gap-2">
          <BaseInput
            compact
            :model-value="form.prep_time"
            type="number"
            placeholder="prep · min"
            @update:model-value="patch({ prep_time: toNullableNumber($event) })"
          />
          <BaseInput
            compact
            :model-value="form.cook_time"
            type="number"
            placeholder="cook · min"
            @update:model-value="patch({ cook_time: toNullableNumber($event) })"
          />
          <BaseInput
            compact
            :model-value="form.servings"
            type="number"
            placeholder="servings"
            @update:model-value="patch({ servings: toNullableNumber($event) })"
          />
        </div>
      </div>

      <RecipeIngredientFields
        :ingredients="form.ingredients"
        :form-open="open"
        @update:ingredients="patch({ ingredients: $event })"
      />

      <RecipeStepFields
        :steps="form.steps"
        :form-open="open"
        @update:steps="patch({ steps: $event })"
      />

      <RecipeTagFields :tags="form.tags" :form-open="open" @update:tags="patch({ tags: $event })" />

      <BaseTextarea
        compact
        :model-value="form.notes"
        :rows="3"
        placeholder="notes · tips, variations"
        @update:model-value="patch({ notes: String($event ?? '') })"
      />
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton variant="secondary" type="button" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            type="submit"
            form="recipe-form-drawer-form"
            family="2xx"
            :disabled="loading"
          >
            {{ loading ? "saving…" : "save" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
