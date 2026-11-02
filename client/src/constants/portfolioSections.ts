export type PortfolioSectionLink = {
  href: string;
  label: string;
};

/** Flat wash for portfolio CV Card tiles (overrides default Card fill/blur). */
export const PORTFOLIO_CV_TILE_CLASS = "portfolio-cv-tile-wash !backdrop-blur-none";

/** Coral accent fill (66%) + text for portfolio CV tech/skill chips. */
export const PORTFOLIO_CV_CHIP_CLASS = "portfolio-cv-chip";

/** Portfolio CV section anchors — order matches PortfolioPage; used by mobile nav. */
export const PORTFOLIO_SECTION_LINKS: PortfolioSectionLink[] = [
  { href: "#about", label: "about" },
  { href: "#experience", label: "experience" },
  { href: "#case-studies", label: "case studies" },
  { href: "#skills", label: "skills" },
  { href: "#education", label: "education" },
  { href: "#contacts", label: "contacts" },
];
