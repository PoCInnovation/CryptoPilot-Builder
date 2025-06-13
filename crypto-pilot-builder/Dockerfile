FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY jsconfig.json ./

RUN npm ci

COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./
COPY vite.config.js ./

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
