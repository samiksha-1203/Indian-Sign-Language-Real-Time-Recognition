/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F7F9FF",
        surface: "#FFFFFF",
        navy: "#161B33",
        "navy-soft": "#4A5178",
        mist: "#8790B3",
        sky: {
          DEFAULT: "#5B7FDE",
          soft: "#EAF0FF",
          deep: "#3C5BC0",
        },
        lav: {
          DEFAULT: "#9B8CE8",
          soft: "#F1EDFF",
        },
        mint: {
          DEFAULT: "#3FC9A8",
          soft: "#E4FAF3",
        },
        coral: {
          DEFAULT: "#EE7C6B",
          soft: "#FFEEE9",
        },
      },
      fontFamily: {
        display: ["'Sora'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(22, 27, 51, 0.04), 0 8px 24px rgba(22, 27, 51, 0.06)",
        glass: "0 1px 1px rgba(255,255,255,0.6) inset, 0 8px 30px rgba(91,127,222,0.10)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
