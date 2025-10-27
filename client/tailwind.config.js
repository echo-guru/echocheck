/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'medical-green': '#10b981',
        'medical-red': '#ef4444',
        'medical-blue': '#3b82f6',
      }
    },
  },
  plugins: [],
}
