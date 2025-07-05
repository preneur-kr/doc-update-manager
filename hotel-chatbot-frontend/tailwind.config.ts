import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      colors: {
        primary: {
          50: '#f5f7fa',
          100: '#e4eaf1',
          200: '#c8d3e1',
          300: '#a2b4cb',
          400: '#7a93b2',
          500: '#56799c',
          600: '#3d5c7a',
          700: '#2d4257',
          800: '#1d2936',
          900: '#10141a',
        },
        dark: {
          900: '#18181b',
          800: '#232329',
          700: '#2a2a31',
          600: '#31313a',
        },
      },
      boxShadow: {
        'xl-dark': '0 8px 32px 0 rgba(0,0,0,0.45)',
      },
    },
  },
} satisfies Config 