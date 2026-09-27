/** Chart palette — resolves CSS theme tokens at runtime (canvas needs concrete colors). */

/** Dark-theme pale fallbacks (match main.css :root / data-theme=dark). */
const CHART_COLOR_VARS = [
  ["--color-accent-blue", "#e8b07a"],
  ["--color-status-success", "#8dcea8"],
  ["--color-status-warning", "#e4c98a"],
  ["--color-status-error", "#f0a8a4"],
  ["--color-status-critical", "#e7a0b4"],
  ["--color-surface-mid", "#9198a1"],
  ["--color-surface-muted", "#7d8590"],
  ["--color-surface-border", "#30363d"],
] as const;

const CHART_GRID_FALLBACK = "#21262d";
const CHART_TEXT_FALLBACK = "#9198a1";
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
