/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#2563EB', 50: '#EFF6FF', 100: '#DBEAFE', 200: '#BFDBFE', 300: '#93C5FD', 400: '#60A5FA', 500: '#2563EB', 600: '#1D4ED8', 700: '#1E40AF', 800: '#1E3A8A', 900: '#1E3A8A' },
        accent: { DEFAULT: '#60A5FA', light: '#93C5FD' },
        neutral: { text: '#475569', border: '#E2E8F0', bg: '#F8FAFC' }
      },
      fontFamily: { sans: ['Inter', 'Roboto', 'system-ui', 'sans-serif'] },
      maxWidth: { content: '72rem' }
    }
  },
  plugins: []
}
