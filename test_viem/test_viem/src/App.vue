<script setup>
import { ref } from 'vue'
import { createWalletClient, custom, parseEther } from 'viem'
import { sepolia } from 'viem/chains'

const address = ref(null)
const recipient = ref('')
const status = ref('')
const isProcessing = ref(false)

async function connectWallet() {
  if (!window.ethereum) {
    status.value = "MetaMask non trouvé"
    return
  }
  try {
    const [account] = await window.ethereum.request({ method: 'eth_requestAccounts' })
    address.value = account
    status.value = "Connecté"
  } catch (err) {
    console.error(err)
    status.value = "Erreur lors de la connexion"
  }
}

async function sendTransaction() {
  if (!window.ethereum || !address.value || !recipient.value)
    return
  isProcessing.value = true
  status.value = "Demande de signature..."
  try {
    const transport = custom(window.ethereum)
    const walletClient = createWalletClient({
      chain: sepolia,
      transport
    })
    const hash = await walletClient.sendTransaction({
      account: address.value,
      to: recipient.value,
      value: parseEther('0.001')
    })
    status.value = `✅ Transaction envoyée : ${hash}`
    recipient.value = ''
  } catch (err) {
    console.error(err)

    if (err.message.includes('User rejected the request')) {
      status.value = '❌ Transaction annulée par l’utilisateur'
    } else if (err.message.includes('insufficient funds')) {
      status.value = '💸 Solde insuffisant'
    } else if (err.message.includes('invalid address') || err.message.includes('Address provided')) {
      status.value = '🚫 Adresse destinataire invalide'
    } else {
      status.value = `⚠️ Échec de l’envoi`
    }
  } finally {
    isProcessing.value = false
  }
}
</script>

<template>
  <div class="app">
    <h1>Connexion MetaMask avec Viem & Vue</h1>
    <button @click="connectWallet" v-if="!address">Se connecter à MetaMask</button>
    <div v-if="address">
      <p><strong>Adresse :</strong> {{ address }}</p>
      <div>
        <input v-model="recipient" placeholder="Adresse destinataire" />
        <button @click="sendTransaction" :disabled="isProcessing || !recipient">
          {{ isProcessing ? "Envoi..." : "Envoyer 0.001 ETH" }}
        </button>
      </div>
    </div>
    <p v-if="status">{{ status }}</p>
  </div>
</template>

<style scoped>
.app {
  max-width: 500px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-family: Arial, sans-serif;
}

input {
  padding: 8px;
  margin-right: 8px;
  width: 60%;
}

button {
  padding: 8px 12px;
}
</style>