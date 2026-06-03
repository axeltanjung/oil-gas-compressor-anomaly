/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: '#0a0e17',
          800: '#111827',
          700: '#1a2332',
          600: '#243044',
          500: '#2d3d56',
        },
        neon: {
          blue: '#00d4ff',
          green: '#00ff88',
          orange: '#ff6b35',
          red: '#ff3366',
          purple: '#a855f7',
          yellow: '#fbbf24',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glow: '0 0 20px rgba(0, 212, 255, 0.3)',
        'glow-green': '0 0 20px rgba(0, 255, 136, 0.3)',
        'glow-red': '0 0 20px rgba(255, 51, 102, 0.3)',
      },
    },
  },
  plugins: [],
}
