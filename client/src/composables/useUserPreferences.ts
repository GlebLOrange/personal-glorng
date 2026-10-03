import { ref, watch } from "vue";

import { api } from "@/composables/useApi";
import {
  EXPENSE_CURRENCY_STORAGE_KEY,
  EXPENSE_DEFAULT_CURRENCY,
  type CurrencyCode,
} from "@/composables/useExpenseFilters";
import { isCurrencyCode } from "@/constants/expenseCatalog";
import { useAuthStore } from "@/stores/auth";

export interface UserPreferences {
  display_currency: string | null;
}

const preferencesLoaded = ref(false);

function readLocalCurrency(): CurrencyCode {
  if (typeof localStorage === "undefined") {
    return EXPENSE_DEFAULT_CURRENCY;
  }
  const stored = localStorage.getItem(EXPENSE_CURRENCY_STORAGE_KEY)?.trim().toUpperCase();
  if (isCurrencyCode(stored)) {
    return stored;
  }
  return EXPENSE_DEFAULT_CURRENCY;
}

export function useUserPreferences() {
  const auth = useAuthStore();
  const displayCurrency = ref<CurrencyCode>(readLocalCurrency());
  const loading = ref(false);

  async function loadPreferences(): Promise<void> {
    if (preferencesLoaded.value) {
      return;
    }
    if (!auth.isAuthenticated) {
      displayCurrency.value = readLocalCurrency();
      preferencesLoaded.value = true;
      return;
    }

    loading.value = true;
    try {
      const { data } = await api.get<UserPreferences>("/auth/me/preferences");
      if (isCurrencyCode(data.display_currency)) {
        displayCurrency.value = data.display_currency;
        localStorage.setItem(EXPENSE_CURRENCY_STORAGE_KEY, data.display_currency);
      } else {
        const local = readLocalCurrency();
        displayCurrency.value = local;
        await api.patch("/auth/me/preferences", { display_currency: local });
      }
    } catch {
      displayCurrency.value = readLocalCurrency();
    } finally {
      loading.value = false;
      preferencesLoaded.value = true;
    }
  }

  async function saveDisplayCurrency(currency: CurrencyCode): Promise<void> {
    displayCurrency.value = currency;
    localStorage.setItem(EXPENSE_CURRENCY_STORAGE_KEY, currency);
    if (!auth.isAuthenticated) {
      return;
    }
    await api.patch("/auth/me/preferences", { display_currency: currency });
  }

  watch(
    () => auth.isAuthenticated,
    () => {
      preferencesLoaded.value = false;
      void loadPreferences();
    },
  );

  return {
    displayCurrency,
    loading,
    preferencesLoaded,
    loadPreferences,
    saveDisplayCurrency,
  };
}
