import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#171923",
        accent: "#7FB069",
        surface: "#262A35",
        "surface-muted": "#34343F",
        parchment: "#F3E6C8",
        muted: "#B8AA88",
        gold: "#D6A84F",
        danger: "#B85C50",
        border: "#6F6047",
        scroll: "#C9A86A",
        ink: "#10131A",
      },
      fontFamily: {
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "Noto Sans TC",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
} satisfies Config;
