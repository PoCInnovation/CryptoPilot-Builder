<script setup>
import { ref, onMounted, watch } from 'vue'
import { createWalletClient, custom, parseEther, parseUnits, encodeFunctionData, getContract } from 'viem'
import { sepolia, mainnet } from 'viem/chains'
import apiService from '../services/apiService'

const address = ref(null)
const recipient = ref('')
const status = ref('')
const isProcessing = ref(false)
const manualAddress = ref('')
const showManualInput = ref(false)

// ERC-20 ABI pour les fonctions transfer et balanceOf
const ERC20_ABI = [
  {
    "constant": false,
    "inputs": [
      {
        "name": "_to",
        "type": "address"
      },
      {
        "name": "_value",
        "type": "uint256"
      }
    ],
    "name": "transfer",
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "payable": false,
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [
      {
        "name": "_owner",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "name": "balance",
        "type": "uint256"
      }
    ],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "decimals",
    "outputs": [
      {
        "name": "",
        "type": "uint8"
      }
    ],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  }
]

// Configuration des réseaux et tokens
const NETWORK_CONFIG = ref({
  // Ethereum Mainnet
  'ETH': {
    chain: mainnet,
    nativeCurrency: 'ETH',
    tokens: {}
  },
  // Sepolia Testnet
  'SEPOLIA': {
    chain: sepolia,
    nativeCurrency: 'SEPOLIA',
    tokens: {}
  }
})

// Fonction pour récupérer dynamiquement les tokens ERC-20
const loadTokensFromAPI = async (network = 'SEPOLIA') => {
  try {
    console.log(`🔄 Chargement des tokens pour ${network}...`)
    
    // Appel à l'API MCP pour récupérer les tokens
    const response = await apiService.callMCPTool('get_all_erc20_tokens', {
      chain_id: network === 'SEPOLIA' ? '11155111' : '1'
    })
    
    if (response && response.content) {
      // Parser la réponse pour extraire les informations des tokens
      const content = response.content
      
      // Extraire les adresses des tokens depuis la réponse
      const tokenMatches = content.match(/• ([A-Z]+) \(([^)]+)\)\n\s+Address: (0x[a-fA-F0-9]{40})\n\s+Decimals: (\d+)/g)
      
      if (tokenMatches) {
        const tokens = {}
        tokenMatches.forEach(match => {
          const parts = match.match(/• ([A-Z]+) \(([^)]+)\)\n\s+Address: (0x[a-fA-F0-9]{40})\n\s+Decimals: (\d+)/)
          if (parts) {
            const [, symbol, name, address, decimals] = parts
            tokens[symbol] = {
              address: address,
              decimals: parseInt(decimals),
              symbol: symbol,
              name: name
            }
          }
        })
        
        // Mettre à jour la configuration
        if (NETWORK_CONFIG.value[network]) {
          NETWORK_CONFIG.value[network].tokens = tokens
        }
        
        console.log(`✅ ${Object.keys(tokens).length} tokens chargés pour ${network}:`, tokens)
        return tokens
      }
    }
    
    // Fallback vers les tokens prédéfinis si l'API échoue
    console.warn('⚠️ Impossible de charger les tokens depuis l\'API, utilisation des tokens prédéfinis')
    return loadFallbackTokens(network)
    
  } catch (error) {
    console.error('❌ Erreur lors du chargement des tokens:', error)
    return loadFallbackTokens(network)
  }
}

// Fonction de fallback avec les tokens prédéfinis
const loadFallbackTokens = (network) => {
  const fallbackTokens = {
    'SEPOLIA': {
      'USDC': {
        address: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        decimals: 6,
        symbol: 'USDC',
        name: 'USD Coin'
      },
      'USDT': {
        address: '0x7169D38820dfd117C3FA1f22a697dBA58d90BA06',
        decimals: 6,
        symbol: 'USDT',
        name: 'Tether USD'
      },
      'DAI': {
        address: '0x68194a729C2450ad26072b3D33ADaCbcef39D574',
        decimals: 18,
        symbol: 'DAI',
        name: 'Dai Stablecoin'
      },
      'WETH': {
        address: '0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9',
        decimals: 18,
        symbol: 'WETH',
        name: 'Wrapped Ether'
      },
      'LINK': {
        address: '0x779877A7B0D9E8603169DdbD7836e478b4624789',
        decimals: 18,
        symbol: 'LINK',
        name: 'Chainlink'
      },
      'UNI': {
        address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        decimals: 18,
        symbol: 'UNI',
        name: 'Uniswap'
      }
    },
    'ETH': {
      'USDC': {
        address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        decimals: 6,
        symbol: 'USDC',
        name: 'USD Coin'
      },
      'USDT': {
        address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        decimals: 6,
        symbol: 'USDT',
        name: 'Tether USD'
      },
      'DAI': {
        address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        decimals: 18,
        symbol: 'DAI',
        name: 'Dai Stablecoin'
      },
      'WETH': {
        address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        decimals: 18,
        symbol: 'WETH',
        name: 'Wrapped Ether'
      }
    }
  }
  
  if (NETWORK_CONFIG.value[network]) {
    NETWORK_CONFIG.value[network].tokens = fallbackTokens[network] || {}
  }
  
  return fallbackTokens[network] || {}
}

