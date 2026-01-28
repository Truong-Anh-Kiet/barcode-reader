/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "var(--font-sans)",
          { fontFeatureSettings: '"cv11", "ss01"' },
          { fontVariationSettings: '"opsz" 32' },
        ],
        mono: [
          "var(--font-mono)",
          { fontFeatureSettings: '"cv11", "ss01"' },
          { fontVariationSettings: '"opsz" 32' },
        ],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}