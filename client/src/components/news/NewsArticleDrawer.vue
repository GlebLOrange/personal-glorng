<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import type { NewsArticleFormData, NewsStatus } from "@/types";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  form: NewsArticleFormData;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:form": [value: NewsArticleFormData];
}>();

const title = computed(() => (props.mode === "create" ? "New article" : "Edit article"));

const inputClass =
  "w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50";

function patch(patchValue: Partial<NewsArticleFormData>): void {
  emit("update:form", { ...props.form, ...patchValue });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}

function updateBullet(index: number, value: string): void {
  const bullets = [...props.form.bullets];
  bullets[index] = value;
  patch({ bullets });
}

function addBullet(): void {
  if (props.form.bullets.length >= 5) return;
  patch({ bullets: [...props.form.bullets, ""] });
}

function removeBullet(index: number): void {
  if (props.form.bullets.length <= 2) return;
  patch({ bullets: props.form.bullets.filter((_, i) => i !== index) });
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && props.open) {
    emit("close");
  }
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex justify-end">
      <Transition name="fade">
        <div
          v-if="open"
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="emit('close')"
        />
      </Transition>

      <Transition name="drawer-slide" appear>
        <aside
          v-if="open"
          class="drawer-panel relative w-full max-w-xl h-full bg-surface-dark border-l border-surface-border flex flex-col"
          aria-labelledby="news-drawer-title"
          @click.stop
        >
          <header
            class="flex items-center justify-between gap-3 px-6 py-4 border-b border-surface-border shrink-0"
          >
            <h2 id="news-drawer-title" class="text-lg font-bold text-surface-light">
              {{ title }}
            </h2>
            <button
              type="button"
              class="text-surface-mid hover:text-surface-light text-xl leading-none p-1 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
              aria-label="Close"
              @click="emit('close')"
            >
              &times;
            </button>
          </header>

          <form class="flex-1 overflow-y-auto px-6 py-5 space-y-6" @submit.prevent="emit('save')">
            <section class="space-y-4">
              <h3 class="text-sm font-medium text-surface-mid">Publishing</h3>
              <BaseInput
                :model-value="form.source_url"
                label="Source URL"
                type="url"
                placeholder="https://..."
                @update:model-value="patch({ source_url: toStringValue($event) })"
              />
              <label class="flex flex-col gap-1 text-sm text-surface-mid">
                Status
                <select
                  :value="form.status"
                  class="rounded-lg border border-surface-border bg-surface-dark px-4 py-2 text-sm text-surface-light focus:outline-none focus:border-accent-blue"
                  @change="patch({ status: ($event.target as HTMLSelectElement).value as NewsStatus })"
                >
                  <option value="draft">draft</option>
                  <option value="published">published</option>
                  <option value="unpublished">unpublished</option>
                  <option value="failed">failed</option>
                </select>
              </label>
            </section>

            <section class="space-y-4">
              <h3 class="text-sm font-medium text-surface-mid">Article</h3>
              <BaseInput
                :model-value="form.title"
                label="Title"
                placeholder="Readable news title"
                @update:model-value="patch({ title: toStringValue($event) })"
              />
              <BaseTextarea
                :model-value="form.summary"
                label="Summary"
                :rows="4"
                placeholder="Short readable summary"
                @update:model-value="patch({ summary: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.themes"
                label="Themes"
                placeholder="world, business"
                @update:model-value="patch({ themes: toStringValue($event) })"
              />
            </section>

            <section class="space-y-3">
              <div class="flex items-center justify-between gap-3">
                <h3 class="text-sm font-medium text-surface-mid">Key points</h3>
                <BaseButton
                  variant="ghost"
                  size="sm"
                  type="button"
                  :disabled="form.bullets.length >= 5"
                  @click="addBullet"
                >
                  + bullet
                </BaseButton>
              </div>
              <div v-for="(_, index) in form.bullets" :key="index" class="flex items-start gap-2">
                <span class="pt-2 text-sm text-surface-muted">{{ index + 1 }}.</span>
                <input
                  :value="form.bullets[index]"
                  :class="inputClass"
                  :placeholder="`Key point ${index + 1}`"
                  @input="updateBullet(index, ($event.target as HTMLInputElement).value)"
                />
                <BaseButton
                  v-if="form.bullets.length > 2"
                  variant="ghost"
                  size="sm"
                  type="button"
                  aria-label="Remove bullet"
                  @click="removeBullet(index)"
                >
                  &times;
                </BaseButton>
              </div>
            </section>

          </form>

          <footer class="shrink-0 px-6 py-4 border-t border-surface-border bg-surface-dark">
            <div class="flex gap-3">
              <BaseButton variant="primary" :disabled="loading" @click="emit('save')">
                {{ loading ? "Saving..." : "Save" }}
              </BaseButton>
              <BaseButton variant="ghost" type="button" @click="emit('close')">Cancel</BaseButton>
            </div>
          </footer>
        </aside>
      </Transition>
    </div>
  </Teleport>
</template>