// Fonction pour détecter le réseau selon la currency
function getNetworkFromCurrency(currency) {
  const currencyUpper = currency.toUpperCase()
  
  // ETH = Ethereum Mainnet (VRAIE CRYPTO CHÈRE !)
  if (currencyUpper === 'ETH') {
    return 'ETH'
  }
  
  // SEPOLIA = Sepolia Testnet
  if (currencyUpper === 'SEPOLIA') {
    return 'SEPOLIA'
  }
  
  // ⚠️ SÉCURITÉ : Pour les tokens ERC-20, utiliser SEPOLIA par défaut pour éviter les frais énormes !
  // Priorité : Sepolia d'abord (gratuit), puis mainnet seulement si pas trouvé
  if (NETWORK_CONFIG.value.SEPOLIA.tokens[currencyUpper]) {
    console.log(`🧪 ${currencyUpper} trouvé sur SEPOLIA (testnet gratuit)`)
    return 'SEPOLIA'
  }
  
  if (NETWORK_CONFIG.value.ETH.tokens[currencyUpper]) {
    console.log(`💰 ${currencyUpper} trouvé sur ETH MAINNET (ATTENTION: FRAIS ÉLEVÉS!)`)
    return 'ETH'
  }
  
  // Par défaut, SEPOLIA pour éviter les frais
  console.log(`🧪 Token ${currencyUpper} non trouvé, utilisation de SEPOLIA par sécurité`)
  return 'SEPOLIA'
}

// Fonction pour changer de réseau dans MetaMask
async function switchToNetwork(networkKey) {
  if (!window.ethereum) {
    throw new Error('MetaMask non trouvé')
  }
  
  const networkConfig = NETWORK_CONFIG.value[networkKey]
  const chainIdHex = `0x${networkConfig.chain.id.toString(16)}`
  
  try {
    // Essayer de basculer vers le réseau
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: chainIdHex }]
    })
    console.log(`✅ Basculé vers ${networkKey}`)
  } catch (switchError) {
    // Si le réseau n'existe pas, l'ajouter
    if (switchError.code === 4902 || switchError.code === -32603) {
      try {
        const networkParams = {
          chainId: chainIdHex,
          chainName: networkConfig.chain.name,
          nativeCurrency: {
            name: networkConfig.chain.nativeCurrency.name,
            symbol: networkConfig.chain.nativeCurrency.symbol,
            decimals: networkConfig.chain.nativeCurrency.decimals
          },
          rpcUrls: networkConfig.chain.rpcUrls.default.http,
          blockExplorerUrls: networkConfig.chain.blockExplorers?.default ? [networkConfig.chain.blockExplorers.default.url] : []
        }
        
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [networkParams]
        })
        console.log(`✅ Réseau ${networkKey} ajouté et activé`)
      } catch (addError) {
        console.error('❌ Erreur ajout réseau:', addError)
        throw new Error(`Impossible d'ajouter le réseau ${networkKey}`)
      }
    } else {
      console.error('❌ Erreur changement réseau:', switchError)
      throw new Error(`Impossible de basculer vers ${networkKey}`)
    }
  }
}

