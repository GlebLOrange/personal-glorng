/** Chart palette — resolves CSS theme tokens at runtime (canvas needs concrete colors). */

/** Dark-theme M3 fallbacks (match main.css :root / data-theme=dark). */
const CHART_COLOR_VARS = [
  ["--color-accent-blue", "#cfbdfe"],
  ["--color-status-success", "#a8d08d"],
  ["--color-status-warning", "#e8c468"],
  ["--color-status-error", "#ffb4ab"],
  ["--color-status-critical", "#ffdad7"],
  ["--color-surface-mid", "#938f99"],
  ["--color-surface-muted", "#79747e"],
  ["--color-surface-border", "#49454e"],
] as const;

const CHART_GRID_FALLBACK = "#2b2930";
const CHART_TEXT_FALLBACK = "#938f99";
const FONT_FAMILY = "IBM Plex Sans, Segoe UI, system-ui, sans-serif";

function cssVar(name: string, fallback: string): string {
  if (typeof document === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export type ChartTheme = {
  colors: string[];
  grid: string;
  text: string;
  defaults: {
    responsive: boolean;
    maintainAspectRatio: boolean;
    plugins: {
      legend: {
        labels: {
          color: string;
          font: { family: string; size: number };
        };
      };
    };
    scales: {
      x: {
        ticks: { color: string; font: { family: string; size: number } };
        grid: { color: string };
      };
      y: {
        ticks: { color: string; font: { family: string; size: number } };
        grid: { color: string };
      };
    };
  };
};

/** Resolve chart colors/options from current CSS variables (call when painting). */
export function resolveChartTheme(): ChartTheme {
  const colors = CHART_COLOR_VARS.map(([name, fallback]) => cssVar(name, fallback));
  const text = cssVar("--color-surface-mid", CHART_TEXT_FALLBACK);
  const grid = cssVar("--color-surface-grid", CHART_GRID_FALLBACK);

  return {
    colors,
    grid,
    text,
    defaults: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: text,
            font: { family: FONT_FAMILY, size: 11 },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: text,
            font: { family: FONT_FAMILY, size: 10 },
          },
          grid: { color: grid },
        },
        y: {
          ticks: {
            color: text,
            font: { family: FONT_FAMILY, size: 10 },
          },
          grid: { color: grid },
        },
      },
    },
  };
}
