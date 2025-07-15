import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
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
          900: '#0f0f0f',
          800: '#1a1a1a',
          700: '#2a2a2a',
          600: '#3a3a3a',
          500: '#4a4a4a',
          400: '#6a6a6a',
          300: '#8a8a8a',
          200: '#aaaaaa',
          100: '#cccccc',
          50: '#f5f5f5',
        },
      },
      boxShadow: {
        'xl-dark': '0 8px 32px 0 rgba(0,0,0,0.45)',
        dark: '0 4px 16px 0 rgba(0,0,0,0.3)',
      },
    },
  },
  plugins: [],
} satisfies Config;
