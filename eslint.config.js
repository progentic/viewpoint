import eslint from "@eslint/js"
import typescriptEslint from "typescript-eslint"

export default typescriptEslint.config(
  {
    ignores: ["taskpane/dist/**", "taskpane/src/generated/**"],
  },
  eslint.configs.recommended,
  ...typescriptEslint.configs.recommended,
  {
    files: ["taskpane/src/**/*.{ts,tsx}", "taskpane/tests/**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-explicit-any": "error",
    },
  },
)
