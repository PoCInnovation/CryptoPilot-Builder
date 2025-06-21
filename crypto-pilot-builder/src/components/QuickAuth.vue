<!-- <template>
  <div class="quick-auth">
    <div v-if="!isAuthenticated" class="login-section">
      <h3>🔐 Connexion rapide</h3>
      <form @submit.prevent="quickLogin" class="login-form">
        <input
          v-model="loginForm.email"
          type="email"
          placeholder="Email"
          required
          class="input-field"
        />
        <input
          v-model="loginForm.password"
          type="password"
          placeholder="Mot de passe"
          required
          class="input-field"
        />
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? "Connexion..." : "Se connecter" }}
        </button>
      </form>

      <div class="register-section">
        <p>Pas encore de compte ?</p>
        <button @click="quickRegister" :disabled="loading" class="register-btn">
          Créer un compte de test
        </button>
      </div>
    </div>

     <div v-else class="user-info">
      <h3>✅ Connecté</h3>
      <p>{{ user?.username || user?.email }}</p>
      <button @click="logout" class="logout-btn">Déconnexion</button>
      <button @click="checkConfig" class="config-btn">Vérifier config</button>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template> -->

<script>
import { mapGetters, mapActions } from "vuex";
import apiService from "../services/apiService";

export default {
  name: "QuickAuth",
  data() {
    return {
      loading: false,
      error: null,
      loginForm: {
        email: "test@example.com",
        password: "TestPassword123",
      },
    };
  },
  computed: {
    ...mapGetters(["isAuthenticated", "getUser"]),
    user() {
      return this.getUser;
    },
  },
  methods: {
    ...mapActions(["login", "logout", "loadAgentConfig"]),

    async quickLogin() {
      this.loading = true;
      this.error = null;

      try {
        const response = await apiService.login({
          email: this.loginForm.email,
          password: this.loginForm.password,
        });

        this.login({
          user: response.user,
          token: response.access_token,
        });

        // Charger la config de l'agent
        await this.loadAgentConfig();

        this.error = null;
      } catch (error) {
        this.error = error.message;
        console.error("Erreur de connexion:", error);
      } finally {
        this.loading = false;
      }
    },

    async quickRegister() {
      this.loading = true;
      this.error = null;

      try {
        const testUser = {
          username: `testuser${Date.now()}`,
          email: `test${Date.now()}@example.com`,
          password: "TestPassword123",
        };

        const response = await apiService.register(testUser);

        this.login({
          user: response.user,
          token: response.access_token,
        });

        this.error = null;
        console.log("Compte créé:", testUser);
      } catch (error) {
        this.error = error.message;
        console.error("Erreur de création de compte:", error);
      } finally {
        this.loading = false;
      }
    },

    async checkConfig() {
      this.loading = true;
      this.error = null;

      try {
        await this.loadAgentConfig();
        this.error = "Configuration chargée avec succès !";
      } catch (error) {
        this.error = `Erreur config: ${error.message}`;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.quick-auth {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 300px;
  z-index: 1000;
  border: 2px solid #e2e8f0;
}

.quick-auth h3 {
  margin: 0 0 15px 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.input-field {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
}

.login-btn,
.register-btn,
.logout-btn,
.config-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-btn,
.config-btn {
  background: #667eea;
  color: white;
}

.login-btn:hover,
.config-btn:hover {
  background: #5a67d8;
}

.register-btn {
  background: #10b981;
  color: white;
  margin-top: 5px;
}

.register-btn:hover {
  background: #059669;
}

.logout-btn {
  background: #ef4444;
  color: white;
  margin-right: 10px;
}

.logout-btn:hover {
  background: #dc2626;
}

.register-section {
  border-top: 1px solid #e2e8f0;
  padding-top: 15px;
  margin-top: 15px;
  text-align: center;
}

.register-section p {
  margin: 0 0 10px 0;
  color: #64748b;
  font-size: 14px;
}

.user-info {
  text-align: center;
}

.user-info p {
  margin: 5px 0 15px 0;
  color: #64748b;
  font-size: 14px;
}

.error-message {
  margin-top: 10px;
  padding: 8px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 12px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
