import { ref, computed } from 'vue'
import { createWalletClient, custom, parseEther, formatEther } from 'viem'
import { mainnet } from 'viem/chains'

// Global wallet state
const walletAddress = ref('')
const isConnected = ref(false)
const isConnecting = ref(false)
const walletClient = ref(null)
const connectionError = ref('')

export function useWalletService() {
  // Computed
  const formattedAddress = computed(() => {
    if (!walletAddress.value) return ''
    return `${walletAddress.value.substring(0, 6)}...${walletAddress.value.substring(walletAddress.value.length - 4)}`
  })

  const hasMetaMask = computed(() => {
    return typeof window !== 'undefined' && window.ethereum && window.ethereum.isMetaMask
  })

  // Methods
  const connectWallet = async () => {
    if (!hasMetaMask.value) {
      connectionError.value = 'MetaMask n\'est pas installé. Veuillez l\'installer pour continuer.'
      return false
    }

    isConnecting.value = true
    connectionError.value = ''

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })

      if (accounts.length === 0) {
        throw new Error('Aucun compte sélectionné')
      }

      // Create wallet client
      walletClient.value = createWalletClient({
        chain: mainnet,
        transport: custom(window.ethereum)
      })

      walletAddress.value = accounts[0]
      isConnected.value = true

      // Listen for account changes
      window.ethereum.on('accountsChanged', handleAccountsChanged)
      window.ethereum.on('chainChanged', handleChainChanged)

      console.log('Wallet connected:', walletAddress.value)
      return true

    } catch (error) {
      console.error('Error connecting wallet:', error)
      connectionError.value = error.message || 'Erreur lors de la connexion au portefeuille'
      return false
    } finally {
      isConnecting.value = false
    }
  }

  const disconnectWallet = () => {
    walletAddress.value = ''
    isConnected.value = false
    walletClient.value = null
    connectionError.value = ''

    // Remove event listeners
    if (window.ethereum) {
      window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
      window.ethereum.removeListener('chainChanged', handleChainChanged)
    }

    console.log('Wallet disconnected')
  }

  const setManualAddress = (address) => {
    if (!address || !isValidAddress(address)) {
      connectionError.value = 'Adresse invalide'
      return false
    }

    walletAddress.value = address
    isConnected.value = true
    connectionError.value = ''
    
    console.log('Manual address set:', address)
    return true
  }

  const validateAddress = async () => {
    if (!walletAddress.value) {
      connectionError.value = 'Aucune adresse à valider'
      return false
    }

    try {
      // Simple validation - check if it's a valid Ethereum address
      if (!isValidAddress(walletAddress.value)) {
        throw new Error('Format d\'adresse invalide')
      }

      // You could add more validation here (e.g., check balance, verify on blockchain)
      console.log('Address validated:', walletAddress.value)
      return true

    } catch (error) {
      console.error('Error validating address:', error)
      connectionError.value = error.message || 'Erreur lors de la validation'
      return false
    }
  }

  const sendTransaction = async (to, amount) => {
    if (!isConnected.value || !walletClient.value) {
      throw new Error('Portefeuille non connecté')
    }

    if (!to || !amount) {
      throw new Error('Destinataire et montant requis')
    }

    if (!isValidAddress(to)) {
      throw new Error('Adresse de destinataire invalide')
    }

    try {
      const amountInWei = parseEther(amount.toString())
      
      const hash = await walletClient.value.sendTransaction({
        account: walletAddress.value,
        to: to,
        value: amountInWei
      })

      console.log('Transaction sent:', hash)
      
      return {
        hash,
        to,
        amount,
        from: walletAddress.value,
        timestamp: new Date().toISOString()
      }

    } catch (error) {
      console.error('Error sending transaction:', error)
      throw new Error(error.message || 'Erreur lors de l\'envoi de la transaction')
    }
  }

  const getBalance = async () => {
    if (!isConnected.value || !walletAddress.value) {
      return '0'
    }

    try {
      const balance = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [walletAddress.value, 'latest']
      })

      // Convert from wei to ether
      const balanceInEther = formatEther(BigInt(balance))
      return parseFloat(balanceInEther).toFixed(4)

    } catch (error) {
      console.error('Error getting balance:', error)
      return '0'
    }
  }

  const estimateGas = async (to, amount) => {
    if (!isConnected.value || !walletClient.value) {
      return '0'
    }

    try {
      const amountInWei = parseEther(amount.toString())
      
      const gasEstimate = await walletClient.value.estimateGas({
        account: walletAddress.value,
        to: to,
        value: amountInWei
      })

      // Get current gas price
      const gasPrice = await window.ethereum.request({
        method: 'eth_gasPrice'
      })

      // Calculate total gas cost in ether
      const gasCost = (gasEstimate * BigInt(gasPrice))
      return formatEther(gasCost)

    } catch (error) {
      console.error('Error estimating gas:', error)
      return '0'
    }
  }

  // Event handlers
  const handleAccountsChanged = (accounts) => {
    if (accounts.length === 0) {
      disconnectWallet()
    } else {
      walletAddress.value = accounts[0]
      console.log('Account changed:', accounts[0])
    }
  }

  const handleChainChanged = (chainId) => {
    console.log('Chain changed:', chainId)
    // You might want to handle chain changes here
    // For now, we'll just log it
  }

  // Utility functions
  const isValidAddress = (address) => {
    return /^0x[a-fA-F0-9]{40}$/.test(address)
  }

  // Auto-connect on page load if previously connected
  const autoConnect = async () => {
    if (!hasMetaMask.value) return

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_accounts'
      })

      if (accounts.length > 0) {
        walletClient.value = createWalletClient({
          chain: mainnet,
          transport: custom(window.ethereum)
        })

        walletAddress.value = accounts[0]
        isConnected.value = true

        // Set up event listeners
        window.ethereum.on('accountsChanged', handleAccountsChanged)
        window.ethereum.on('chainChanged', handleChainChanged)

        console.log('Auto-connected to wallet:', walletAddress.value)
      }
    } catch (error) {
      console.error('Error auto-connecting wallet:', error)
    }
  }

  // Initialize auto-connect
  if (typeof window !== 'undefined') {
    autoConnect()
  }

  return {
    // State
    walletAddress: readonly(walletAddress),
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    connectionError: readonly(connectionError),
    formattedAddress,
    hasMetaMask,

    // Methods
    connectWallet,
    disconnectWallet,
    setManualAddress,
    validateAddress,
    sendTransaction,
    getBalance,
    estimateGas,
    autoConnect
  }
}

// Helper function to make refs readonly
function readonly(ref) {
  return computed(() => ref.value)
}
