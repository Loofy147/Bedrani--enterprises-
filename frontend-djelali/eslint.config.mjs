import "@rushstack/eslint-patch/modern-module-resolution.js";
import next from "eslint-config-next";
import globals from "globals";

/** @type {import('eslint').Linter.Config} */
const config = [
  {
    files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"],
    plugins: {
      next: next,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parserOptions: {
        project: true,
      },
    },
  },
];

export default config;