// Fonction pour ajouter un token ERC-20 dans MetaMask
async function addTokenToMetaMask(tokenSymbol, networkKey) {
  if (!window.ethereum) {
    console.error('MetaMask non trouvé')
    return false
  }
  
  const networkConfig = NETWORK_CONFIG.value[networkKey]
  const tokenInfo = networkConfig.tokens[tokenSymbol.toUpperCase()]
  
  if (!tokenInfo) {
    console.error(`Token ${tokenSymbol} non trouvé sur ${networkKey}`)
    return false
  }
  
  try {
    await window.ethereum.request({
      method: 'wallet_watchAsset',
      params: {
        type: 'ERC20',
        options: {
          address: tokenInfo.address,
          symbol: tokenInfo.symbol,
          decimals: tokenInfo.decimals,
          image: `https://cryptologos.cc/logos/${tokenSymbol.toLowerCase()}-${tokenSymbol.toLowerCase()}-logo.png`
        }
      }
    })
    
    console.log(`✅ Token ${tokenSymbol} proposé à MetaMask sur ${networkKey}`)
    return true
  } catch (error) {
    if (error.code === 4001) {
      console.log(`⚠️ Utilisateur a refusé l'ajout du token ${tokenSymbol}`)
    } else {
      console.error(`❌ Erreur ajout token ${tokenSymbol}:`, error)
    }
    return false
  }
}

async function connectWallet() {
  if (!window.ethereum) {
    status.value = "🦊 MetaMask non trouvé"
    return
  }

  try {
    const [account] = await window.ethereum.request({ method: 'eth_requestAccounts' })
    address.value = account
    status.value = "Wallet connecté automatiquement"
    showManualInput.value = false
    // Synchroniser avec le backend
    await syncWalletAddressWithBackend()
  } catch (err) {
    console.error(err)
    status.value = "❌ Erreur lors de la connexion automatique"
    showManualSetup()
  }
}

function showManualSetup() {
  showManualInput.value = true
  status.value = "✏️ Saisissez votre adresse manuellement"
}

async function validateManualAddress() {
  if (!manualAddress.value) {
    status.value = "❌ Veuillez saisir une adresse"
    return
  }
  if (!isValidAddress(manualAddress.value)) {
    status.value = "❌ Adresse invalide (format 0x...)"
    return
  }
  address.value = manualAddress.value
  status.value = "Adresse configurée manuellement"
  showManualInput.value = false
  // Synchroniser avec le backend
  await syncWalletAddressWithBackend()
}

function changeWallet() {
  address.value = null
  manualAddress.value = ''
  showManualInput.value = false
  status.value = "🔄 Prêt pour une nouvelle connexion"
}

function isValidAddress(addr) {
  return /^0x[a-fA-F0-9]{40}$/.test(addr)
}

// Synchroniser l'adresse avec le backend
async function syncWalletAddressWithBackend() {
  if (!address.value) return
  
  try {
    await apiService.request('/wallet-address', {
      method: 'PUT',
      body: {
        wallet_address: address.value
      }
    })
    console.log('Adresse wallet synchronisée avec le backend')
  } catch (error) {
    console.error('❌ Erreur synchronisation wallet:', error)
  }
}

// Charger l'adresse depuis le backend
async function loadWalletAddressFromBackend() {
  try {
    const response = await apiService.request('/wallet-address')
    if (response.wallet_address) {
      address.value = response.wallet_address
      status.value = " Adresse chargée depuis le serveur"
      console.log('Adresse wallet chargée depuis le backend')
    }
  } catch (error) {
    console.log('ℹ️ Aucune adresse wallet configurée sur le serveur')
  }
}

async function sendTransactionFromChat(recipientAddress, amount, tokenSymbol = 'ETH') {
  if (!window.ethereum || !address.value) {
    throw new Error('Wallet non connecté')
  }
  if (!recipientAddress || !amount) {
    throw new Error('Adresse ou montant manquant')
  }
  
  // Détecter le réseau selon la currency
  const networkKey = getNetworkFromCurrency(tokenSymbol)
  const networkConfig = NETWORK_CONFIG.value[networkKey]
  
  console.log(`🌐 Réseau détecté pour ${tokenSymbol}: ${networkKey}`)
  
  // Basculer automatiquement vers le bon réseau
  status.value = `🔄 Basculement vers ${networkKey}...`
  try {
    await switchToNetwork(networkKey)
    status.value = `✅ Connecté à ${networkKey}`
  } catch (error) {
    status.value = `❌ Erreur réseau: ${error.message}`
    throw error
  }
  
  // Déterminer si c'est une transaction native ou ERC-20
  if (tokenSymbol.toUpperCase() === networkConfig.nativeCurrency) {
    return await executeTransaction(recipientAddress, amount, networkConfig.chain)
  } else {
    return await executeERC20Transaction(recipientAddress, amount, tokenSymbol, networkKey)
  }
}

