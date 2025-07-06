FROM node:22-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Optimiser npm
RUN npm config set fund false \
    && npm config set audit false \
    && npm config set update-notifier false

# Copier les fichiers de configuration
COPY package*.json ./
COPY jsconfig.json ./

# Installation avec npm install pour éviter les problèmes de rollup
RUN npm install --omit=optional --no-audit --no-fund

# Installer explicitement Rollup et ses dépendances natives pour Debian (glibc)
RUN npm install --save-dev @rollup/rollup-linux-x64-gnu

# Copier le code source
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./
COPY vite.config.js ./

EXPOSE 3000

# Commande pour démarrer le serveur de développement
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
