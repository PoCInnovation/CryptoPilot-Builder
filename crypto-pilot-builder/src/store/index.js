import { createStore } from 'vuex'

const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem('aiConfig')
    return saved ? JSON.parse(saved) : { selectedModel: '', apiKey: '', prompt: '' }
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error)
    return { selectedModel: '', apiKey: '', prompt: '' }
  }
}

const saveToStorage = (config) => {
  try {
    localStorage.setItem('aiConfig', JSON.stringify(config))
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error)
  }
}

export default createStore({
  state: {
    aiConfig: loadFromStorage()
  },
  mutations: {
    SET_AI_CONFIG(state, config) {
      state.aiConfig = { ...state.aiConfig, ...config }
      saveToStorage(state.aiConfig)
    },
    SET_API_KEY(state, apiKey) {
      state.aiConfig.apiKey = apiKey
      saveToStorage(state.aiConfig)
    },
    SET_MODEL(state, model) {
      state.aiConfig.selectedModel = model
      saveToStorage(state.aiConfig)
    },
    SET_PROMPT(state, prompt) {
      state.aiConfig.prompt = prompt
      saveToStorage(state.aiConfig)
    },
    CLEAR_CONFIG(state) {
      state.aiConfig = { selectedModel: '', apiKey: '', prompt: '' }
      localStorage.removeItem('aiConfig')
    }
  },
  actions: {
    updateAIConfig({ commit }, config) {
      commit('SET_AI_CONFIG', config)
    },
    setApiKey({ commit }, apiKey) {
      commit('SET_API_KEY', apiKey)
    },
    setModel({ commit }, model) {
      commit('SET_MODEL', model)
    },
    setPrompt({ commit }, prompt) {
      commit('SET_PROMPT', prompt)
    },
    clearConfig({ commit }) {
      commit('CLEAR_CONFIG')
    }
  },
  getters: {
    getApiKey: state => state.aiConfig.apiKey,
    getSelectedModel: state => state.aiConfig.selectedModel,
    getPrompt: state => state.aiConfig.prompt,
    getAIConfig: state => state.aiConfig,
    isConfigured: state => !!(state.aiConfig.apiKey && state.aiConfig.selectedModel)
  }
})