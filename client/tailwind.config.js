/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2FCB6E',
          50: '#EEFBF3',
          100: '#D6F5E3',
          200: '#AAE9C5',
          300: '#7fe0a3',
          400: '#55D586',
          500: '#2FCB6E',
          600: '#27a359',
          700: '#1F8247',
          800: '#175C32',
          900: '#0F361D',
        },
        gray: {
          50: '#f7f9fc', // light-gray
          100: '#e5e7eb', // mid-gray
          200: '#e5e8eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280', // text-gray
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        black: {
          DEFAULT: '#000000',
          light: '#333333',
        },
      },
      boxShadow: {
        card: '0 8px 16px rgba(0, 0, 0, 0.1)',
      },
      borderRadius: {
        card: '12px',
      },
    },
    fontFamily: {
      sans: ['Segoe UI', 'Tahoma', 'Geneva', 'Verdana', 'sans-serif'],
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}