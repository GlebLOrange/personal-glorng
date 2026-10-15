<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import QrLibraryListItem from "@/components/admin/QrLibraryListItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { ADMIN_MOBILE_LIST_CLASS, ADMIN_TH_CLASS } from "@/constants/adminDataTable";
import { useQrLibrary } from "@/composables/useQrLibrary";
import type { QrListItem } from "@/types";

const router = useRouter();
const deletingId = ref<number | null>(null);

const {
  canReadLibrary,
  canWriteLibrary,
  items,
  page,
  total,
  totalPages,
  loading,
  deleting,
  hasNextPage,
  hasPreviousPage,
  loadList,
  remove,
  goToPage,
} = useQrLibrary();

function openSaved(item: QrListItem): void {
  void router.push({ name: "qr-generator", query: { saved: String(item.id) } });
}

async function deleteSaved(id: number): Promise<void> {
  deletingId.value = id;
  try {
    if (await remove(id)) {
      if (items.value.length === 1 && page.value > 1) {
        page.value -= 1;
      }
      await loadList();
    }
  } finally {
    deletingId.value = null;
  }
}

onMounted(() => {
  if (canReadLibrary.value) void loadList();
});
</script>

<template>
  <Card v-if="canReadLibrary" variant="compact">
    <CardBody>
      <CardHeader class="!mb-3 flex flex-wrap items-center justify-between gap-2">
        <CardTitle>saved qr codes</CardTitle>
        <RouterLink to="/qr-generator" class="text-sm text-accent hover:underline">
          open generator
        </RouterLink>
      </CardHeader>

      <AdminListSkeleton v-if="loading && items.length === 0" />
      <EmptyState v-else-if="!loading && items.length === 0"> no saved QR codes yet. </EmptyState>

      <div v-else class="min-w-0">
        <div :class="ADMIN_MOBILE_LIST_CLASS">
          <QrLibraryListItem
            v-for="item in items"
            :key="`m-${item.id}`"
            layout="card"
            :item="item"
            :can-write="canWriteLibrary"
            :deleting="deleting && deletingId === item.id"
            @select="openSaved(item)"
            @delete="deleteSaved(item.id)"
          />
        </div>
        <AdminDataTable table-label="saved QR codes">
          <template #header>
            <th class="w-px px-3 py-1.5">
              <span class="sr-only">preview</span>
            </th>
            <th :class="ADMIN_TH_CLASS">content</th>
            <th :class="ADMIN_TH_CLASS">level</th>
            <th class="w-px px-2 text-right">
              <span class="sr-only">actions</span>
            </th>
          </template>
          <QrLibraryListItem
            v-for="item in items"
            :key="item.id"
            layout="table"
            :item="item"
            :can-write="canWriteLibrary"
            :deleting="deleting && deletingId === item.id"
            @select="openSaved(item)"
            @delete="deleteSaved(item.id)"
          />
        </AdminDataTable>
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
