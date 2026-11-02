/** Collect in-page section targets for next-section scrolling. */
export function getSectionTargets(root: ParentNode = document): HTMLElement[] {
  const main = root.querySelector("#main-content");
  if (!main) return [];
  return Array.from(main.querySelectorAll<HTMLElement>("section[id]")).sort(
    (a, b) => sectionTop(a) - sectionTop(b),
  );
}

/** Absolute document top (offsetTop is relative to offsetParent, not the page). */
export function sectionTop(el: HTMLElement): number {
  return el.getBoundingClientRect().top + window.scrollY;
}

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth";
}

/** Minimum travel per click — ~one screen so short sections don’t feel stuck. */
export function scrollStepPx(viewportHeight: number): number {
  return Math.round(viewportHeight * 0.85);
}

/** Find the next section below the current scroll position. */
export function findNextSection(
  sections: HTMLElement[],
  scrollY: number,
  offset = 8,
): HTMLElement | null {
  return sections.find((section) => sectionTop(section) > scrollY + offset) ?? null;
}

export function useNextSectionScroll(): {
  scrollToNextSection: () => void;
  scrollToTop: () => void;
} {
  function scrollToNextSection(): void {
    const behavior = scrollBehavior();
    const step = scrollStepPx(window.innerHeight);
    const sections = getSectionTargets();
    // Next section whose top is below the current viewport top (no skipping).
    const next = findNextSection(sections, window.scrollY);
    if (next) {
      next.scrollIntoView({ behavior, block: "start" });
      return;
    }
    const maxTop = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    window.scrollTo({ top: Math.min(window.scrollY + step, maxTop), behavior });
  }

  function scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: scrollBehavior() });
  }

  return { scrollToNextSection, scrollToTop };
}
