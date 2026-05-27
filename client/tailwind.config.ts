import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"Roboto Mono"', "monospace"],
      },
      colors: {
        accent: {
          blue: "#7BBDE2",
          violet: "#B8A3C8",
          golden: "#D4CE94",
        },
        surface: {
          light: "#F5F2EC",
          sage: "#D5DCD3",
          mid: "#C4B8AC",
          muted: "#8A847E",
          dark: "#141820",
          card: "#1c2230",
          border: "#2e3a4e",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
