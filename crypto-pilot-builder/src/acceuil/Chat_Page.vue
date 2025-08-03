<template>
  <div class="app-container">
    <!-- Bouton de déconnexion en haut à gauche -->
    <header class="chat-header">
      <button
        v-if="isAuthenticated"
        @click="handleLogout"
        class="logout-button"
        title="Se déconnecter"
      >
        <span class="logout-icon">🚪</span>
        Déconnexion
      </button>
      <router-link to="/" class="home-button" title="Retour à l'accueil">
        <span class="home-icon">🏠</span>
        Accueil
      </router-link>
      <router-link
        to="/memory"
        class="memory-button"
        title="Voir la mémoire de l'IA"
      >
        <span class="memory-icon">🧠</span>
        Mémoire IA
      </router-link>
    </header>

    <Wallet ref="walletComponent" />
    <ChatBot />
  </div>
</template>

<script setup>
import { ref, provide, computed } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import Wallet from "../components/wallet.vue";
import ChatBot from "../components/chatbot.vue";

const walletComponent = ref(null);
const store = useStore();
const router = useRouter();

// Computed properties pour l'authentification
const isAuthenticated = computed(() => store.getters["auth/isAuthenticated"]);

// Méthode de déconnexion
const handleLogout = async () => {
  await store.dispatch("auth/logout");
  router.push("/");
};

provide("walletFunctions", {
  sendTransaction: (recipient, amount) => {
    if (walletComponent.value) {
      return walletComponent.value.sendTransactionFromChat(recipient, amount);
    }
    throw new Error("Wallet non disponible");
  },
  getAddress: () => {
    return walletComponent.value?.address || null;
  },
  isConnected: () => {
    return !!walletComponent.value?.address;
  },
});
</script>

<style scoped>
.app-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background-color: #eef1f5;
  padding-top: 0rem;
}

.chat-header {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  gap: 10px;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #e74c3c;
  border: none;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
}

.logout-button:hover {
  background: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
}

.home-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  text-decoration: none;
}

.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.memory-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  border: none;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
  text-decoration: none;
}

.memory-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
}

.logout-icon,
.home-icon,
.memory-icon {
  font-size: 16px;
}
</style>
