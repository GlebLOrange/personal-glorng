<script setup lang="ts">
import { computed, onUnmounted, ref, useTemplateRef } from "vue";
import { RouterLink } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { effectiveSearchQuery } from "@/constants/search";
import { safeRouterPath } from "@/utils/safeUrl";

interface SearchHit {
  id: number;
  title: string;
  url: string;
  source_type: string;
  snippet: string;
  visibility: string;
}

const query = ref("");
const sourceType = ref("");
const hits = ref<SearchHit[]>([]);
const { loading, lastError: listError, run: runSearch } = useApiAction({ silent: true });
const hasSearched = ref(false);
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const sourceTypeOptions = [
  { value: "task", label: "tasks" },
  { value: "expense", label: "expenses" },
  { value: "feedback", label: "feedback" },
  { value: "url", label: "URLs" },
] as const;

const resultSummary = computed(() => {
  if (!hasSearched.value) return "";
  return hits.value.length === 1 ? "1 result" : `${hits.value.length} results`;
});

const displayHits = computed(() =>
  hits.value.map((hit) => ({ ...hit, path: safeRouterPath(hit.url) })),
);

const hasActiveFilters = computed(() => Boolean(sourceType.value));
const activeFilterLabel = computed(
  () => sourceTypeOptions.find((option) => option.value === sourceType.value)?.label,
);

let searchTimer: ReturnType<typeof setTimeout> | undefined;

async function search(): Promise<void> {
  const trimmed = effectiveSearchQuery(query.value);
  if (!trimmed) {
    hasSearched.value = false;
    hits.value = [];
    return;
  }

  hasSearched.value = true;
  const data = await runSearch(
    async () => {
      const params: Record<string, string> = { q: trimmed };
      if (sourceType.value) params.source_type = sourceType.value;
      const { data: response } = await api.get<{ query: string; hits: SearchHit[] }>(
        "/tools/search",
        { params },
      );
      return response;
    },
    { errorMessage: "Search failed.", logContext: "adminSearch.search" },
  );
  if (!data) {
    hits.value = [];
    return;
  }
  hits.value = data.hits;
}

function scheduleSearch(): void {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    void search();
  }, 300);
}

function onQueryChange(value: string): void {
  query.value = value;
  scheduleSearch();
}

function setSourceTypeFilter(next: string): void {
  sourceType.value = next;
  filterDropdownRef.value?.close();
  scheduleSearch();
}

function clearFilters(): void {
  sourceType.value = "";
  scheduleSearch();
}

function sourceLabel(type: string): string {
  return sourceTypeOptions.find((option) => option.value === type)?.label ?? type;
}

onUnmounted(() => {
  clearTimeout(searchTimer);
});
</script>

<template>
  <AdminPageLayout title="search">
    <div class="mb-6 space-y-2">
      <div class="flex min-w-0 flex-wrap items-center gap-2">
        <AdminFilterDropdown
          ref="filterDropdown"
          :has-active-filters="hasActiveFilters"
          :active-label="activeFilterLabel"
          :option-labels="sourceTypeOptions.map((option) => option.label)"
          @clear="clearFilters"
        >
          <template #chips>
            <AdminFilterChip
              v-for="option in sourceTypeOptions"
              :key="option.value"
              :label="option.label"
              :active="sourceType === option.value"
              @click="setSourceTypeFilter(option.value)"
            />
          </template>
        </AdminFilterDropdown>
      </div>
      <SearchInput
        :model-value="query"
        placeholder="search (admin content)"
        aria-label="search admin content"
        class="w-full"
        @update:model-value="onQueryChange"
      />
    </div>

    <section v-if="loading" class="space-y-3" aria-busy="true" aria-label="Searching">
      <Card v-for="i in 4" :key="i" class="h-20 animate-pulse" />
    </section>

    <ErrorState v-else-if="listError" :message="listError" show-retry @retry="search" />

    <EmptyState v-else-if="hasSearched && hits.length === 0" description="no matches found" />

    <div v-else-if="displayHits.length > 0" class="space-y-3">
      <p class="text-xs text-surface-muted">{{ resultSummary }} for “{{ query.trim() }}”</p>
      <Card v-for="hit in displayHits" :key="`${hit.source_type}:${hit.id}`" class="text-sm">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="text-xs px-2 py-0.5 rounded bg-accent-blue/20 text-accent-blue">
            {{ sourceLabel(hit.source_type) }}
          </span>
          <RouterLink
            v-if="hit.path"
            :to="hit.path"
            class="font-medium text-accent-blue hover:underline"
          >
            {{ hit.title }}
          </RouterLink>
          <span v-else class="font-medium text-surface-light">{{ hit.title }}</span>
        </div>
        <p class="text-xs text-surface-mid">{{ hit.snippet }}</p>
      </Card>
    </div>
  </AdminPageLayout>
</template>
