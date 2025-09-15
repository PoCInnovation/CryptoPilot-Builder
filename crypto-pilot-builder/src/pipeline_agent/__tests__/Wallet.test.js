import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import Wallet from '../components/wallet.vue'
import { createWalletClient, custom } from 'viem'

// Mock de viem - déplacé en haut du fichier
vi.mock('viem', () => ({
  createWalletClient: vi.fn(),
  custom: vi.fn(),
  parseEther: vi.fn((amount) => `parsed_${amount}`),
}))

vi.mock('viem/chains', () => ({
  sepolia: { id: 11155111, name: 'Sepolia' }
}))

describe('Wallet.vue', () => {
  let wrapper
  let mockEthereum
  let mockWalletClient

  beforeEach(() => {
    // Reset des mocks
    vi.clearAllMocks()

    // Mock de window.ethereum
    mockEthereum = {
      request: vi.fn(),
      isMetaMask: true
    }

    // Mock du wallet client
    mockWalletClient = {
      sendTransaction: vi.fn()
    }

    // Configuration des mocks viem
    createWalletClient.mockReturnValue(mockWalletClient)
    custom.mockReturnValue('mocked-transport')

    // Simuler la présence de MetaMask
    global.window = {
      ethereum: mockEthereum
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(Wallet, {
      ...options
    })
  }

  describe('Initialisation du composant', () => {
    it('devrait se monter correctement', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('devrait afficher le composant wallet', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.wallet-connect').exists()).toBe(true)
    })

    it('devrait afficher le bouton de connexion initialement', () => {
      wrapper = createWrapper()
      const connectButton = wrapper.find('.connect-button')
      expect(connectButton.exists()).toBe(true)
      expect(connectButton.text()).toBe('🔗 Connecter')
    })

    it('ne devrait pas afficher les informations du wallet initialement', () => {
      wrapper = createWrapper()
      const walletInfo = wrapper.find('.wallet-info')
      expect(walletInfo.exists()).toBe(false)
    })
  })

  describe('Connexion au wallet', () => {
    it('devrait connecter le wallet avec succès', async () => {
      const testAddress = '0x1234567890123456789012345678901234567890'
      mockEthereum.request.mockResolvedValueOnce([testAddress])
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
      expect(mockEthereum.request).toHaveBeenCalledWith({
        method: 'eth_requestAccounts'
      })
      expect(wrapper.vm.address).toBe(testAddress)
      expect(wrapper.vm.status).toBe('✅ Wallet connecté automatiquement')
    })

    it('devrait afficher les informations du wallet après connexion', async () => {
      const testAddress = '0x1234567890123456789012345678901234567890'
      mockEthereum.request.mockResolvedValueOnce([testAddress])
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
      const walletInfo = wrapper.find('.wallet-info')
      const connectButton = wrapper.find('.connect-button')
      expect(walletInfo.exists()).toBe(true)
      expect(walletInfo.text()).toBe('0x12...7890')
      expect(connectButton.exists()).toBe(false)
    })

    it('devrait gérer l\'absence de MetaMask', async () => {
      global.window.ethereum = undefined
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
      expect(wrapper.vm.status).toBe('🦊 MetaMask non trouvé')
      expect(wrapper.vm.address).toBeNull()
    })

    it('devrait gérer les erreurs de connexion', async () => {
      mockEthereum.request.mockRejectedValueOnce(new Error('User rejected'))
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
      expect(wrapper.vm.status).toBe('✏️ Saisissez votre adresse manuellement')
      expect(wrapper.vm.address).toBeNull()
    })

    it('devrait déclencher la connexion au clic sur le bouton', async () => {
      const testAddress = '0x1234567890123456789012345678901234567890'
      mockEthereum.request.mockResolvedValueOnce([testAddress])
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
      expect(wrapper.vm.address).toBe(testAddress)
    })
  })

  describe('Envoi de transactions', () => {
    const testAddress = '0x1234567890123456789012345678901234567890'
    const recipientAddress = '0x9876543210987654321098765432109876543210'
    const amount = '0.1'
    const txHash = '0xabcdef123456789abcdef123456789abcdef123456'

    beforeEach(async () => {
      mockEthereum.request.mockResolvedValueOnce([testAddress])
      wrapper = createWrapper()
      await wrapper.vm.connectWallet()
      await nextTick()
    })

    it('devrait envoyer une transaction avec succès', async () => {
      mockWalletClient.sendTransaction.mockResolvedValueOnce(txHash)
      const result = await wrapper.vm.sendTransactionFromChat(recipientAddress, amount)
      expect(mockWalletClient.sendTransaction).toHaveBeenCalledWith({
        account: testAddress,
        to: recipientAddress,
        value: `parsed_${amount}`
      })
      expect(result.success).toBe(true)
      expect(result.hash).toBe(txHash)
      expect(wrapper.vm.status).toContain('✅ Tx envoyée')
      expect(wrapper.vm.isProcessing).toBe(false)
    })

    it('devrait gérer le rejet de la transaction par l\'utilisateur', async () => {
      const userRejectedError = new Error('User rejected the request')
      mockWalletClient.sendTransaction.mockRejectedValueOnce(userRejectedError)
      await expect(wrapper.vm.sendTransactionFromChat(recipientAddress, amount))
        .rejects.toThrow('❌ Rejeté')
      expect(wrapper.vm.status).toBe('❌ Rejeté')
      expect(wrapper.vm.isProcessing).toBe(false)
    })

    it('devrait gérer les fonds insuffisants', async () => {
      const insufficientFundsError = new Error('insufficient funds for intrinsic transaction cost')
      mockWalletClient.sendTransaction.mockRejectedValueOnce(insufficientFundsError)
      await expect(wrapper.vm.sendTransactionFromChat(recipientAddress, amount))
        .rejects.toThrow('💸 Fonds insuffisants')
      expect(wrapper.vm.status).toBe('💸 Fonds insuffisants')
    })

    it('devrait rejeter si le wallet n\'est pas connecté', async () => {
      wrapper.vm.address = null
      await expect(wrapper.vm.sendTransactionFromChat(recipientAddress, amount))
        .rejects.toThrow('Wallet non connecté')
    })

    it('devrait rejeter si les paramètres sont manquants', async () => {
      await expect(wrapper.vm.sendTransactionFromChat('', amount))
        .rejects.toThrow('Adresse ou montant manquant')
        await expect(wrapper.vm.sendTransactionFromChat(recipientAddress, ''))
        .rejects.toThrow('Adresse ou montant manquant')
    })
  })

  describe('Fonctions utilitaires', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('devrait raccourcir les adresses correctement', () => {
      const longAddress = '0x1234567890123456789012345678901234567890'
      const shortened = wrapper.vm.shortenAddress(longAddress)
      expect(shortened).toBe('0x12...7890')
    })

    it('devrait retourner une chaîne vide pour les adresses nulles', () => {
      expect(wrapper.vm.shortenAddress(null)).toBe('')
      expect(wrapper.vm.shortenAddress(undefined)).toBe('')
      expect(wrapper.vm.shortenAddress('')).toBe('')
    })

    it('devrait indiquer si le wallet est connecté', () => {
      expect(wrapper.vm.isConnected()).toBe(false)
      wrapper.vm.address = '0x1234567890123456789012345678901234567890'
      expect(wrapper.vm.isConnected()).toBe(true)
    })
  })

  describe('Interface utilisateur', () => {
    it('devrait afficher le statut quand il existe', async () => {
      wrapper = createWrapper()
      wrapper.vm.status = 'Test status message'
      await nextTick()
      const statusElement = wrapper.find('.status')
      expect(statusElement.exists()).toBe(true)
      expect(statusElement.text()).toBe('Test status message')
    })

    it('ne devrait pas afficher le statut quand il est vide', async () => {
      wrapper = createWrapper()
      wrapper.vm.status = ''
      await nextTick()
      const statusElement = wrapper.find('.status')
      expect(statusElement.exists()).toBe(false)
    })

    it('devrait appliquer les bonnes classes CSS', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.wallet-connect').exists()).toBe(true)
      expect(wrapper.find('.top-bar').exists()).toBe(true)
      expect(wrapper.find('.actions').exists()).toBe(true)
    })
  })
})