import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        trustline: {
          background: "#FFFFFF",
          surface: "#F7F8FA",
          surface2: "#F1F3F5",
          border: "#E6E8EC",
          text: "#111318",
          textSecondary: "#555B66",
          textMuted: "#7A808A",
          primary: "#2457D6",
          primaryDark: "#163B91",
          primaryLight: "#EAF0FF",
          success: "#159A68",
          warning: "#B77900",
          danger: "#D92D3A",
          info: "#3672C9",
          inverse: "#111318",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "system-ui", "sans-serif"],
        mono: [
          "ui-monospace",
          "SF Mono",
          "Cascadia Code",
          "Roboto Mono",
          "Consolas",
          "monospace",
        ],
      },
      fontSize: {
        "display-lg": ["clamp(2.75rem, 5.5vw, 5.5rem)", { lineHeight: "1.04", letterSpacing: "-0.025em" }],
        "display-md": ["clamp(2.25rem, 4vw, 3.5rem)", { lineHeight: "1.08", letterSpacing: "-0.02em" }],
        "display-sm": ["clamp(1.75rem, 2.6vw, 2.5rem)", { lineHeight: "1.12", letterSpacing: "-0.015em" }],
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
      },
      boxShadow: {
        soft: "var(--shadow-sm)",
        elevated: "var(--shadow-md)",
      },
      maxWidth: {
        content: "1240px",
        wide: "1440px",
      },
      spacing: {
        18: "4.5rem",
      },
    },
  },
  plugins: [],
};
export default config;
