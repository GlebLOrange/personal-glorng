<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink } from "vue-router";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { useQrLibrary, type QrStoredItem } from "@/composables/useQrLibrary";

const {
  canReadLibrary,
  items,
  page,
  total,
  totalPages,
  loading,
  hasNextPage,
  hasPreviousPage,
  loadList,
  goToPage,
} = useQrLibrary();

function tileTitle(item: QrStoredItem): string {
  return item.label?.trim() || item.content_preview;
}

onMounted(() => {
  if (canReadLibrary.value) void loadList();
});
</script>

<template>
  <Card v-if="canReadLibrary" variant="compact" class="col-span-full">
    <CardBody>
      <CardHeader class="!mb-3 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>saved qr codes</CardTitle>
        <RouterLink to="/qr-generator" class="text-sm text-accent hover:underline">
          open generator
        </RouterLink>
      </CardHeader>

      <AdminListSkeleton v-if="loading && items.length === 0" />
      <EmptyState v-else-if="!loading && items.length === 0" message="No saved QR codes yet." />

      <div v-else class="page-tool-grid min-w-0">
        <RouterLink
          v-for="item in items"
          :key="item.id"
          class="page-tile"
          :to="{ name: 'qr-generator', query: { saved: String(item.id) } }"
          :aria-label="`Edit ${tileTitle(item)}`"
        >
          <Card hoverable class="page-tile-card h-full items-center text-center">
            <img
              :src="item.svg_url"
              alt=""
              class="mx-auto size-20 rounded-md bg-white p-1.5"
              loading="lazy"
            />
            <h3 class="mt-2 w-full truncate text-sm font-semibold text-surface-light">
              {{ tileTitle(item) }}
            </h3>
            <p
              v-if="item.label"
              class="mt-0.5 w-full truncate text-xs lowercase text-surface-mid"
            >
              {{ item.content_preview }}
            </p>
            <p class="mt-1 text-xs text-surface-muted">correction {{ item.error_level }}</p>
          </Card>
        </RouterLink>
      </div>

      <AdminListFooter
        v-if="items.length > 0"
        class="mt-4"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        item-label="saved QR codes"
        aria-label="Saved QR codes pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </CardBody>
  </Card>
</template>
