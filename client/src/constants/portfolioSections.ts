export type PortfolioSectionLink = {
  href: string;
  label: string;
};

/** In-page CV anchors — order matches PortfolioPage section order. */
export const PORTFOLIO_SECTION_LINKS: PortfolioSectionLink[] = [
  { href: "#about", label: "about" },
  { href: "#experience", label: "experience" },
  { href: "#case-studies", label: "case studies" },
  { href: "#skills", label: "skills" },
  { href: "#export", label: "export" },
  { href: "#contacts", label: "contacts" },
];
