export type PortfolioSectionLink = {
  href: string;
  label: string;
};

/** Portfolio CV section anchors — order matches PortfolioPage; used by mobile nav. */
export const PORTFOLIO_SECTION_LINKS: PortfolioSectionLink[] = [
  { href: "#about", label: "about" },
  { href: "#experience", label: "experience" },
  { href: "#case-studies", label: "case studies" },
  { href: "#skills", label: "skills" },
  { href: "#education", label: "education" },
  { href: "#contacts", label: "contacts" },
];
