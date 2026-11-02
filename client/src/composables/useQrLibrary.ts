import { computed, ref, watch } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useLocalStorage } from "@/composables/useLocalStorage";
import { usePermissions } from "@/composables/usePermissions";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import type { PaginatedList, QrErrorLevel, QrListItem, QrStoredItem } from "@/types";
import {
  createGuestQr,
  deleteGuestQr,
  GUEST_QR_LIBRARY_KEY,
  guestQrLimitMessage,
  sanitizeGuestQrLibrary,
  toGuestQrListItem,
  updateGuestQr,
} from "@/utils/guestQrLibrary";

export function useQrLibrary() {
  const { can } = usePermissions();
  const canReadServer = computed(() => can("qr-generator", "read"));
  const canWriteServer = computed(() => can("qr-generator", "write"));
  /** Guest / no-capability: same UI, localStorage only. */
  const isLocalMode = computed(() => !canReadServer.value);
  const canReadLibrary = computed(() => true);
  const canWriteLibrary = computed(() => isLocalMode.value || canWriteServer.value);

  const items = ref<QrListItem[]>([]);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);

  const guestStored = useLocalStorage<unknown>(GUEST_QR_LIBRARY_KEY, []);
  const guestItems = ref<QrStoredItem[]>(sanitizeGuestQrLibrary(guestStored.value));

  watch(
    guestItems,
    (next) => {
      guestStored.value = next;
    },
    { deep: true },
  );

  const { loading, run: runList } = useApiAction();
  const { loading: detailLoading, run: runDetail } = useApiAction();
  const { loading: deleting, run: runDelete } = useApiAction();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);
  const guestLimitLabel = computed(() =>
    isLocalMode.value && guestItems.value.length > 0
      ? guestQrLimitMessage(guestItems.value.length)
      : null,
  );

  function syncLocalPage(): void {
    const all = guestItems.value;
    total.value = all.length;
    totalPages.value = Math.max(1, Math.ceil(all.length / ADMIN_LIST_PAGE_SIZE) || 1);
    if (all.length === 0) {
      totalPages.value = 0;
      items.value = [];
      return;
    }
    if (page.value > totalPages.value) {
      page.value = totalPages.value;
    }
    const start = (page.value - 1) * ADMIN_LIST_PAGE_SIZE;
    items.value = all.slice(start, start + ADMIN_LIST_PAGE_SIZE).map(toGuestQrListItem);
  }

  async function loadList(): Promise<void> {
    if (isLocalMode.value) {
      guestItems.value = sanitizeGuestQrLibrary(guestStored.value);
      syncLocalPage();
      return;
    }
    if (!canReadServer.value) return;
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
    if (isLocalMode.value) {
      return guestItems.value.find((item) => item.id === id) ?? null;
    }
    const data = await runDetail(() => api.get<QrStoredItem>(`/tools/qr-generator/library/${id}`), {
      errorFallback: "Failed to load QR code",
    });
    return data?.data ?? null;
  }

  async function remove(id: number): Promise<boolean> {
    if (isLocalMode.value) {
      guestItems.value = deleteGuestQr(guestItems.value, id);
      syncLocalPage();
      return true;
    }
    const result = await runDelete(() => api.delete(`/tools/qr-generator/library/${id}`), {
      successMessage: "QR code deleted",
      errorFallback: "Failed to delete QR code",
    });
    return Boolean(result);
  }

  function saveLocal(input: {
    id: number | null;
    content: string;
    label: string | null;
    error_level: QrErrorLevel;
    svg: string;
  }): { ok: true; item: QrStoredItem } | { ok: false; error: string } {
    const payload = {
      content: input.content,
      label: input.label,
      error_level: input.error_level,
      svg: input.svg,
    };
    const result =
      input.id != null
        ? updateGuestQr(guestItems.value, input.id, payload)
        : createGuestQr(guestItems.value, payload);
    if (!result.ok) {
      return result;
    }
    guestItems.value = result.next;
    page.value = 1;
    syncLocalPage();
    return { ok: true, item: result.item };
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
    void loadList();
  }

  watch(isLocalMode, () => {
    page.value = 1;
    void loadList();
  });

  return {
    isLocalMode,
    canReadLibrary,
    canWriteLibrary,
    guestLimitLabel,
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
    saveLocal,
    goToPage,
  };
}
