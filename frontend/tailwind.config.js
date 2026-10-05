/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forest: { 50: '#eef7f2', 100: '#d8eee1', 200: '#b4dec6', 500: '#23845b', 600: '#176b49', 700: '#14563c', 800: '#124531', 900: '#103a2a' },
        ink: '#18332a',
      },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
      boxShadow: { card: '0 2px 10px rgba(21, 59, 43, .045)' },
    },
  },
  plugins: [],
};