async function executeTransaction(recipientAddress, amountEth, chain = sepolia) {
  isProcessing.value = true
  status.value = "Signature..."
  try {
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({ chain, transport })
    const hash = await walletClient.sendTransaction({
      account: address.value,
      to: recipientAddress,
      value: parseEther(amountEth.toString())
    })
    status.value = `✅ Tx envoyée : ${hash.slice(0, 10)}...`
    if (recipientAddress === recipient.value) {
      recipient.value = ''
    }
    return { success: true, hash, message: status.value }
  } catch (err) {
    console.error(err)
    let errorMessage
    if (err.message.includes('User rejected')) {
      errorMessage = '❌ Rejeté'
    } else if (err.message.includes('insufficient funds')) {
      errorMessage = '💸 Fonds insuffisants'
    } else {
      errorMessage = '⚠️ Erreur transaction'
    }
    status.value = errorMessage
    throw new Error(errorMessage)
  } finally {
    isProcessing.value = false
  }
}

async function executeERC20Transaction(recipientAddress, amount, tokenSymbol, networkKey = 'SEPOLIA') {
  isProcessing.value = true
  status.value = "Signature token..."
  
  try {
    const networkConfig = NETWORK_CONFIG.value[networkKey]
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({ chain: networkConfig.chain, transport })
    
    // Récupérer les informations du token
    const tokenInfo = networkConfig.tokens[tokenSymbol.toUpperCase()]
    if (!tokenInfo) {
      throw new Error(`Token ${tokenSymbol} non supporté sur ${networkKey}`)
    }
    
    // Proposer d'ajouter le token à MetaMask (surtout pour Sepolia)
    if (networkKey === 'SEPOLIA') {
      status.value = `🪙 Ajout ${tokenSymbol} à MetaMask...`
      await addTokenToMetaMask(tokenSymbol, networkKey)
    }
    
    status.value = "Signature token..."
    
    // Convertir le montant selon les décimales du token
    const amountInWei = parseUnits(amount.toString(), tokenInfo.decimals)
    
    // Encoder les données de la fonction transfer
    const data = encodeFunctionData({
      abi: ERC20_ABI,
      functionName: 'transfer',
      args: [recipientAddress, amountInWei]
    })
    
    // Envoyer la transaction
    const hash = await walletClient.sendTransaction({
      account: address.value,
      to: tokenInfo.address,
      data: data,
      value: 0n // Pas de valeur pour les tokens ERC-20
    })
    
    status.value = `✅ Tx ${tokenSymbol} envoyée : ${hash.slice(0, 10)}...`
    if (recipientAddress === recipient.value) {
      recipient.value = ''
    }
    return { success: true, hash, message: status.value, token: tokenSymbol }
    
  } catch (err) {
    console.error(err)
    let errorMessage
    if (err.message.includes('User rejected')) {
      errorMessage = '❌ Rejeté'
    } else if (err.message.includes('insufficient funds') || err.message.includes('ERC20: transfer amount exceeds balance')) {
      errorMessage = `💸 Fonds ${tokenSymbol} insuffisants`
    } else if (err.message.includes('Token')) {
      errorMessage = err.message
    } else {
      errorMessage = '⚠️ Erreur transaction token'
    }
    status.value = errorMessage
    throw new Error(errorMessage)
  } finally {
    isProcessing.value = false
  }
}

// Fonction pour obtenir le solde d'un token ERC-20
async function getTokenBalance(tokenSymbol, networkKey = null) {
  if (!address.value) return '0'
  
  try {
    // Auto-détecter le réseau si non spécifié
    if (!networkKey) {
      networkKey = getNetworkFromCurrency(tokenSymbol)
    }
    
    const networkConfig = NETWORK_CONFIG.value[networkKey]
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({ chain: networkConfig.chain, transport })
    
    const tokenInfo = networkConfig.tokens[tokenSymbol.toUpperCase()]
    if (!tokenInfo) {
      throw new Error(`Token ${tokenSymbol} non supporté sur ${networkKey}`)
    }
    
    const contract = getContract({
      address: tokenInfo.address,
      abi: ERC20_ABI,
      client: walletClient
    })
    
    const balance = await contract.read.balanceOf([address.value])
    const decimals = await contract.read.decimals()
    
    // Convertir le solde en format lisible
    const balanceInUnits = balance / (10n ** BigInt(decimals))
    return balanceInUnits.toString()
    
  } catch (error) {
    console.error(`Erreur récupération solde ${tokenSymbol}:`, error)
    return '0'
  }
}

