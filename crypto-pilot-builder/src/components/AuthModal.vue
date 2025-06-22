<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isLoginMode ? "Connexion" : "Inscription" }}
        </h2>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>

      <!-- Messages d'erreur/succès -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>

      <!-- Mode Connexion -->
      <form v-if="isLoginMode" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="login-email" class="form-label"
            >Email ou nom d'utilisateur</label
          >
          <input
            id="login-email"
            v-model="loginForm.email"
            type="text"
            class="form-input"
            placeholder="votre@email.com ou username"
            required
          />
        </div>
        <div class="form-group">
          <label for="login-password" class="form-label">Mot de passe</label>
          <input
            id="login-password"
            v-model="loginForm.password"
            type="password"
            class="form-input"
            placeholder="Votre mot de passe"
            required
          />
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$emit('close')">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? "Connexion..." : "Se connecter" }}
          </button>
        </div>
        <div class="form-footer">
          <p>
            Pas encore de compte ?
            <button type="button" @click="switchToRegister" class="link-button">
              S'inscrire
            </button>
          </p>
        </div>
      </form>

      <!-- Mode Inscription -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="register-username" class="form-label"
            >Nom d'utilisateur</label
          >
          <input
            id="register-username"
            v-model="registerForm.username"
            type="text"
            class="form-input"
            placeholder="Votre nom d'utilisateur"
            required
          />
        </div>
        <div class="form-group">
          <label for="register-email" class="form-label">Email</label>
          <input
            id="register-email"
            v-model="registerForm.email"
            type="email"
            class="form-input"
            placeholder="votre@email.com"
            required
          />
        </div>
        <div class="form-group">
          <label for="register-password" class="form-label">Mot de passe</label>
          <input
            id="register-password"
            v-model="registerForm.password"
            type="password"
            class="form-input"
            placeholder="Au moins 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre"
            required
          />
        </div>
        <div class="form-group">
          <label for="register-confirm" class="form-label"
            >Confirmer le mot de passe</label
          >
          <input
            id="register-confirm"
            v-model="registerForm.confirmPassword"
            type="password"
            class="form-input"
            placeholder="Répétez votre mot de passe"
            required
          />
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$emit('close')">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? "Inscription..." : "S'inscrire" }}
          </button>
        </div>
        <div class="form-footer">
          <p>
            Déjà un compte ?
            <button type="button" @click="switchToLogin" class="link-button">
              Se connecter
            </button>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "AuthModal",
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["close", "authenticated"],
  data() {
    return {
      isLoginMode: true,
      loading: false,
      message: "",
      messageType: "",
      loginForm: {
        email: "",
        password: "",
      },
      registerForm: {
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
      },
    };
  },
  computed: {
    ...mapState("auth", ["isAuthenticated", "user"]),
  },
  methods: {
    ...mapActions("auth", ["login", "register"]),

    switchToLogin() {
      this.isLoginMode = true;
      this.clearMessage();
      this.resetForms();
    },

    switchToRegister() {
      this.isLoginMode = false;
      this.clearMessage();
      this.resetForms();
    },

    resetForms() {
      this.loginForm = { email: "", password: "" };
      this.registerForm = {
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
      };
    },

    clearMessage() {
      this.message = "";
      this.messageType = "";
    },

    showMessage(message, type = "error") {
      this.message = message;
      this.messageType = type;
      setTimeout(() => {
        this.clearMessage();
      }, 5000);
    },

    async handleLogin() {
      this.clearMessage();

      if (!this.loginForm.email || !this.loginForm.password) {
        this.showMessage("Veuillez remplir tous les champs");
        return;
      }

      this.loading = true;

      try {
        await this.login({
          email: this.loginForm.email,
          password: this.loginForm.password,
        });

        this.showMessage("Connexion réussie !", "success");
        this.$emit("authenticated");
        setTimeout(() => {
          this.$emit("close");
        }, 1000);
      } catch (error) {
        const errorMessage =
          error.response?.data?.error || "Erreur lors de la connexion";
        this.showMessage(errorMessage);
      } finally {
        this.loading = false;
      }
    },

    async handleRegister() {
      this.clearMessage();

      // Validation
      if (
        !this.registerForm.username ||
        !this.registerForm.email ||
        !this.registerForm.password ||
        !this.registerForm.confirmPassword
      ) {
        this.showMessage("Veuillez remplir tous les champs");
        return;
      }

      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.showMessage("Les mots de passe ne correspondent pas");
        return;
      }

      if (this.registerForm.password.length < 8) {
        this.showMessage("Le mot de passe doit contenir au moins 8 caractères");
        return;
      }

      this.loading = true;

      try {
        await this.register({
          username: this.registerForm.username,
          email: this.registerForm.email,
          password: this.registerForm.password,
        });

        this.showMessage(
          "Inscription réussie ! Vous êtes maintenant connecté.",
          "success"
        );
        this.$emit("authenticated");
        setTimeout(() => {
          this.$emit("close");
        }, 1000);
      } catch (error) {
        const errorMessage =
          error.response?.data?.error || "Erreur lors de l'inscription";
        this.showMessage(errorMessage);
      } finally {
        this.loading = false;
      }
    },
  },

  watch: {
    show(newValue) {
      if (newValue) {
        this.resetForms();
        this.clearMessage();
        this.isLoginMode = true;
      }
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 12px;
  padding: 0;
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.message {
  margin: 0 24px 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
}

.message.success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.auth-form {
  padding: 0 24px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background-color: transparent;
  color: #6b7280;
  border: 2px solid #d1d5db;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.btn-secondary:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.form-footer p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.link-button {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-weight: 500;
  text-decoration: underline;
  font-size: 14px;
}

.link-button:hover {
  color: #2563eb;
}
</style>
