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
const NETWORK_CONFIG = {
  // Ethereum Mainnet
  'ETH': {
    chain: mainnet,
    nativeCurrency: 'ETH',
    tokens: {
      'USDC': {
        address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        decimals: 6,
        symbol: 'USDC'
      },
      'USDT': {
        address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        decimals: 6,
        symbol: 'USDT'
      },
      'DAI': {
        address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        decimals: 18,
        symbol: 'DAI'
      },
      'WETH': {
        address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        decimals: 18,
        symbol: 'WETH'
      }
    }
  },
  // Sepolia Testnet
  'SEPOLIA': {
    chain: sepolia,
    nativeCurrency: 'SEPOLIA',
    tokens: {
      'USDC': {
        address: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        decimals: 6,
        symbol: 'USDC'
      },
      'USDT': {
        address: '0x7169D38820dfd117C3FA1f22a697dBA58d90BA06',
        decimals: 6,
        symbol: 'USDT'
      },
      'DAI': {
        address: '0x68194a729C2450ad26072b3D33ADaCbcef39D574',
        decimals: 18,
        symbol: 'DAI'
      },
      'WETH': {
        address: '0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9',
        decimals: 18,
        symbol: 'WETH'
      },
      'LINK': {
        address: '0x779877A7B0D9E8603169DdbD7836e478b4624789',
        decimals: 18,
        symbol: 'LINK'
      },
      'UNI': {
        address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        decimals: 18,
        symbol: 'UNI'
      }
    }
  }
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
  if (NETWORK_CONFIG.SEPOLIA.tokens[currencyUpper]) {
    console.log(`🧪 ${currencyUpper} trouvé sur SEPOLIA (testnet gratuit)`)
    return 'SEPOLIA'
  }
  
  if (NETWORK_CONFIG.ETH.tokens[currencyUpper]) {
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
  
  const networkConfig = NETWORK_CONFIG[networkKey]
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
  
  const networkConfig = NETWORK_CONFIG[networkKey]
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
    status.value = "✅ Wallet connecté automatiquement"
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
  status.value = "✅ Adresse configurée manuellement"
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
    console.log('✅ Adresse wallet synchronisée avec le backend')
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
      status.value = "✅ Adresse chargée depuis le serveur"
      console.log('✅ Adresse wallet chargée depuis le backend')
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
  const networkConfig = NETWORK_CONFIG[networkKey]
  
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
    const networkConfig = NETWORK_CONFIG[networkKey]
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
    
    const networkConfig = NETWORK_CONFIG[networkKey]
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
    const networkConfig = NETWORK_CONFIG[networkKey]
    return [networkConfig.nativeCurrency, ...Object.keys(networkConfig.tokens)]
  }
  
  // Retourner tous les tokens de tous les réseaux
  const allTokens = new Set()
  Object.values(NETWORK_CONFIG).forEach(config => {
    allTokens.add(config.nativeCurrency)
    Object.keys(config.tokens).forEach(token => allTokens.add(token))
  })
  return Array.from(allTokens)
}

function shortenAddress(addr) {
  if (!addr) return ''
  return addr.slice(0, 4) + '...' + addr.slice(-4)
}

// Charger l'adresse depuis le backend au montage
onMounted(() => {
  loadWalletAddressFromBackend()
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
  getSupportedTokens
})
</script>

<template>
  <div class="wallet-connect">
    <div class="top-bar">
      <div class="actions">
        <button
          v-if="!address && !showManualInput"
          @click="connectWallet"
          class="connect-button"
        >
          🔗 Connecter
        </button>
        <button
          v-if="!address && !showManualInput"
          @click="showManualSetup"
          class="manual-button"
        >
          ✏️ Manuel
        </button>
        <button
          v-if="showManualInput && !address"
          @click="validateManualAddress"
          class="validate-button"
        >
          ✅ Valider
        </button>
        <button
          v-if="address"
          @click="changeWallet"
          class="change-button"
        >
          🔄 Changer
        </button>
      </div>
    </div>

    <div v-if="address" class="wallet-info">
      {{ shortenAddress(address) }}
    </div>

    <div v-if="showManualInput && !address" class="manual-input">
      <input
        v-model="manualAddress"
        placeholder="0x1234567890abcdef..."
        class="address-input-manual"
        @keyup.enter="validateManualAddress"
      />
      <small class="hint">Saisissez l'adresse du wallet (format 0x...)</small>
    </div>

    <p v-if="status" class="status">{{ status }}</p>
  </div>
</template>

<style scoped>
.wallet-connect {
  padding: 1rem;
  box-sizing: border-box;
  font-family: sans-serif;
  width: 100%;
}

.top-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
}

.actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.connect-button,
.manual-button,
.validate-button,
.change-button {
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.connect-button {
  background-color: #4caf50;
}

.connect-button:hover {
  background-color: #45a049;
}

.manual-button {
  background-color: #2196f3;
}

.manual-button:hover {
  background-color: #1976d2;
}

.validate-button {
  background-color: #ff9800;
}

.validate-button:hover {
  background-color: #f57c00;
}

.change-button {
  background-color: #9c27b0;
}

.change-button:hover {
  background-color: #7b1fa2;
}

.wallet-info {
  font-family: monospace;
  font-size: 0.9rem;
  background: #e8f5e8;
  padding: 8px 12px;
  border-radius: 6px;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
  margin-top: 1rem;
  text-align: center;
  width: 5%;
  margin-right: 0;
  margin-left: auto;
}

.manual-input {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.address-input-manual {
  padding: 10px;
  border: 2px solid #2196f3;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: monospace;
  width: 100%;
  box-sizing: border-box;
}

.address-input-manual:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.hint {
  color: #666;
  font-size: 0.8rem;
  margin-left: 4px;
}

.status {
  margin-top: 0.75rem;
  font-size: 0.9rem;
  color: #555;
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>