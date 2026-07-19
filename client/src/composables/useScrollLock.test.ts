import { afterEach, describe, expect, it } from "vitest";
import { effectScope, nextTick, ref } from "vue";

import { useScrollLock } from "@/composables/useScrollLock";

afterEach(() => {
  document.body.style.overflow = "";
});

describe("useScrollLock", () => {
  it("locks and restores body overflow with nested holders", async () => {
    document.body.style.overflow = "auto";
    const a = ref(false);
    const b = ref(false);
    const scope = effectScope();

    scope.run(() => {
      useScrollLock(a);
      useScrollLock(b);
    });

    a.value = true;
    await nextTick();
    expect(document.body.style.overflow).toBe("hidden");

    b.value = true;
    await nextTick();
    expect(document.body.style.overflow).toBe("hidden");

    a.value = false;
    await nextTick();
    expect(document.body.style.overflow).toBe("hidden");

    b.value = false;
    await nextTick();
    expect(document.body.style.overflow).toBe("auto");

    scope.stop();
  });
});
