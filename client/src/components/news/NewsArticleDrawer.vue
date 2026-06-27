<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import type { NewsArticleFormData, NewsSource, NewsStatus } from "@/types";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  form: NewsArticleFormData;
  sources: NewsSource[];
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

function toSourceId(value: string): number | null {
  const sourceId = Number(value);
  return Number.isInteger(sourceId) && sourceId > 0 ? sourceId : null;
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
              <label class="flex flex-col gap-1 text-sm text-surface-mid">
                Source
                <select
                  :value="form.source_id ?? ''"
                  class="rounded-lg border border-surface-border bg-surface-dark px-4 py-2 text-sm text-surface-light focus:outline-none focus:border-accent-blue"
                  @change="patch({ source_id: toSourceId(($event.target as HTMLSelectElement).value) })"
                >
                  <option value="">Auto from URL host</option>
                  <option v-for="source in sources" :key="source.id" :value="source.id">
                    {{ source.name }}{{ source.host ? ` (${source.host})` : "" }}
                  </option>
                </select>
              </label>
              <BaseInput
                :model-value="form.source_url"
                label="Article URL"
                type="url"
                placeholder="https://..."
                @update:model-value="patch({ source_url: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.source_name"
                label="Source name"
                placeholder="DW"
                @update:model-value="patch({ source_name: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.source_feed_url"
                label="Source feed/home URL"
                type="url"
                placeholder="https://www.dw.com/"
                @update:model-value="patch({ source_feed_url: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.source_published_at"
                label="Source published at"
                type="datetime-local"
                @update:model-value="patch({ source_published_at: toStringValue($event) })"
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
                v-if="mode === 'edit'"
                :model-value="form.slug"
                label="Slug"
                placeholder="article-url-slug"
                @update:model-value="patch({ slug: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.title"
                label="Title"
                placeholder="Readable news title"
                @update:model-value="patch({ title: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.original_title"
                label="Original title"
                placeholder="Original publisher title"
                @update:model-value="patch({ original_title: toStringValue($event) })"
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
              <BaseInput
                :model-value="form.language"
                label="Language"
                placeholder="en"
                @update:model-value="patch({ language: toStringValue($event) })"
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

            <section class="space-y-4">
              <h3 class="text-sm font-medium text-surface-mid">Admin metadata</h3>
              <BaseInput
                :model-value="form.published_at"
                label="Published at"
                type="datetime-local"
                @update:model-value="patch({ published_at: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.telegram_message_id"
                label="Telegram message ID"
                inputmode="numeric"
                placeholder="12345"
                @update:model-value="patch({ telegram_message_id: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.ai_model"
                label="AI model"
                placeholder="gpt-..."
                @update:model-value="patch({ ai_model: toStringValue($event) })"
              />
              <BaseInput
                :model-value="form.ai_input_hash"
                label="AI input hash"
                placeholder="sha256..."
                @update:model-value="patch({ ai_input_hash: toStringValue($event) })"
              />
              <BaseTextarea
                :model-value="form.ingest_error"
                label="Ingest error"
                :rows="3"
                placeholder="Optional ingestion error"
                @update:model-value="patch({ ingest_error: toStringValue($event) })"
              />
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
