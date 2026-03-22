import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        tesla: {
          red: '#E31937',
          dark: '#171A20',
          gray: '#393C41',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
