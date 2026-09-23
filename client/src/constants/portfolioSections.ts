export type PortfolioSectionLink = {
  href: string;
  label: string;
};

/** In-page CV anchors — order matches PortfolioPage section order. */
export const PORTFOLIO_SECTION_LINKS: PortfolioSectionLink[] = [
  { href: "#about", label: "about" },
  { href: "#experience", label: "experience" },
  { href: "#projects", label: "projects" },
  { href: "#skills", label: "skills" },
  { href: "#contacts", label: "contacts" },
];
