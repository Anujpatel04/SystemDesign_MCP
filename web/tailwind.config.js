/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc4fb',
          400: '#36a5f6',
          500: '#0c87e7',
          600: '#006bc5',
          700: '#0155a0',
          800: '#064984',
          900: '#0b3d6e',
        },
        surface: { DEFAULT: '#0f172a', light: '#1e293b', border: '#334155' },
      },
    },
  },
  plugins: [],
};
