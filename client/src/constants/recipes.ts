/** Curated recipe tags for the form chip picker (themes-style). */
export const RECIPE_TAGS = [
  "italian",
  "mexican",
  "indian",
  "thai",
  "japanese",
  "chinese",
  "vegetarian",
  "vegan",
  "quick",
  "easy",
  "healthy",
  "dessert",
  "breakfast",
  "dinner",
  "seafood",
  "chicken",
  "beef",
  "pasta",
] as const;

export const RECIPE_TAG_LIMIT = 6;

export const RECIPE_TAG_SET = new Set<string>(RECIPE_TAGS);
