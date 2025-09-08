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

  async sendChatMessage(message, sessionId = null) {
    return this.request("/chat", {
      method: "POST",
      body: {
        message,
        session_id: sessionId,
      },
    });
  }

  async renameSession(sessionId, newName) {
    return this.request(`/sessions/${sessionId}/rename`, {
      method: "PUT",
      body: { session_name: newName },
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

  // ===== AUTOWALLET =====

  async getAutowalletConfig() {
    return this.request("/api/autowallet/config");
  }

  async createAutowalletConfig(config) {
    return this.request("/api/autowallet/config", {
      method: "POST",
      body: config,
    });
  }

  async updateAutowalletConfig(config) {
    return this.request("/api/autowallet/config", {
      method: "PUT",
      body: config,
    });
  }

  async getAutowalletNews() {
    return this.request("/api/autowallet/news");
  }

  async getAutowalletAlerts() {
    return this.request("/api/autowallet/alerts");
  }

  async analyzeNews(newsIds, analysisType = "individual") {
    return this.request("/api/autowallet/analyze", {
      method: "POST",
      body: {
        news_ids: newsIds,
        analysis_type: analysisType,
      },
    });
  }

  async startAutowalletMonitoring() {
    return this.request("/api/autowallet/start", {
      method: "POST",
    });
  }

  async stopAutowalletMonitoring() {
    return this.request("/api/autowallet/stop", {
      method: "POST",
    });
  }

  // ===== PIPELINE =====

  async getPipelineStatus() {
    return this.request("/api/trading-pipeline/test/status");
  }

  async getPipelineData() {
    return this.request("/api/trading-pipeline/test/market-data");
  }

  async startPipeline() {
    return this.request("/api/trading-pipeline/test/start", {
      method: "POST",
    });
  }

  async stopPipeline() {
    return this.request("/api/trading-pipeline/test/stop", {
      method: "POST",
    });
  }

  async startAllAgents() {
    return this.request("/api/trading-pipeline/test/start", {
      method: "POST",
    });
  }

  async stopAllAgents() {
    return this.request("/api/trading-pipeline/test/stop", {
      method: "POST",
    });
  }

  async callLoggerAgent() {
    return this.request("/api/trading-pipeline/test/logger", {
      method: "POST",
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
  renameSession,
  deleteUserMemory,
  getAutowalletConfig,
  createAutowalletConfig,
  updateAutowalletConfig,
  getAutowalletNews,
  getAutowalletAlerts,
  analyzeNews,
  startAutowalletMonitoring,
  stopAutowalletMonitoring,
  getPipelineStatus,
  getPipelineData,
  startPipeline,
  stopPipeline,
  startAllAgents,
  stopAllAgents,
} = apiService;
