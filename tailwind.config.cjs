module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        momoBlue: {
          50: '#eef8ff',
          100: '#d9f0ff',
          200: '#b3e1ff',
          300: '#84d1ff',
          400: '#4bbaff',
          500: '#1aa3ff',
          600: '#008ee6',
          700: '#006bb3',
          800: '#004b80',
          900: '#002b4d'
        },
        mobilityTeal: '#0fb6a5',
        mobilityWarm: '#ff8a4c',
        mobilitySlate: {
          100: '#f6f8fb',
          300: '#cfd8e3',
          500: '#94a3b8'
        }
      },
      borderRadius: {
        'xl': '1rem'
      }
    }
  },
  plugins: []
}
