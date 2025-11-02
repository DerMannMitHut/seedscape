// Flat-config for ESLint v9+
import pluginJs from "@eslint/js";
import globals from "globals";
import eslintPluginImport from "eslint-plugin-import";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
    // Ignore patterns (replaces .eslintignore)
    {
        ignores: ["dist/**", "node_modules/**", "coverage/**", "*.min.js"],
    },

    // Base JS recommended rules
    pluginJs.configs.recommended,

    // Project rules and environment
    {
        files: ["**/*.js"],
        languageOptions: {
            sourceType: "module",
            ecmaVersion: "latest",
            globals: {
                ...globals.browser,
                ...globals.es2021,
            },
        },
        plugins: {
            import: eslintPluginImport,
        },
        rules: {
            "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
            "no-console": "off",
            // In a no-bundler setup, module resolution may be non-standard
            "import/no-unresolved": "off",
        },
    },

    // Disable rules that conflict with Prettier
    eslintConfigPrettier,
];
