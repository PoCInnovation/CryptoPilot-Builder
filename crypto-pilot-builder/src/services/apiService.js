/**
 * Service API pour l'application CryptoPilot-Builder
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Méthode utilitaire pour faire des requêtes
  async request(endpoint, options = {}) {
    const token = localStorage.getItem("auth_token");

    const defaultHeaders = {
      "Content-Type": "application/json",
    };

    if (token) {
      defaultHeaders.Authorization = `Bearer ${token}`;
    }

    const config = {
      method: "GET",
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === "object") {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ error: "Erreur réseau" }));
        throw new Error(errorData.error || `Erreur HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Erreur API ${endpoint}:`, error);
      throw error;
    }
  }

  // ===== AUTHENTIFICATION =====

  async register(userData) {
    return this.request("/register", {
      method: "POST",
      body: userData,
    });
  }

  async login(credentials) {
    return this.request("/login", {
      method: "POST",
      body: credentials,
    });
  }

  // ===== CONFIGURATION AGENT =====

  async getAgentConfig() {
    return this.request("/agent-config");
  }

  async saveAgentConfig(config) {
    return this.request("/agent-config", {
      method: "POST",
      body: config,
    });
  }

  async updatePartialConfig(partialConfig) {
    return this.request("/agent-config/partial", {
      method: "PUT",
      body: partialConfig,
    });
  }

  async listAgentConfigs() {
    return this.request("/agent-configs");
  }

  // ===== CHAT =====

  async sendChatMessage(message, sessionId = null, walletAddress = null) {
    return this.request("/chat", {
      method: "POST",
      body: {
        message,
        session_id: sessionId,
        wallet_address: walletAddress,
      },
    });
  }

  async createNewSession(sessionName = "New Chat") {
    return this.request("/new-session", {
      method: "POST",
      body: { session_name: sessionName },
    });
  }

  async getSession(sessionId) {
    return this.request(`/sessions/${sessionId}`);
  }

  async listSessions() {
    return this.request("/sessions");
  }

  async deleteSession(sessionId) {
    return this.request(`/sessions/${sessionId}`, {
      method: "DELETE",
    });
  }

  // ===== MCP =====

  async connectMCP() {
    return this.request("/mcp/connect", {
      method: "POST",
    });
  }

  async listMCPTools() {
    return this.request("/mcp/tools");
  }

  async getCryptoPrice(cryptoId, currency = "usd") {
    return this.request("/crypto/price", {
      method: "POST",
      body: {
        crypto_id: cryptoId,
        currency,
      },
    });
  }

  // ===== HEALTH =====

  async healthCheck() {
    return this.request("/health");
  }

  // ===== MÉMOIRE UTILISATEUR =====

  async getUserMemory() {
    return this.request("/user-memory");
  }

  async addUserMemory(memoryData) {
    return this.request("/user-memory", {
      method: "POST",
      body: memoryData,
    });
  }

  async deleteUserMemory(memoryId) {
    return this.request(`/user-memory/${memoryId}`, {
      method: "DELETE",
    });
  }
}

// Instance singleton
const apiService = new ApiService();

export default apiService;

// Export des méthodes pour utilisation directe
export const {
  register,
  login,
  getAgentConfig,
  saveAgentConfig,
  updatePartialConfig,
  listAgentConfigs,
  sendChatMessage,
  createNewSession,
  getSession,
  listSessions,
  deleteSession,
  connectMCP,
  listMCPTools,
  getCryptoPrice,
  healthCheck,
  getUserMemory,
  addUserMemory,
  deleteUserMemory,
} = apiService;
