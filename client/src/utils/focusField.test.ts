import { describe, expect, it } from "vitest";

import { focusEditableField, queryEditableField } from "@/utils/focusField";

describe("focusField", () => {
  it("prefers text inputs over buttons", () => {
    const root = document.createElement("div");
    root.innerHTML = `
      <button type="button">Close</button>
      <input type="text" aria-label="Title" />
      <button type="submit">Save</button>
    `;

    const field = queryEditableField(root);
    expect(field?.getAttribute("aria-label")).toBe("Title");
  });

  it("falls back when no editable field exists", () => {
    const root = document.createElement("div");
    const close = document.createElement("button");
    close.type = "button";
    close.textContent = "Close";
    root.append(close);
    document.body.append(root);

    focusEditableField(root, close);
    expect(document.activeElement).toBe(close);

    root.remove();
  });
});
