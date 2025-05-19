<script setup>
import { ref } from 'vue'

const address = ref(null)
const status = ref('')

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
function shortenAddress(addr) {
  if (!addr) return ''
  return addr.slice(0, 4) + '...' + addr.slice(-4)
}

</script>

<template>
  <div class="wallet-connect">
    <div class="right-align">
      <button @click="connectWallet" v-if="!address" class="connect-button">
        Connecter Wallet
      </button>
      <div v-else class="wallet-info">
        <span>💼 {{ shortenAddress(address) }}</span>
      </div>
    </div>
    <p v-if="status" class="status">{{ status }}</p>
  </div>
</template>

<style scoped>
.wallet-connect {
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

.right-align {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
}

.connect-button {
  background-color: #4caf50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.connect-button:hover {
  background-color: #43a047;
}

.wallet-info {
  background: #e0f2f1;
  padding: 8px 12px;
  border-radius: 6px;
  font-family: monospace;
  color: #00695c;
  font-size: small;
}

.status {
  margin-top: 0.5rem;
  text-align: right;
  font-size: 0.9rem;
  color: #555;
}
</style>
