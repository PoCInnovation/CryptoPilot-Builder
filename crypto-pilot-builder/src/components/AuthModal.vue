<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isLoginMode ? "Connexion" : "Inscription" }}
        </h2>
        <button class="modal-close" @click="$emit('close')">
          <span class="close-icon">×</span>
        </button>
      </div>
      <!-- Messages d'erreur/succès -->
      <div v-if="message" :class="['message', messageType]">
        <div class="message-content">
          <span class="message-icon">{{ messageType === 'success' ? '✅' : '⚠️' }}</span>
          <span>{{ message }}</span>
        </div>
      </div>
      <!-- Mode Connexion -->
      <form v-if="isLoginMode" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="login-email" class="form-label">
            Email ou nom d'utilisateur
          </label>
          <div class="input-wrapper">
            <input
              id="login-email"
              v-model="loginForm.email"
              type="text"
              class="form-input"
              placeholder="votre@email.com ou username"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="login-password" class="form-label">Mot de passe</label>
          <div class="input-wrapper">
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              class="form-input"
              placeholder="Votre mot de passe"
              required
            />
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$emit('close')">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
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
          <label for="register-username" class="form-label">Nom d'utilisateur</label>
          <div class="input-wrapper">
            <input
              id="register-username"
              v-model="registerForm.username"
              type="text"
              class="form-input"
              placeholder="Votre nom d'utilisateur"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="register-email" class="form-label">Email</label>
          <div class="input-wrapper">
            <input
              id="register-email"
              v-model="registerForm.email"
              type="email"
              class="form-input"
              placeholder="votre@email.com"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="register-password" class="form-label">Mot de passe</label>
          <div class="input-wrapper">
            <input
              id="register-password"
              v-model="registerForm.password"
              type="password"
              class="form-input"
              placeholder="Au moins 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="register-confirm" class="form-label">Confirmer le mot de passe</label>
          <div class="input-wrapper">
            <input
              id="register-confirm"
              v-model="registerForm.confirmPassword"
              type="password"
              class="form-input"
              placeholder="Répétez votre mot de passe"
              required
            />
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$emit('close')">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
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
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.7) 0%, rgba(90, 52, 148, 0.7) 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(6px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(118, 75, 162, 0.3);
  width: 90%;
  max-width: 450px;
  overflow: hidden;
  transform: scale(0.95);
  animation: modalAppear 0.4s ease forwards;
  position: relative;
  overflow: hidden;
}

@keyframes modalAppear {
  to {
    transform: scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, #764ba2 0%, #5a3494 100%);
  color: white;
  padding: 28px 28px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
  position: relative;
}

.modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #764ba2 0%, #a552cc 100%);
}

.modal-title {
  font-size: 26px;
  font-weight: bold;
  margin: 0;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.close-icon {
  position: relative;
  transition: transform 0.3s ease;
}

.modal-close:hover .close-icon {
  transform: rotate(90deg);
}

.message {
  margin: 20px 24px 16px;
  padding: 16px 20px;
  border-radius: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
  border-left: 4px solid;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.message.success {
  background-color: #d1fae5;
  color: #065f46;
  border-color: #10b981;
}

.message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #ef4444;
}

.message-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.message-icon {
  font-size: 18px;
  min-width: 20px;
}

.auth-form {
  padding: 20px 28px 32px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #4b2e83;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-wrapper {
  position: relative;
  overflow: hidden;
}

.form-input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #dcdcdc;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #f8f6ff;
  box-sizing: border-box;
  font-family: inherit;
  z-index: 1;
  position: relative;
}

.form-input:focus {
  outline: none;
  border-color: #764ba2;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.15);
}

.form-input::placeholder {
  color: #aaa;
}

.form-input:focus + .input-decoration,
.input-wrapper:hover .input-decoration {
  transform: translateX(0);
}

.input-decoration {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(118, 75, 162, 0.1), transparent);
  transition: transform 0.5s ease;
  z-index: 0;
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 30px;
  flex-wrap: wrap;
}

.btn-secondary {
  padding: 12px 24px;
  border: 2px solid #e1e8ed;
  background: white;
  color: #4b2e83;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.btn-secondary:hover {
  background-color: #f3e8ff;
  border-color: #c5b3f4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(197, 179, 244, 0.3);
}

.btn-secondary::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(118, 75, 162, 0.1), transparent);
  transition: left 0.5s ease;
  z-index: -1;
}

.btn-secondary:hover::after {
  left: 100%;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #764ba2 0%, #5a3494 100%);
  border: none;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}

.btn-primary:disabled {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  cursor: not-allowed;
  transform: none;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  margin-right: 8px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-footer p {
  margin: 0;
  color: #4b2e83;
  font-size: 14px;
  line-height: 1.5;
}

.link-button {
  background: none;
  border: none;
  color: #764ba2;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  position: relative;
}

.link-button:hover {
  color: #5a3494;
  transform: translateX(5px);
}

.link-button::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 1px;
  background: #764ba2;
  transition: width 0.3s ease;
}

.link-button:hover::after {
  width: 100%;
}

.modal-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(118, 75, 162, 0.05) 0%, transparent 60%);
  animation: rotateBackground 20s linear infinite;
  z-index: 0;
  pointer-events: none;
}

@keyframes rotateBackground {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .modal-container {
    margin: 20px;
  }
  .modal-title {
    font-size: 22px;
  }
  .form-input {
    font-size: 14px;
  }
  .btn-primary,
  .btn-secondary {
    font-size: 14px;
    padding: 10px 20px;
  }
}
</style>