// Fonction pour obtenir la liste des tokens supportés
function getSupportedTokens(networkKey = null) {
  if (networkKey) {
    const networkConfig = NETWORK_CONFIG.value[networkKey]
    return [networkConfig.nativeCurrency, ...Object.keys(networkConfig.tokens)]
  }
  
  // Retourner tous les tokens de tous les réseaux
  const allTokens = new Set()
  Object.values(NETWORK_CONFIG.value).forEach(config => {
    allTokens.add(config.nativeCurrency)
    Object.keys(config.tokens).forEach(token => allTokens.add(token))
  })
  return Array.from(allTokens)
}

// Fonction pour exécuter un swap
async function executeSwap(transactionData) {
  if (!address.value) {
    throw new Error('Wallet non connecté')
  }
  
  if (!window.ethereum) {
    throw new Error('MetaMask non trouvé')
  }
  
  try {
    console.log('🔄 Exécution du swap avec les données:', transactionData)
    
    // Extraire les données de transaction
    const { to, data, value, gasLimit, gasPrice, chainId } = transactionData
    
    // Convertir le chainId au format hexadécimal si nécessaire
    let targetChainId = chainId
    if (typeof chainId === 'string' && !chainId.startsWith('0x')) {
      // Convertir de décimal à hexadécimal
      targetChainId = '0x' + parseInt(chainId).toString(16)
    } else if (typeof chainId === 'number') {
      // Convertir de nombre à hexadécimal
      targetChainId = '0x' + chainId.toString(16)
    }
    
    console.log(`🎯 ChainId cible: ${targetChainId}`)
    
    // Basculer vers la bonne chaîne si nécessaire
    const currentChainId = await window.ethereum.request({ method: 'eth_chainId' })
    console.log(`📍 ChainId actuel: ${currentChainId}`)
    
    if (currentChainId !== targetChainId) {
      console.log(`🔄 Basculement vers la chaîne ${targetChainId}...`)
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: targetChainId }]
      })
    }
    
    // Préparer les paramètres de transaction
    const txParams = {
      from: address.value,
      to: to,
      data: data,
      value: value || '0x0'
    }
    
    // Option 1: Utiliser les frais de gaz calculés par Li.Fi (recommandé pour les swaps)
    // if (gasLimit) {
    //   txParams.gasLimit = gasLimit
    // }
    // if (gasPrice) {
    //   txParams.gasPrice = gasPrice
    // }
    
    // Option 2: Laisser MetaMask calculer les frais (comme les transactions normales)
    // Pas de gasLimit/gasPrice = MetaMask calcule automatiquement
    
    console.log('📝 Paramètres de transaction:', txParams)
    
    // Envoyer la transaction
    const hash = await window.ethereum.request({
      method: 'eth_sendTransaction',
      params: [txParams]
    })
    
    console.log('✅ Transaction swap envoyée:', hash)
    return { success: true, hash }
    
  } catch (error) {
    console.error('❌ Erreur lors de l\'exécution du swap:', error)
    throw error
  }
}

// Fonction pour exécuter un swap natif sur Sepolia (sans Li.Fi)
async function executeNativeSwap(fromToken, toToken, amount, fromAddress) {
  console.log(`🔄 Swap natif sur Sepolia: ${amount} ${fromToken} → ${toToken}`)
  
  try {
    // Vérifier que nous sommes sur Sepolia
    const currentChainId = await window.ethereum.request({ method: 'eth_chainId' })
    if (currentChainId !== '0xaa36a7') { // Sepolia chainId
      throw new Error('Ce swap natif nécessite d\'être sur Sepolia')
    }
    
    // Pour l'instant, utiliser une approche simple : transfert direct
    // Dans une vraie implémentation, on utiliserait un DEX comme Uniswap
    if (fromToken === 'ETH' && toToken === 'USDC') {
      // Simuler un swap ETH → USDC en envoyant l'ETH à un contrat de swap
      const swapContractAddress = '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238' // USDC sur Sepolia
      
      const hash = await window.ethereum.request({
        method: 'eth_sendTransaction',
        params: [{
          from: fromAddress,
          to: swapContractAddress,
          value: parseEther(amount).toString(16), // Convertir en hex
          data: '0x' // Pas de données pour un simple transfert
        }]
      })
      
      console.log('✅ Swap natif exécuté:', hash)
      return { success: true, hash, method: 'native_sepolia' }
    }
    
    throw new Error(`Swap natif ${fromToken} → ${toToken} non encore implémenté`)
    
  } catch (error) {
    console.error('❌ Erreur swap natif:', error)
    throw error
  }
}

function shortenAddress(addr) {
  if (!addr) return ''
  return addr.slice(0, 4) + '...' + addr.slice(-4)
}

