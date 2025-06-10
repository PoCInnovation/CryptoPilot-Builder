import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()], // Permet de tester les composants Vue
  test: {
    environment: 'jsdom', // Simule un navigateur pour les tests DOM
    globals: true,        // Active les fonctions globales (describe, it, etc.)
  },
})