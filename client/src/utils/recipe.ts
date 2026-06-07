export function formatRecipeTime(minutes: number | null): string {
  if (!minutes) return "";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}

export function totalRecipeMinutes(
  prepTime: number | null,
  cookTime: number | null,
): number | null {
  if (prepTime == null && cookTime == null) return null;
  return (prepTime ?? 0) + (cookTime ?? 0);
}
