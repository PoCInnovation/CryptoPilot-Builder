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
  background: linear-gradient(135deg, rgba(28, 32, 51, 0.8), rgba(16, 21, 33, 0.9));
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(15px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
  }
  to { 
    opacity: 1; 
  }
}

.modal-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  transform: scale(0.95);
  animation: modalAppear 0.4s ease forwards;
  position: relative;
}

@keyframes modalAppear {
  to {
    transform: scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.8) 0%, rgba(90, 52, 148, 0.9) 100%);
  backdrop-filter: blur(10px);
  color: white;
  padding: 24px 28px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(118, 75, 162, 0.3);
  position: relative;
  border-radius: 24px 24px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, rgba(118, 75, 162, 0.6) 0%, rgba(165, 82, 204, 0.8) 100%);
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.modal-close {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 24px;
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.modal-close:focus {
  outline: 2px solid rgba(255, 255, 255, 0.5);
  outline-offset: 2px;
}

.close-icon {
  font-weight: 300;
  line-height: 1;
  font-size: 20px;
}

/* Messages d'erreur/succès */
.message {
  margin: 20px 28px 0;
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  animation: slideDown 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.error {
  background: rgba(255, 107, 107, 0.9);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.message.success {
  background: rgba(81, 207, 102, 0.9);
  color: white;
  box-shadow: 0 4px 15px rgba(81, 207, 102, 0.3);
}

.message-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.message-icon {
  font-size: 16px;
  flex-shrink: 0;
}

/* Formulaire */
.auth-form {
  padding: 28px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
  letter-spacing: 0.3px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  transition: all 0.3s ease;
  box-sizing: border-box;
  outline: none;
  font-family: inherit;
}

.form-input:focus {
  border-color: rgba(118, 75, 162, 0.8);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 0 0 3px rgba(118, 75, 162, 0.2),
    0 4px 20px rgba(118, 75, 162, 0.1);
  transform: translateY(-1px);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* Actions du formulaire */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
  font-family: inherit;
  backdrop-filter: blur(10px);
}

.btn-primary {
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.8) 0%, rgba(90, 52, 148, 0.9) 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(118, 75, 162, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.9) 0%, rgba(90, 52, 148, 1) 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(118, 75, 162, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary:focus,
.btn-secondary:focus {
  outline: 2px solid rgba(118, 75, 162, 0.5);
  outline-offset: 2px;
}

/* Spinner de chargement */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Pied de formulaire */
.form-footer {
  margin-top: 24px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.form-footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.link-button {
  background: none;
  border: none;
  color: rgba(118, 75, 162, 1);
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 14px;
  font-family: inherit;
  text-shadow: 0 0 10px rgba(118, 75, 162, 0.5);
}

.link-button:hover {
  color: rgba(165, 82, 204, 1);
  text-decoration: underline;
  text-shadow: 0 0 15px rgba(165, 82, 204, 0.7);
}

.link-button:focus {
  outline: 2px solid rgba(118, 75, 162, 0.5);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Responsive */
@media (max-width: 500px) {
  .modal-container {
    width: 95%;
    margin: 20px;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-title {
    font-size: 20px;
  }
  
  .auth-form {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
  
  .message {
    margin: 16px 20px 0;
    padding: 14px 16px;
  }
}

/* Animation pour les champs d'erreur */
.form-input.error {
  border-color: rgba(255, 107, 107, 0.8);
  background: rgba(255, 107, 107, 0.1);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* Styles pour les états de validation */
.form-input.valid {
  border-color: rgba(81, 207, 102, 0.8);
  background: rgba(81, 207, 102, 0.1);
}

.form-input.invalid {
  border-color: rgba(255, 107, 107, 0.8);
  background: rgba(255, 107, 107, 0.1);
}

/* Scrollbar personnalisée pour modal-container */
.modal-container::-webkit-scrollbar {
  width: 6px;
}

.modal-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.modal-container::-webkit-scrollbar-thumb {
  background: rgba(118, 75, 162, 0.6);
  border-radius: 3px;
  backdrop-filter: blur(10px);
}

.modal-container::-webkit-scrollbar-thumb:hover {
  background: rgba(118, 75, 162, 0.8);
}

/* Amélioration de l'accessibilité */
@media (prefers-reduced-motion: reduce) {
  .modal-overlay,
  .modal-container,
  .message,
  .form-input,
  .btn-primary,
  .btn-secondary,
  .modal-close,
  .spinner {
    animation: none;
    transition: none;
  }
}

.form-input:focus-visible {
  outline: 2px solid rgba(118, 75, 162, 0.5);
  outline-offset: 2px;
}
</style>