/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx,html}",
    "./src/components/**/*.{js,jsx}",
    "./src/pages/**/*.{js,jsx}",
  ],
  safelist: [
    {
      pattern: /.(bg|text|border|ring)-./,
    },
    {
      pattern: /.(w|h|p|m)-./,
    },
    'shadow', 'rounded-lg', 'rounded-md', 'border', 'flex', 'grid', 'items-center', 'justify-center',
    'bg-primary', 'hover:bg-primary/90', 'text-primary-foreground',
  ],
  plugins: [require("tailwindcss-animate")],
}