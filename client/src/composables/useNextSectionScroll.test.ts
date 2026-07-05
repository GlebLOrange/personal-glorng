import { describe, expect, it } from "vitest";

import { findNextSection, getSectionTargets } from "@/composables/useNextSectionScroll";

describe("getSectionTargets", () => {
  it("returns section[id] elements under main sorted by offsetTop", () => {
    document.body.innerHTML = `
      <main id="main-content">
        <section id="b"></section>
        <section id="a"></section>
        <div id="ignored"></div>
      </main>
    `;

    const main = document.querySelector("#main-content");
    const sectionA = main?.querySelector<HTMLElement>("#a");
    const sectionB = main?.querySelector<HTMLElement>("#b");
    if (!sectionA || !sectionB) throw new Error("fixture sections missing");
    Object.defineProperty(sectionA, "offsetTop", { value: 100, configurable: true });
    Object.defineProperty(sectionB, "offsetTop", { value: 200, configurable: true });

    const sections = getSectionTargets(document);
    expect(sections.map((el) => el.id)).toEqual(["a", "b"]);
  });
});

describe("findNextSection", () => {
  it("picks the first section below scrollY + offset", () => {
    const first = document.createElement("section");
    Object.defineProperty(first, "offsetTop", { value: 100, configurable: true });
    const second = document.createElement("section");
    Object.defineProperty(second, "offsetTop", { value: 500, configurable: true });

    expect(findNextSection([first, second], 50)?.offsetTop).toBe(100);
    expect(findNextSection([first, second], 200)?.offsetTop).toBe(500);
    expect(findNextSection([first, second], 900)).toBeNull();
  });
});
