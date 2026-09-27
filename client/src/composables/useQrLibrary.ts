import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import type { PaginatedList, QrListItem, QrStoredItem } from "@/types";

export function useQrLibrary() {
  const { can } = usePermissions();
  const canReadLibrary = computed(() => can("qr-generator", "read"));
  const canWriteLibrary = computed(() => can("qr-generator", "write"));

  const items = ref<QrListItem[]>([]);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);

  const { loading, run: runList } = useApiAction();
  const { loading: detailLoading, run: runDetail } = useApiAction();
  const { loading: deleting, run: runDelete } = useApiAction();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);

  async function loadList(): Promise<void> {
    if (!canReadLibrary.value) return;
    const data = await runList(
      () =>
        api.get<PaginatedList<QrListItem>>("/tools/qr-generator/library", {
          params: { page: page.value, per_page: ADMIN_LIST_PAGE_SIZE },
        }),
      { errorFallback: "Failed to load saved QR codes" },
    );
    if (data) {
      items.value = data.data.items;
      total.value = data.data.total;
      totalPages.value = data.data.pages;
    }
  }

  async function loadOne(id: number): Promise<QrStoredItem | null> {
    const data = await runDetail(
      () => api.get<QrStoredItem>(`/tools/qr-generator/library/${id}`),
      { errorFallback: "Failed to load QR code" },
    );
    return data?.data ?? null;
  }

  async function remove(id: number): Promise<boolean> {
    const result = await runDelete(() => api.delete(`/tools/qr-generator/library/${id}`), {
      successMessage: "QR code deleted",
      errorFallback: "Failed to delete QR code",
    });
    return Boolean(result);
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
    void loadList();
  }

  return {
    canReadLibrary,
    canWriteLibrary,
    items,
    page,
    total,
    totalPages,
    loading,
    detailLoading,
    deleting,
    hasNextPage,
    hasPreviousPage,
    loadList,
    loadOne,
    remove,
    goToPage,
  };
}
