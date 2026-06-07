<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
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

function patch(patch: Partial<RecipeFormData>): void {
  emit("update:form", { ...props.form, ...patch });
}

function addIngredient(): void {
  patch({ ingredients: [...props.form.ingredients, ""] });
}

function removeIngredient(index: number): void {
  if (props.form.ingredients.length <= 1) return;
  patch({ ingredients: props.form.ingredients.filter((_, i) => i !== index) });
}

function updateIngredient(index: number, value: string): void {
  const ingredients = [...props.form.ingredients];
  ingredients[index] = value;
  patch({ ingredients });
}

function addStep(): void {
  patch({ steps: [...props.form.steps, ""] });
}

function removeStep(index: number): void {
  if (props.form.steps.length <= 1) return;
  patch({ steps: props.form.steps.filter((_, i) => i !== index) });
}

function updateStep(index: number, value: string): void {
  const steps = [...props.form.steps];
  steps[index] = value;
  patch({ steps });
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
  <BaseModal v-if="open" max-width="2xl" @close="emit('close')">
    <h2 class="text-lg font-bold text-surface-light mb-6 -mt-2">
        <span class="accent-gradient">€ {{ formTitle }}</span>
      </h2>

      <form class="space-y-4 max-h-[65vh] overflow-y-auto pr-1" @submit.prevent="emit('save')">
        <BaseInput
          :model-value="form.title"
          label="Title"
          placeholder="Recipe title"
          @update:model-value="patch({ title: toStringValue($event) })"
        />

        <BaseInput
          :model-value="form.image_url"
          label="Image URL"
          placeholder="https://..."
          @update:model-value="patch({ image_url: toStringValue($event) })"
        />

        <div class="grid grid-cols-3 gap-3">
          <BaseInput
            :model-value="form.prep_time"
            label="Prep (min)"
            type="number"
            placeholder="15"
            @update:model-value="patch({ prep_time: toNullableNumber($event) })"
          />
          <BaseInput
            :model-value="form.cook_time"
            label="Cook (min)"
            type="number"
            placeholder="30"
            @update:model-value="patch({ cook_time: toNullableNumber($event) })"
          />
          <BaseInput
            :model-value="form.servings"
            label="Servings"
            type="number"
            placeholder="4"
            @update:model-value="patch({ servings: toNullableNumber($event) })"
          />
        </div>

        <BaseInput
          :model-value="form.tags"
          label="Tags"
          placeholder="dinner, pasta, quick"
          @update:model-value="patch({ tags: toStringValue($event) })"
        />

        <div>
          <label class="text-sm text-surface-mid block mb-1">Ingredients</label>
          <div class="space-y-2">
            <div v-for="(_, idx) in form.ingredients" :key="idx" class="flex gap-2">
              <input
                :value="form.ingredients[idx]"
                class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50"
                :placeholder="`Ingredient ${idx + 1}`"
                @input="updateIngredient(idx, ($event.target as HTMLInputElement).value)"
              />
              <BaseButton
                v-if="form.ingredients.length > 1"
                variant="ghost"
                size="sm"
                type="button"
                @click="removeIngredient(idx)"
              >
                &times;
              </BaseButton>
            </div>
            <BaseButton variant="ghost" size="sm" type="button" @click="addIngredient">
              + ingredient
            </BaseButton>
          </div>
        </div>

        <div>
          <label class="text-sm text-surface-mid block mb-1">Steps</label>
          <div class="space-y-2">
            <div v-for="(_, idx) in form.steps" :key="idx" class="flex gap-2">
              <div class="text-surface-mid text-sm pt-2 w-6 text-right shrink-0">
                {{ idx + 1 }}.
              </div>
              <textarea
                :value="form.steps[idx]"
                rows="2"
                class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
                :placeholder="`Step ${idx + 1}`"
                @input="updateStep(idx, ($event.target as HTMLTextAreaElement).value)"
              />
              <BaseButton
                v-if="form.steps.length > 1"
                variant="ghost"
                size="sm"
                type="button"
                @click="removeStep(idx)"
              >
                &times;
              </BaseButton>
            </div>
            <BaseButton variant="ghost" size="sm" type="button" @click="addStep">
              + step
            </BaseButton>
          </div>
        </div>

        <div>
          <label class="text-sm text-surface-mid block mb-1">Notes</label>
          <textarea
            :value="form.notes"
            rows="3"
            placeholder="Tips, variations, source link..."
            class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
            @input="patch({ notes: ($event.target as HTMLTextAreaElement).value })"
          />
        </div>

        <div class="flex gap-3 pt-2 sticky bottom-0 bg-surface-card">
          <BaseButton variant="primary" :disabled="loading">
            {{ loading ? "Saving..." : "Save" }}
          </BaseButton>
          <BaseButton variant="ghost" type="button" @click="emit('close')">Cancel</BaseButton>
        </div>
      </form>
  </BaseModal>
</template>
