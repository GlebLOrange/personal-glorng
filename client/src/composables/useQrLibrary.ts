import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import type { PaginatedList } from "@/types";

export type QrErrorLevel = "L" | "M" | "Q" | "H";

export interface QrStoredItem {
  id: number;
  content: string;
  content_preview: string;
  label: string | null;
  error_level: QrErrorLevel;
  svg_url: string;
  created_at: string;
  updated_at: string;
  svg?: string | null;
}

export function useQrLibrary() {
  const { can } = usePermissions();
  const canReadLibrary = computed(() => can("qr-generator", "read"));

  const items = ref<QrStoredItem[]>([]);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);

  const { loading, run } = useApiAction();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);

  async function loadList(): Promise<void> {
    if (!canReadLibrary.value) return;
    const data = await run(
      () =>
        api.get<PaginatedList<QrStoredItem>>("/tools/qr-generator/library", {
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
    const data = await run(
      () => api.get<QrStoredItem>(`/tools/qr-generator/library/${id}`),
      { errorFallback: "Failed to load QR code" },
    );
    return data?.data ?? null;
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
    void loadList();
  }

  return {
    canReadLibrary,
    items,
    page,
    total,
    totalPages,
    loading,
    hasNextPage,
    hasPreviousPage,
    loadList,
    loadOne,
    goToPage,
  };
}
