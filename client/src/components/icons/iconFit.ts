export type IconBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

const TARGET = 16;
const CENTER = 12;

function trim(value: number): string {
  return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

/**
 * Uniform scale so a glyph's longest side is 16 inside a 24 viewBox, centered.
 * Returns undefined when the glyph is already that size, or when there is no box.
 */
export function iconFitTransform(box: IconBox): string | undefined {
  if (box.width < 1 || box.height < 1) return undefined;
  const scale = TARGET / Math.max(box.width, box.height);
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  const alreadyFit =
    Math.abs(scale - 1) < 0.04 && Math.abs(cx - CENTER) < 0.4 && Math.abs(cy - CENTER) < 0.4;
  if (alreadyFit) return undefined;
  return `translate(${CENTER} ${CENTER}) scale(${trim(scale)}) translate(${trim(-cx)} ${trim(-cy)})`;
}
