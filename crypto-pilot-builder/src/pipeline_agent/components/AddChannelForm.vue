<template>
  <form @submit.prevent="saveChannel" class="add-channel-form">
    <div class="form-group">
      <label>Type de canal</label>
      <select v-model="channelData.channel_type" @change="onChannelTypeChange">
        <option value="">Sélectionner un type</option>
        <option value="email">Email</option>
        <option value="webhook">Webhook</option>
        <option value="telegram">Telegram</option>
        <option value="discord">Discord</option>
      </select>
    </div>
    
    <!-- Configuration Email -->
    <div v-if="channelData.channel_type === 'email'" class="channel-config">
      <div class="form-group">
        <label>Adresse email</label>
        <input type="email" v-model="channelData.config.email" placeholder="votre@email.com" required />
      </div>
    </div>
    
    <!-- Configuration Webhook -->
    <div v-if="channelData.channel_type === 'webhook'" class="channel-config">
      <div class="form-group">
        <label>URL du webhook</label>
        <input type="url" v-model="channelData.config.webhook_url" placeholder="https://hooks.slack.com/..." required />
      </div>
      <div class="form-group">
        <label>Description</label>
        <input type="text" v-model="channelData.config.description" placeholder="Slack, Discord, etc." />
      </div>
    </div>
    
    <!-- Configuration Telegram -->
    <div v-if="channelData.channel_type === 'telegram'" class="channel-config">
      <div class="form-group">
        <label>Token du bot</label>
        <input type="text" v-model="channelData.config.bot_token" placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz" required />
        <small class="help-text">
          Obtenez le token depuis @BotFather sur Telegram
        </small>
      </div>
      <div class="form-group">
        <label>ID du chat</label>
        <input type="text" v-model="channelData.config.chat_id" placeholder="123456789" required />
        <small class="help-text">
          Utilisez @userinfobot pour obtenir votre ID
        </small>
      </div>
    </div>
    
    <!-- Configuration Discord -->
    <div v-if="channelData.channel_type === 'discord'" class="channel-config">
      <div class="form-group">
        <label>URL du webhook Discord</label>
        <input type="url" v-model="channelData.config.webhook_url" placeholder="https://discord.com/api/webhooks/..." required />
        <small class="help-text">
          Créez un webhook dans les paramètres de votre serveur Discord
        </small>
      </div>
      <div class="form-group">
        <label>Nom du canal</label>
        <input type="text" v-model="channelData.config.channel_name" placeholder="alertes-crypto" />
      </div>
    </div>
    
    <div class="form-group">
      <label>
        <input type="checkbox" v-model="channelData.is_active" />
        Activer le canal immédiatement
      </label>
    </div>
    
    <div class="form-actions">
      <button type="button" @click="$emit('cancel')" class="btn btn-secondary">
        Annuler
      </button>
      <button type="submit" class="btn btn-primary" :disabled="!isValid || isLoading">
        {{ isLoading ? 'Ajout...' : 'Ajouter le canal' }}
      </button>
    </div>
    
    <!-- Instructions d'aide -->
    <div v-if="channelData.channel_type" class="help-section">
      <h4>Instructions de configuration</h4>
      <div v-if="channelData.channel_type === 'email'" class="help-content">
        <p>Les alertes seront envoyées à l'adresse email spécifiée.</p>
      </div>
      
      <div v-if="channelData.channel_type === 'webhook'" class="help-content">
        <p>Configurez un webhook dans votre application (Slack, Discord, etc.) et collez l'URL ici.</p>
        <p>Les alertes seront envoyées au format JSON avec les détails de l'investissement.</p>
      </div>
      
      <div v-if="channelData.channel_type === 'telegram'" class="help-content">
        <ol>
          <li>Créez un bot avec @BotFather sur Telegram</li>
          <li>Copiez le token fourni</li>
          <li>Démarrez une conversation avec votre bot</li>
          <li>Utilisez @userinfobot pour obtenir votre ID utilisateur</li>
          <li>Collez le token et l'ID dans les champs ci-dessus</li>
        </ol>
      </div>
      
      <div v-if="channelData.channel_type === 'discord'" class="help-content">
        <ol>
          <li>Allez dans les paramètres de votre serveur Discord</li>
          <li>Créez un webhook dans le canal de votre choix</li>
          <li>Copiez l'URL du webhook</li>
          <li>Collez l'URL dans le champ ci-dessus</li>
        </ol>
      </div>
    </div>
  </form>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'AddChannelForm',
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const channelData = ref({
      channel_type: '',
      config: {},
      is_active: true
    })
    
    const isLoading = ref(false)
    
    const isValid = computed(() => {
      if (!channelData.value.channel_type) return false
      
      switch (channelData.value.channel_type) {
        case 'email':
          return channelData.value.config.email && channelData.value.config.email.includes('@')
        case 'webhook':
          return channelData.value.config.webhook_url && channelData.value.config.webhook_url.startsWith('http')
        case 'telegram':
          return channelData.value.config.bot_token && channelData.value.config.chat_id
        case 'discord':
          return channelData.value.config.webhook_url && channelData.value.config.webhook_url.startsWith('http')
        default:
          return false
      }
    })
    
    const onChannelTypeChange = () => {
      // Réinitialiser la configuration lors du changement de type
      channelData.value.config = {}
      
      // Initialiser avec des valeurs par défaut selon le type
      switch (channelData.value.channel_type) {
        case 'email':
          channelData.value.config = { email: '' }
          break
        case 'webhook':
          channelData.value.config = { webhook_url: '', description: '' }
          break
        case 'telegram':
          channelData.value.config = { bot_token: '', chat_id: '' }
          break
        case 'discord':
          channelData.value.config = { webhook_url: '', channel_name: '' }
          break
      }
    }
    
    const saveChannel = async () => {
      if (!isValid.value) return
      
      isLoading.value = true
      try {
        emit('save', { ...channelData.value })
      } catch (error) {
        console.error('Erreur lors de l\'ajout du canal:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      channelData,
      isLoading,
      isValid,
      onChannelTypeChange,
      saveChannel
    }
  }
}
</script>

<style scoped>
.add-channel-form {
  display: grid;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #34495e;
}

.form-group input,
.form-group select {
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 16px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.help-text {
  font-size: 14px;
  color: #7f8c8d;
  margin-top: 4px;
}

.channel-config {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.help-section {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.help-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.help-content {
  color: #34495e;
  line-height: 1.6;
}

.help-content p {
  margin: 0 0 12px 0;
}

.help-content ol {
  margin: 0;
  padding-left: 20px;
}

.help-content li {
  margin-bottom: 8px;
}
</style>
