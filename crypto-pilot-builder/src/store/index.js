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
    },
  },

  state: {
    aiConfig: loadFromStorage(),
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

    CLEAR_CONFIG(state) {
      state.aiConfig = {
        selectedModel: "",
        apiKey: "",
        prompt: "",
        modules: {},
      };
      localStorage.removeItem("aiConfig");
    },
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

    async updateAIConfig({ commit, dispatch, rootState }, config) {
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

    async setApiKey({ commit, dispatch, rootState }, apiKey) {
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

    async setModel({ commit, dispatch, rootState }, model) {
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

    async setPrompt({ commit, dispatch, rootState }, prompt) {
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

    async setModules({ commit, dispatch, rootState }, modules) {
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
    },
  },

  getters: {
    aiConfig: (state) => state.aiConfig,
    isLoading: (state) => state.loading,
    error: (state) => state.error,
    isAuthenticated: (state, getters, rootState) =>
      rootState.auth.isAuthenticated,
    user: (state, getters, rootState) => rootState.auth.user,
  },
});
