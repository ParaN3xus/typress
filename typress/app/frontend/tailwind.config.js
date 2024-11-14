/** @type {import('tailwindcss').Config} */

import daisyui from 'daisyui'

export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        'inner-strong': 'inset -1px 2px 9px 1.5px rgba(0, 0, 0, 0.1)',
        'offset': '-3px 6px 20px 1px rgba(0, 0, 0, 0.2)'
      },
    },
  },
  plugins: [
    daisyui
  ],
  daisyui: {
    themes: ["light", "dark"],
  },
}

