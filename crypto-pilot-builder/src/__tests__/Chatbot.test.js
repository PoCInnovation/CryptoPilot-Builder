import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import Chatbot from '../components/chatbot.vue'

// Mock des composants enfants
const mockChatSidebar = {
  template: '<div data-testid="chat-sidebar">Chat Sidebar</div>',
  props: ['chats', 'selectedChat'],
  emits: ['select-chat', 'add-chat']
}

const mockChatMessages = {
  template: '<div data-testid="chat-messages">Chat Messages</div>',
  props: ['messages', 'isLoading']
}

const mockChatInput = {
  template: '<div data-testid="chat-input">Chat Input</div>',
  emits: ['send-message']
}

// Mock du router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

describe('Chatbot.vue', () => {
  let wrapper
  let mockWalletFunctions

  beforeEach(() => {
    // Reset des mocks
    vi.clearAllMocks()
    
    // Mock de fetch
    global.fetch = vi.fn()
    
    // Mock des wallet functions
    mockWalletFunctions = {
      isConnected: vi.fn(() => true),
      getAddress: vi.fn(() => '0x1234567890123456789012345678901234567890'),
      sendTransaction: vi.fn(() => Promise.resolve({ hash: '0xabcdef123456' }))
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(Chatbot, {
      global: {
        components: {
          ChatSidebar: mockChatSidebar,
          ChatMessages: mockChatMessages,
          ChatInput: mockChatInput,
          'router-link': {
            template: '<a><slot /></a>',
            props: ['to']
          }
        },
        provide: {
          walletFunctions: mockWalletFunctions
        },
        mocks: {
          $router: mockRouter,
          $route: { path: '/chat' }
        }
      },
      ...options
    })
  }

  describe('Initialisation du composant', () => {
    it('devrait se monter correctement', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('devrait afficher les composants enfants', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })

      wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 0))
      expect(wrapper.findComponent(mockChatSidebar).exists()).toBe(true)
      expect(wrapper.findComponent(mockChatMessages).exists()).toBe(true)
      expect(wrapper.findComponent(mockChatInput).exists()).toBe(true)
    })

    it('devrait avoir un message initial', () => {
      wrapper = createWrapper()
      const messages = wrapper.vm.messages
      expect(messages).toHaveLength(1)
      expect(messages[0].text).toContain('Bonjour !')
      expect(messages[0].isUser).toBe(false)
    })

    it('devrait créer une nouvelle session au montage', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })
      wrapper = createWrapper()
      await nextTick()
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/new-session',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      )
    })
  })

  describe('Gestion des messages', () => {
    beforeEach(async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })
      wrapper = createWrapper()
      await nextTick()
    })

    it('devrait envoyer un message utilisateur', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          response: 'Réponse du bot',
          session_id: 'test-session-123'
        })
      })
      const testMessage = 'Bonjour, comment ça va ?'
      await wrapper.vm.sendMessage(testMessage)
      const messages = wrapper.vm.messages
      expect(messages.some(msg => msg.text === testMessage && msg.isUser === true)).toBe(true)
    })

    it('devrait gérer les réponses du bot', async () => {
      const botResponse = 'Réponse du chatbot'
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          response: botResponse,
          session_id: 'test-session-123'
        })
      })
      await wrapper.vm.sendMessage('Test message')
      await nextTick()
      const messages = wrapper.vm.messages
      expect(messages.some(msg => msg.text === botResponse && msg.isUser === false)).toBe(true)
    })

    it('devrait gérer les erreurs de l\'API', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Erreur réseau'))

      await wrapper.vm.sendMessage('Test message')
      await nextTick()

      const messages = wrapper.vm.messages
      expect(messages.some(msg => msg.text.includes('Erreur de communication'))).toBe(true)
    })

    it('ne devrait pas envoyer de messages vides', async () => {
      vi.clearAllMocks()
      const initialMessageCount = wrapper.vm.messages.length
      await wrapper.vm.sendMessage('')
      await wrapper.vm.sendMessage('   ')

      expect(wrapper.vm.messages).toHaveLength(initialMessageCount)
      expect(global.fetch).not.toHaveBeenCalled()
    })
  })

  describe('Gestion des transactions', () => {
    beforeEach(async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })
      wrapper = createWrapper()
      await nextTick()
    })

    it('devrait détecter une demande de transaction', async () => {
      const transactionRequest = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          response: 'Transaction détectée',
          transaction_request: transactionRequest,
          session_id: 'test-session-123'
        })
      })

      await wrapper.vm.sendMessage('Envoie 0.1 ETH à 0x1234567890123456789012345678901234567890')
      await nextTick()

      expect(wrapper.vm.pendingTransaction).toEqual(transactionRequest)
    })

    it('devrait afficher la modal de confirmation', async () => {
      wrapper.vm.pendingTransaction = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }
      await nextTick()

      const modal = wrapper.find('.transaction-modal-overlay')
      expect(modal.exists()).toBe(true)

      const confirmBtn = wrapper.find('.confirm-btn')
      const cancelBtn = wrapper.find('.cancel-btn')
      expect(confirmBtn.exists()).toBe(true)
      expect(cancelBtn.exists()).toBe(true)
    })

    it('devrait confirmer une transaction', async () => {
      wrapper.vm.pendingTransaction = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })
      await wrapper.vm.confirmTransaction()
      expect(mockWalletFunctions.sendTransaction).toHaveBeenCalledWith(
        '0x1234567890123456789012345678901234567890',
        '0.1'
      )
      expect(wrapper.vm.pendingTransaction).toBeNull()
    })

    it('devrait annuler une transaction', async () => {
      wrapper.vm.pendingTransaction = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })

      await wrapper.vm.cancelTransaction()

      expect(wrapper.vm.pendingTransaction).toBeNull()
      const messages = wrapper.vm.messages
      expect(messages.some(msg => msg.text.includes('Transaction annulée'))).toBe(true)
    })

    it('devrait gérer les erreurs de wallet non connecté', async () => {
      mockWalletFunctions.isConnected.mockReturnValue(false)
      
      wrapper.vm.pendingTransaction = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }

      await wrapper.vm.confirmTransaction()

      const messages = wrapper.vm.messages
      expect(messages.some(msg => msg.text.includes('Wallet non connecté'))).toBe(true)
      expect(wrapper.vm.pendingTransaction).toBeNull()
    })
  })

  describe('Gestion des chats', () => {
    beforeEach(async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })
      wrapper = createWrapper()
      await nextTick()
    })

    it('devrait créer un nouveau chat', async () => {
      const initialChatCount = wrapper.vm.chats.length
      await wrapper.vm.addNewChat()

      expect(wrapper.vm.chats.length).toBeGreaterThan(initialChatCount)
    })

    it('devrait sélectionner un chat existant', async () => {
      wrapper.vm.chats.push('Test Chat')
      wrapper.vm.chatSessions['Test Chat'] = {
        sessionId: 'test-session-456',
        messages: [{ text: 'Test message', isUser: false }]
      }

      wrapper.vm.selectChat(wrapper.vm.chats.length - 1)

      expect(wrapper.vm.currentSessionId).toBe('test-session-456')
      expect(wrapper.vm.messages).toEqual([{ text: 'Test message', isUser: false }])
    })
  })

  describe('Fonctions utilitaires', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('devrait vérifier le statut du wallet', () => {
      const status = wrapper.vm.checkWalletStatus()
      expect(status.connected).toBe(true)
      expect(status.address).toBe('0x1234567890123456789012345678901234567890')
    })

    it('devrait gérer l\'absence de wallet', () => {
      wrapper = createWrapper({
        global: {
          components: {
            ChatSidebar: mockChatSidebar,
            ChatMessages: mockChatMessages,
            ChatInput: mockChatInput,
            'router-link': {
              template: '<a><slot /></a>',
              props: ['to']
            }
          },
          provide: {
            walletFunctions: null
          },
          mocks: {
            $router: mockRouter,
            $route: { path: '/chat' }
          }
        }
      })
      
      const status = wrapper.vm.checkWalletStatus()
      
      expect(status.connected).toBe(false)
      expect(status.error).toBe('Wallet non disponible')
    })
  })

  describe('Interface utilisateur', () => {
    beforeEach(async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-session-123' })
      })
      wrapper = createWrapper()
      await nextTick()
    })

    it('devrait afficher l\'en-tête avec l\'ID de session', async () => {
      wrapper.vm.currentSessionId = 'test-session-123456789'
      await nextTick()

      const header = wrapper.find('.chat-header h3')
      expect(header.text()).toContain('test-ses...')
    })

    it('devrait fermer la modal en cliquant sur l\'overlay', async () => {
      wrapper.vm.pendingTransaction = {
        recipient: '0x1234567890123456789012345678901234567890',
        amount: '0.1',
        currency: 'eth'
      }
      await nextTick()

      const overlay = wrapper.find('.transaction-modal-overlay')
      await overlay.trigger('click')

      expect(wrapper.vm.pendingTransaction).toBeNull()
    })
  })
})