// Charger l'adresse depuis le backend au montage
onMounted(async () => {
  loadWalletAddressFromBackend()
  
  // Charger dynamiquement les tokens ERC-20
  console.log('🔄 Chargement des tokens ERC-20...')
  await loadTokensFromAPI('SEPOLIA')
  await loadTokensFromAPI('ETH')
  console.log('✅ Tokens ERC-20 chargés')
})

// Surveiller les changements d'adresse pour charger les soldes
watch(address, (newAddress) => {
  if (newAddress) {
    console.log('💼 Nouvelle adresse connectée:', newAddress)
  }
})

// Exposer les méthodes pour que le parent puisse les utiliser
defineExpose({
  sendTransactionFromChat,
  address,
  connectWallet,
  isConnected: () => !!address.value,
  getTokenBalance,
  getSupportedTokens,
  executeSwap,
  getAddress: () => address.value
})
</script>

<template>
  <div class="wallet-connect">
    <!-- État connecté avec adresse -->
    <div v-if="address" class="wallet-connected">
      <div class="wallet-actions">
        <button @click="changeWallet" class="change-button">
          <span class="button-icon">🔄</span>
          <span class="button-text">Changer</span>
        </button>
      </div>
      
      <div class="wallet-address">
        <span class="address-label">Adresse</span>
        <span class="address-value">{{ shortenAddress(address) }}</span>
      </div>
      
      <div v-if="status" class="status-message">
        <span class="status-icon">✅</span>
        <span class="status-text">{{ status }}</span>
      </div>
    </div>

    <!-- État non connecté -->
    <div v-else class="wallet-disconnected">
      <div class="connection-actions">
        <button @click="connectWallet" class="connect-button">
          <span class="button-icon">🔗</span>
          <span class="button-text">Connecter</span>
        </button>
        <button @click="showManualSetup" class="manual-button">
          <span class="button-icon">✏️</span>
          <span class="button-text">Manuel</span>
        </button>
      </div>

      <!-- Saisie manuelle -->
      <div v-if="showManualInput" class="manual-input">
        <div class="input-group">
          <input
            v-model="manualAddress"
            placeholder="0x1234567890abcdef..."
            class="address-input-manual"
            @keyup.enter="validateManualAddress"
          />
          <button @click="validateManualAddress" class="validate-button">
            <span class="button-icon">✅</span>
            <span class="button-text">Valider</span>
          </button>
        </div>
        <small class="hint">Saisissez l'adresse du wallet (format 0x...)</small>
      </div>

      <div v-if="status" class="status-message">
        <span class="status-icon">ℹ️</span>
        <span class="status-text">{{ status }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wallet-connect {
  padding: 1.5rem;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100%;
}

/* État connecté */
.wallet-connected {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.wallet-actions {
  display: flex;
  gap: 0.5rem;
}

.wallet-address {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 120px;
}

.address-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.address-value {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.9rem;
  color: #ffffff;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
}

/* État non connecté */
.wallet-disconnected {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.connection-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Boutons communs */
.connect-button,
.manual-button,
.validate-button,
.change-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: none;
  letter-spacing: 0.25px;
  position: relative;
  overflow: hidden;
}

.connect-button {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.connect-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.manual-button {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.manual-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
}

.validate-button {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

.validate-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}

.change-button {
  background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
}

.change-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(156, 39, 176, 0.4);
}

.button-icon {
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.button-text {
  font-weight: 600;
}

/* Saisie manuelle */
.manual-input {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.input-group {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.address-input-manual {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.address-input-manual::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.address-input-manual:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

.hint {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  text-align: center;
  font-style: italic;
}

/* Messages de statut */
.status-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  color: #2e7d32;
  font-weight: 500;
  margin-top: 0.5rem;
}

.status-icon {
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.status-text {
  font-size: 0.9rem;
  color: #555;
}

/* Responsive */
@media (max-width: 768px) {
  .wallet-connect {
    padding: 1rem;
  }
  
  .wallet-connected {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .connection-actions {
    flex-direction: column;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .wallet-address {
    text-align: center;
  }
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.wallet-connected,
.wallet-disconnected {
  animation: fadeInUp 0.5s ease-out;
}

/* Effet de brillance sur les boutons */
.connect-button::before,
.manual-button::before,
.validate-button::before,
.change-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.connect-button:hover::before,
.manual-button:hover::before,
.validate-button:hover::before,
.change-button:hover::before {
  left: 100%;
}
</style>