<script setup>
import { ref } from 'vue'
import { createWalletClient, custom, parseEther } from 'viem'
import { sepolia } from 'viem/chains'

const address = ref(null)
const recipient = ref('')
const amount = ref('0.001')
const status = ref('')
const isProcessing = ref(false)

async function connectWallet() {
  if (!window.ethereum) {
    status.value = "🦊 MetaMask non trouvé"
    return
  }
  try {
    const [account] = await window.ethereum.request({ method: 'eth_requestAccounts' })
    address.value = account
  } catch (err) {
    console.error(err)
    status.value = "❌ Erreur lors de la connexion"
  }
}

async function sendTransaction() {
  if (!window.ethereum || !address.value || !recipient.value || !amount.value)
    return
  isProcessing.value = true
  status.value = "Signature..."
  try {
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({ chain: sepolia, transport })
    const hash = await walletClient.sendTransaction({
      account: address.value,
      to: recipient.value,
      value: parseEther(amount.value)
    })
    status.value = `✅ Tx envoyée : ${hash.slice(0, 10)}...`
    recipient.value = ''
  } catch (err) {
    console.error(err)
    if (err.message.includes('User rejected')) {
      status.value = '❌ Rejeté'
    } else if (err.message.includes('insufficient funds')) {
      status.value = '💸 Fonds insuffisants'
    } else {
      status.value = '⚠️ Erreur transaction'
    }
  } finally {
    isProcessing.value = false
  }
}

function shortenAddress(addr) {
  if (!addr) return ''
  return addr.slice(0, 4) + '...' + addr.slice(-4)
}
</script>

<template>
  <div class="wallet-connect">
    <div class="top-bar">
      <div v-if="address" class="wallet-info">{{ shortenAddress(address) }}</div>
      <div class="actions">
        <button @click="connectWallet" v-if="!address" class="connect-button">connect</button>
        <template v-else>
          <input v-model="recipient" placeholder="To" class="address-input" />
          <input v-model="amount" placeholder="ETH" class="amount-input" />
          <button @click="sendTransaction" :disabled="isProcessing || !recipient || !amount" class="send-button">
            Send
          </button>
        </template>
      </div>
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
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-left: auto;
}

.connect-button,
.send-button {
  background-color: #4caf50;
  color: white;
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.connect-button:hover,
.send-button:hover {
  background-color: #43a047;
}

.wallet-info {
  font-family: monospace;
  font-size: 0.9rem;
  background: #e0f2f1;
  padding: 6px 10px;
  border-radius: 6px;
  color: #00695c;
}

.address-input,
.amount-input {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 120px;
  font-size: 0.9rem;
}

.status {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #555;
  text-align: right;
}
</style>
