<script setup>
import { ref } from 'vue'
import { createWalletClient, custom, parseEther } from 'viem'
import { sepolia, mainnet } from 'viem/chains'

const address = ref(null)
const recipient = ref('')
const status = ref('')
const isProcessing = ref(false)
const manualAddress = ref('')
const showManualInput = ref(false)

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

function validateManualAddress() {
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

async function sendTransactionFromChat(recipientAddress, amountEth) {
  if (!window.ethereum || !address.value) {
    throw new Error('Wallet non connecté')
  }
  if (!recipientAddress || !amountEth) {
    throw new Error('Adresse ou montant manquant')
  }
  return await executeTransaction(recipientAddress, amountEth)
}

async function executeTransaction(recipientAddress, amountEth) {
  isProcessing.value = true
  status.value = "Signature..."
  try {
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({ chain: sepolia, transport })
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

async function executeSwap(transactionData) {
  if (!window.ethereum || !address.value) {
    throw new Error('Wallet non connecté')
  }

  if (!transactionData) {
    throw new Error('Données de transaction manquantes')
  }

  isProcessing.value = true
  status.value = "Signature du swap..."

  try {
    const transport = custom(window.ethereum)
    const chainId = transactionData.chainId || 1
    const selectedChain = chainId === 1 ? mainnet : (chainId === 11155111 ? sepolia : mainnet)
    const walletClient = createWalletClient({ chain: selectedChain, transport })

    const hash = await walletClient.sendTransaction({
      account: address.value,
      to: transactionData.to,
      value: BigInt(transactionData.value || "0"),
      data: transactionData.data,
      gas: transactionData.gasLimit ? BigInt(transactionData.gasLimit) : undefined,
      gasPrice: transactionData.gasPrice ? BigInt(transactionData.gasPrice) : undefined
    })

    status.value = `✅ Swap envoyé : ${hash.slice(0, 10)}...`
    return { success: true, hash, message: status.value }
  } catch (err) {
    let errorMessage
    if (err.message.includes('User rejected')) {
      errorMessage = '❌ Swap rejeté'
    } else if (err.message.includes('insufficient funds')) {
      errorMessage = '💸 Fonds insuffisants pour le swap'
    } else if (err.message.includes('execution reverted')) {
      errorMessage = '⚠️ Échec du swap (slippage ou liquidité)'
    } else {
      errorMessage = '⚠️ Erreur swap'
    }
    status.value = errorMessage
    throw new Error(errorMessage)
  } finally {
    isProcessing.value = false
  }
}

function shortenAddress(addr) {
  if (!addr) return ''
  return addr.slice(0, 4) + '...' + addr.slice(-4)
}

// Exposer les méthodes pour que le parent puisse les utiliser
defineExpose({
  sendTransactionFromChat,
  executeSwap,
  address,
  connectWallet,
  isConnected: () => !!address.value
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