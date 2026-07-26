/** Chart palette — resolves CSS theme tokens at runtime (canvas needs concrete colors). */

const CHART_COLOR_VARS = [
  ["--color-accent-blue", "#8ec4e0"],
  ["--color-status-success", "#7bc49a"],
  ["--color-status-warning", "#d4ce94"],
  ["--color-status-error", "#e88a8a"],
  ["--color-status-critical", "#d98aad"],
  ["--color-surface-mid", "#d4cdc6"],
  ["--color-surface-muted", "#a39d97"],
  ["--color-surface-border", "#6b7a90"],
] as const;

/** Darker mix for grid lines — border token is too light on canvas. */
const CHART_GRID_FALLBACK = "#2e3a4e";
const CHART_TEXT_FALLBACK = "#d4cdc6";
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
  const grid = CHART_GRID_FALLBACK;

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
