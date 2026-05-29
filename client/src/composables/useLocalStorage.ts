import { ref, type Ref } from "vue";

function readStorage<T>(key: string, defaultValue: T): T {
  if (typeof localStorage === "undefined") {
    return defaultValue;
  }
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) {
      return defaultValue;
    }
    return JSON.parse(raw) as T;
  } catch {
    return defaultValue;
  }
}

function writeStorage<T>(key: string, value: T): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore quota / private mode
  }
}

/** Reactive localStorage-backed ref with JSON serialization. */
export function useLocalStorage<T>(key: string, defaultValue: T): Ref<T> {
  const stored = ref(readStorage(key, defaultValue)) as Ref<T>;

  return new Proxy(stored, {
    get(target, prop, receiver) {
      if (prop === "value") {
        return target.value;
      }
      return Reflect.get(target, prop, receiver);
    },
    set(target, prop, value, receiver) {
      if (prop === "value") {
        target.value = value as T;
        writeStorage(key, value as T);
        return true;
      }
      return Reflect.set(target, prop, value, receiver);
    },
  }) as Ref<T>;
}

/** String localStorage without JSON quotes (for simple text prefs). */
export function useLocalStorageString(
  key: string,
  defaultValue: string,
): { value: Ref<string>; set: (next: string) => void } {
  const value = ref(defaultValue);

  if (typeof localStorage !== "undefined") {
    try {
      const stored = localStorage.getItem(key)?.trim();
      if (stored) {
        value.value = stored;
      }
    } catch {
      // ignore
    }
  }

  function set(next: string): void {
    const trimmed = next.trim();
    if (!trimmed) {
      return;
    }
    value.value = trimmed;
    try {
      localStorage.setItem(key, trimmed);
    } catch {
      // ignore
    }
  }

  return { value, set };
}
