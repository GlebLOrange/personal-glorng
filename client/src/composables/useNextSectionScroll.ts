/** Collect in-page section targets for next-section scrolling. */
export function getSectionTargets(root: ParentNode = document): HTMLElement[] {
  const main = root.querySelector("#main-content");
  if (!main) return [];
  return Array.from(main.querySelectorAll<HTMLElement>("section[id]")).sort(
    (a, b) => a.offsetTop - b.offsetTop,
  );
}

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth";
}

/** Find the next section below the current scroll position. */
export function findNextSection(
  sections: HTMLElement[],
  scrollY: number,
  offset = 48,
): HTMLElement | null {
  return sections.find((section) => section.offsetTop > scrollY + offset) ?? null;
}

export function useNextSectionScroll(): {
  scrollToNextSection: () => void;
  scrollToTop: () => void;
} {
  function scrollToNextSection(): void {
    const sections = getSectionTargets();
    const next = findNextSection(sections, window.scrollY);
    const behavior = scrollBehavior();
    if (next) {
      next.scrollIntoView({ behavior, block: "start" });
      return;
    }
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior,
    });
  }

  function scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: scrollBehavior() });
  }

  return { scrollToNextSection, scrollToTop };
}
