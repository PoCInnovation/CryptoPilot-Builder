import js from "@eslint/js";
import globals from "globals";
import pluginVue from "eslint-plugin-vue";
import { defineConfig } from "eslint/config";

export default defineConfig([
  // Configuration de base pour JavaScript
  js.configs.recommended,

  // Configuration pour les fichiers Node.js (main.js, vite.config.js, etc.)
  {
    files: ["main.js", "vite.config.js", "**/*.config.js"],
    languageOptions: {
      globals: globals.node
    }
  },

  // Configuration pour les tests
  {
    files: ["**/*.test.js", "**/tests/**/*.js", "**/setup.js"],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.jest
      }
    }
  },

  // Configuration pour les fichiers Vue et JS côté client
  {
    files: ["src/**/*.{js,vue}"],
    languageOptions: {
      globals: globals.browser
    }
  },

  // Configuration pour les fichiers de couverture et utilitaires navigateur
  {
    files: ["coverage/**/*.js", "**/block-navigation.js", "**/sorter.js"],
    languageOptions: {
      globals: globals.browser
    }
  },

  // Configuration Vue
  ...pluginVue.configs["flat/essential"],

  // Règles personnalisées
  {
    files: ["**/*.vue"],
    rules: {
      "vue/multi-word-component-names": "off",
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
    }
  },

  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/venv/**",
      "**/.git/**",
      "**/python/venv/**",
      "**/coverage/**",
      "*.log",
      ".DS_Store",
      "**/*.min.js",
      "**/vendor/**",
      "**/.nyc_output/**"
    ]
  }
]);