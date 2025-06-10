// src/test/setup.js
import { vi } from 'vitest'

// Mock du fetch global
global.fetch = vi.fn()

// Mock de console pour éviter les logs pendant les tests
global.console = {
  ...console,
  log: vi.fn(),
  error: vi.fn(),
  warn: vi.fn(),
}

// Mock de l'objet window si nécessaire
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
  },
  writable: true,
})