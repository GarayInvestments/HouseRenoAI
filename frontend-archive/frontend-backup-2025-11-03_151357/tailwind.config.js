/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    // Gradient backgrounds
    'bg-gradient-to-br',
    'bg-gradient-to-b', 
    'bg-gradient-to-r',
    'from-slate-50',
    'via-slate-100',
    'to-blue-50',
    'from-white',
    'to-blue-50/30',
    'from-slate-50/50',
    'to-white/80',
    'via-slate-50/30',
    'to-slate-100/50',
    'from-blue-500',
    'to-blue-600',
    'from-blue-50',
    'to-blue-100/50',
    'from-green-50',
    'to-green-100/50',
    'from-orange-50',
    'to-orange-100/50',
    'from-purple-50',
    'to-purple-100/50',
    'from-slate-100',
    'to-blue-200',
    'from-green-100',
    'to-green-200',
    'from-orange-100',
    'to-orange-200',
    'from-blue-100',
    'to-blue-200',
    'from-green-400',
    'to-green-500',
    'from-orange-400',
    'to-orange-500',
    'from-blue-400',
    'to-blue-600',
    'from-blue-600',
    'to-blue-700',
    // Shadow classes
    'shadow-xl',
    'shadow-lg',
    'shadow-md',
    'shadow-sm',
    'shadow-blue-500/25',
    // Border opacity
    'border-slate-200/60',
    'border-slate-200/40',
    'border-blue-200',
    'border-green-200',
    'border-orange-200',
    'border-purple-200',
    // Background opacity
    'bg-white/95',
    'bg-white/60',
    'bg-white/20',
    'bg-white/30',
    'bg-slate-50/50',
    'bg-blue-50/20',
    'bg-blue-50/30',
    'bg-blue-50/40',
    // Backdrop blur
    'backdrop-blur-sm',
    'backdrop-blur-md',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
}