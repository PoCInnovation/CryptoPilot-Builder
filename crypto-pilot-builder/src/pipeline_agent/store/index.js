import { createStore } from "vuex";
import apiService from "../services/apiService";

// Fonction de fallback pour le localStorage (en cas d'absence de connexion)
const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem("aiConfig");
    return saved
      ? JSON.parse(saved)
      : { selectedModel: "", apiKey: "", prompt: "", modules: {} };
  } catch (error) {
    console.error("Erreur lors du chargement des données:", error);
    return { selectedModel: "", apiKey: "", prompt: "", modules: {} };
  }
};

const saveToStorage = (config) => {
  try {
    localStorage.setItem("aiConfig", JSON.stringify(config));
  } catch (error) {
    console.error("Erreur lors de la sauvegarde:", error);
  }
};

export default createStore({
  modules: {
    auth: {
      namespaced: true,
      state: {
        isAuthenticated: !!localStorage.getItem("auth_token"),
        user: null,
        token: localStorage.getItem("auth_token"),
        loading: false,
        error: null,
      },

      mutations: {
        SET_LOADING(state, loading) {
          state.loading = loading;
        },

        SET_ERROR(state, error) {
          state.error = error;
        },

        SET_AUTH(state, { user, token }) {
          state.isAuthenticated = true;
          state.user = user;
          state.token = token;
          if (token) {
            localStorage.setItem("auth_token", token);
          }
        },

        CLEAR_AUTH(state) {
          state.isAuthenticated = false;
          state.user = null;
          state.token = null;
          localStorage.removeItem("auth_token");
        },
      },

      actions: {
        async login({ commit }, { email, password }) {
          try {
            commit("SET_LOADING", true);
            commit("SET_ERROR", null);

            const response = await apiService.login({ email, password });

            commit("SET_AUTH", {
              user: response.user,
              token: response.access_token,
            });

            // Charger la configuration après connexion
            await this.dispatch("loadAgentConfig");

            return response;
          } catch (error) {
            commit(
              "SET_ERROR",
              error.response?.data?.error || "Erreur de connexion"
            );
            throw error;
          } finally {
            commit("SET_LOADING", false);
          }
        },

        async renameChat({ commit }, { chatId, newName }) {
          try {
            await apiService.renameSession(chatId, newName);
            commit("SET_CHAT_NAME", { chatId, newName });
          } catch (error) {
            console.error("Erreur lors du renommage du chat:", error);
            // Optionnel : afficher une notification à l'utilisateur
          }
        },
        async register({ commit }, { username, email, password }) {
          try {
            commit("SET_LOADING", true);
            commit("SET_ERROR", null);

            const response = await apiService.register({
              username,
              email,
              password,
            });

            commit("SET_AUTH", {
              user: response.user,
              token: response.access_token,
            });

            return response;
          } catch (error) {
            commit(
              "SET_ERROR",
              error.response?.data?.error || "Erreur d'inscription"
            );
            throw error;
          } finally {
            commit("SET_LOADING", false);
          }
        },

        logout({ commit }) {
          commit("CLEAR_AUTH");
          this.dispatch("clearConfig");
        },

        checkAuth({ commit, state }) {
          const token = localStorage.getItem("auth_token");
          if (token && !state.isAuthenticated) {
            // Tenter de valider le token avec l'API si nécessaire
            commit("SET_AUTH", { user: null, token });
          }
        },
      },

      getters: {
        isAuthenticated: (state) => state.isAuthenticated,
        user: (state) => state.user,
        authLoading: (state) => state.loading,
        authError: (state) => state.error,
      },
    }
  },

  state: {
    aiConfig: loadFromStorage(),
    loading: false,
    error: null,
    // Ajout de l'état pour les chats
    chats: [],
    activeChat: null,
    nextChatId: 1
  },

  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading;
    },

    SET_ERROR(state, error) {
      state.error = error;
    },

    SET_AI_CONFIG(state, config) {
      state.aiConfig = { ...state.aiConfig, ...config };
      saveToStorage(state.aiConfig); // Sauvegarde locale de secours
    },

    SET_API_KEY(state, apiKey) {
      state.aiConfig.apiKey = apiKey;
      saveToStorage(state.aiConfig);
    },

    SET_MODEL(state, model) {
      state.aiConfig.selectedModel = model;
      saveToStorage(state.aiConfig);
    },

    SET_PROMPT(state, prompt) {
      state.aiConfig.prompt = prompt;
      saveToStorage(state.aiConfig);
    },

    SET_MODULES(state, modules) {
      state.aiConfig.modules = modules;
      saveToStorage(state.aiConfig);
    },
    SET_CHAT_NAME(state, { chatId, newName }) {
      const chat = state.chats.find(c => c.id === chatId);
      if (chat) {
        chat.name = newName;
      }
    },
    CLEAR_CONFIG(state) {
      state.aiConfig = {
        selectedModel: "",
        apiKey: "",
        prompt: "",
        modules: {},
      };
      localStorage.removeItem("aiConfig");
    },

    // Mutations pour la gestion des chats
    SET_CHATS(state, chats) {
      state.chats = chats;
      // Mettre à jour nextChatId basé sur les IDs existants
      state.nextChatId = chats.length > 0 
        ? Math.max(...chats.map(c => c.id)) + 1 
        : 1;
    },

    ADD_CHAT(state, chat) {
      state.chats.push(chat);
      state.activeChat = chat.id;
    },

    DELETE_CHAT(state, chatId) {
      const index = state.chats.findIndex(chat => chat.id === chatId);
      if (index !== -1) {
        state.chats.splice(index, 1);
        // Si le chat actif est supprimé, sélectionner le premier chat
        if (state.activeChat === chatId && state.chats.length > 0) {
          state.activeChat = state.chats[0].id;
        }
      }
    }
  },

  actions: {
    // Actions de configuration avec API
    async loadAgentConfig({ commit, rootState }) {
      if (!rootState.auth.isAuthenticated) {
        console.warn(
          "Utilisateur non authentifié, utilisation du localStorage"
        );
        return;
      }

      try {
        commit("SET_LOADING", true);
        commit("SET_ERROR", null);

        const response = await apiService.getAgentConfig();
        commit("SET_AI_CONFIG", {
          selectedModel: response.config.selectedModel,
          apiKey: response.config.apiKey,
          prompt: response.config.prompt,
          modules: response.config.modules || {},
        });
      } catch (error) {
        console.error(
          "Erreur lors du chargement de la configuration:",
          error.message
        );
        commit("SET_ERROR", error.message);
        // En cas d'erreur, garder les données locales
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // Nouvelle action pour charger les chats depuis l'API
    async loadChatsFromApi({ commit }) {
      try {
        commit("SET_LOADING", true);
        const response = await apiService.listSessions();
        const sessions = response.sessions || [];
        
        // Convertir les sessions en format compatible avec l'UI
        const chats = sessions.map(session => ({
          id: session.session_id,
          name: session.session_name || `Chat ${session.session_id}`
        }));
        
        commit("SET_CHATS", chats);
      } catch (error) {
        console.error("Erreur lors du chargement des chats:", error);
        // Fallback avec un chat par défaut
        commit("SET_CHATS", [{ 
          id: 1, 
          name: "Chat par défaut"
        }]);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // Nouvelle action pour créer un chat
    async createNewChat({ commit, state }, chatName) {
      try {
        commit("SET_LOADING", true);
        const sessionData = await apiService.createNewSession(chatName);
        
        const newChat = {
          id: sessionData.session_id,
          name: chatName
        };
        
        commit("ADD_CHAT", newChat);
        return newChat;
      } catch (error) {
        console.error("Erreur lors de la création du chat:", error);
        // Créer un chat local en fallback
        const fallbackChat = {
          id: state.nextChatId,
          name: chatName
        };
        commit("ADD_CHAT", fallbackChat);
        return fallbackChat;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // Nouvelle action pour supprimer un chat
    async deleteChat({ commit }, chatId) {
      try {
        commit("SET_LOADING", true);
        await apiService.deleteSession(chatId);
        commit("DELETE_CHAT", chatId);
      } catch (error) {
        console.error("Erreur lors de la suppression du chat:", error);
        // Suppression locale en fallback
        commit("DELETE_CHAT", chatId);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async saveCompleteConfig({ commit, rootState }, config) {
      if (!rootState.auth.isAuthenticated) {
        // Mode hors ligne - sauvegarde locale uniquement
        commit("SET_AI_CONFIG", config);
        return;
      }

      try {
        commit("SET_LOADING", true);
        commit("SET_ERROR", null);

        const response = await apiService.saveAgentConfig(config);
        commit("SET_AI_CONFIG", {
          selectedModel: response.config.selectedModel,
          apiKey: response.config.apiKey,
          prompt: response.config.prompt,
          modules: response.config.modules || {},
        });

        return response;
      } catch (error) {
        console.error("Erreur lors de la sauvegarde complète:", error.message);
        commit("SET_ERROR", error.message);
        // Sauvegarde locale de secours
        commit("SET_AI_CONFIG", config);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async updateAIConfig({ commit, rootState }, config) {
      // Mise à jour locale immédiate pour la réactivité
      commit("SET_AI_CONFIG", config);

      if (!rootState.auth.isAuthenticated) {
        return;
      }

      try {
        // Sauvegarde en arrière-plan via API
        await apiService.updatePartialConfig(config);
      } catch (error) {
        console.error(
          "Erreur lors de la mise à jour partielle:",
          error.message
        );
        // Pas de throw - la mise à jour locale est déjà faite
      }
    },

    async setApiKey({ commit, rootState }, apiKey) {
      commit("SET_API_KEY", apiKey);

      if (rootState.auth.isAuthenticated) {
        try {
          await apiService.updatePartialConfig({ apiKey });
        } catch (error) {
          console.error(
            "Erreur lors de la sauvegarde de la clé API:",
            error.message
          );
        }
      }
    },

    async setModel({ commit, rootState }, model) {
      commit("SET_MODEL", model);

      if (rootState.auth.isAuthenticated) {
        try {
          await apiService.updatePartialConfig({ selectedModel: model });
        } catch (error) {
          console.error(
            "Erreur lors de la sauvegarde du modèle:",
            error.message
          );
        }
      }
    },

    async setPrompt({ commit, rootState }, prompt) {
      commit("SET_PROMPT", prompt);

      if (rootState.auth.isAuthenticated) {
        try {
          await apiService.updatePartialConfig({ prompt });
        } catch (error) {
          console.error(
            "Erreur lors de la sauvegarde du prompt:",
            error.message
          );
        }
      }
    },

    async setModules({ commit, rootState }, modules) {
      commit("SET_MODULES", modules);

      if (rootState.auth.isAuthenticated) {
        try {
          await apiService.updatePartialConfig({ modules });
        } catch (error) {
          console.error(
            "Erreur lors de la sauvegarde des modules:",
            error.message
          );
        }
      }
    },

    clearConfig({ commit }) {
      commit("CLEAR_CONFIG");
    }
  },

  getters: {
    aiConfig: (state) => state.aiConfig,
    isLoading: (state) => state.loading,
    error: (state) => state.error,
    isAuthenticated: (state, getters, rootState) =>
      rootState.auth.isAuthenticated,
    user: (state, getters, rootState) => rootState.auth.user,
    chats: (state) => state.chats,
    activeChat: (state) => state.activeChat,
    nextChatId: (state) => state.nextChatId
  }
});