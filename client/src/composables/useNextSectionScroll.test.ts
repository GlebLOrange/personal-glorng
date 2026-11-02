import { describe, expect, it } from "vitest";

function setTop(el: HTMLElement, top: number): void {
  el.getBoundingClientRect = () => ({ top }) as DOMRect;
}

import {
  findNextSection,
  getSectionTargets,
  scrollStepPx,
} from "@/composables/useNextSectionScroll";

describe("getSectionTargets", () => {
  it("returns section[id] elements under main sorted by document top", () => {
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
    setTop(sectionA, 100);
    setTop(sectionB, 200);

    const sections = getSectionTargets(document);
    expect(sections.map((el) => el.id)).toEqual(["a", "b"]);
  });
});

describe("findNextSection", () => {
  it("picks the first section below scrollY + offset", () => {
    const first = document.createElement("section");
    setTop(first, 100);
    const second = document.createElement("section");
    setTop(second, 500);

    expect(findNextSection([first, second], 50)).toBe(first);
    expect(findNextSection([first, second], 200)).toBe(second);
    expect(findNextSection([first, second], 90)).toBe(first);
    expect(findNextSection([first, second], 900)).toBeNull();
  });
});

describe("scrollStepPx", () => {
  it("uses about 85% of the viewport", () => {
    expect(scrollStepPx(1000)).toBe(850);
  });
});
