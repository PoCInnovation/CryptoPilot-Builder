# CryptoPilot-Builder

CryptoPilot-Builder is an AI-powered no-code platform that allows users to easily create personalized AI assistants for cryptocurrency portfolio management. By leveraging advanced AI algorithms, users can configure their preferences, risk tolerance, and investment goals, and the platform will automatically generate optimized investment strategies without requiring any technical knowledge.

## 🚀 Key Features

### 🤖 Custom AI Agent Configuration

- **Intuitive 3-step interface**: AI Configuration → Modules → Finalization
- **Multiple model support**: GPT-4o Mini and extensible to other models
- **Personal API configuration**: Each user uses their own OpenAI key
- **Customizable prompts**: Define assistant behavior
- **Functional modules**:
  - Advanced Chat with contextual memory
  - Complex data analysis
  - Real-time web search
  - Creative content generation

### 💬 Intelligent Chat Interface

- **Multiple sessions**: Manage several simultaneous conversations
- **Data persistence**: Automatic conversation saving
- **Modern interface**: Glassmorphism design with fluid animations
- **Robust error handling**: Clear error messages and automatic recovery

### 🔗 Blockchain Integration

- **MetaMask support**: Native wallet connection
- **Automated transactions**: Crypto transaction detection and execution
- **Multi-network support**: Ethereum Sepolia (testnet) and extensible
- **Secure confirmations**: Validation modal for each transaction

### 🏗️ MCP Architecture (Model Context Protocol)

- **MCP Client-Server**: Standardized communication with AI
- **Integrated crypto tools**:
  - Real-time price retrieval (CoinGecko API)
  - Blockchain transaction management
  - Automated market analysis
- **Extensibility**: Easy addition of new tools

### 🔐 Authentication System

- **Secure JWT**: User session management
- **PostgreSQL database**: Secure configuration storage
- **Data isolation**: Each user has their own configurations and sessions

## 🏛️ Technical Architecture

### Frontend (Vue.js + Electron)

```
crypto-pilot-builder/
├── src/
│   ├── acceuil/              # Home pages and navigation
│   ├── agent_building/       # Agent configuration wizard
│   │   ├── Ai.vue           # Step 1: AI Configuration
│   │   ├── Module.vue       # Step 2: Module selection
│   │   ├── Prompte.vue      # Step 3: Behavior definition
│   │   └── Progress_bar.vue # Progress bar
│   ├── components/
│   │   ├── chatbot.vue      # Main chat interface
│   │   ├── wallet.vue       # MetaMask integration
│   │   └── AuthModal.vue    # Authentication modal
│   ├── router/              # Route configuration
│   ├── services/            # API services
│   └── store/               # Vuex state management
```

### Backend Python (Flask + MCP)

```
crypto-pilot-builder/python/
├── mcp_client/              # MCP Client
│   ├── api_routes.py        # REST API routes
│   ├── mcp_client.py        # MCP client for AI communication
│   └── session_manager.py   # Session management
├── mcp_serveur/             # MCP Server
│   ├── mcp_server_sdk.py    # MCP server with crypto tools
│   └── crypto_tools.py      # Integrated blockchain tools
├── tools/                   # Specialized tools
└── chatbot.py              # Alternative Agno version
```

### Database (PostgreSQL)

```sql
-- Users and authentication
users (id, username, email, password_hash, wallet_address)

-- Chat sessions
chat_sessions (id, user_id, session_name, created_at)
chat_messages (id, session_id, role, content, created_at)

-- AI agent configurations
agent_configs (id, user_id, selected_model, api_key, modules_config, prompt, name)
```

## 📦 Installation

### Prerequisites

- **Node.js** (v16+) and npm
- **Python** (3.8+) with pip
- **PostgreSQL** (13+)
- **MetaMask** (browser extension)
- **Docker & Docker Compose** (optional)

### Docker Installation (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/PoCInnovation/CryptoPilot-Builder.git
   cd CryptoPilot-Builder
   ```

2. **Environment variables configuration**

   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Launch with Docker Compose**

   ```bash
   docker-compose up -d
   ```

4. **Access services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Database: localhost:5432

### Manual Installation

#### Python Backend

```bash
cd crypto-pilot-builder/python
pip install -r requirements.txt

# Database configuration
createdb cryptopilot
psql cryptopilot < ../init.sql

# Start server
python mcp_client/mcp_http_bridge.py
```

#### Vue.js Frontend

```bash
cd crypto-pilot-builder
npm install

# Development mode
npm run dev

# Electron mode
npm run electron
```

## 🎯 Usage Guide

### 1. Initial Setup

1. **Create an account** or sign in
2. **Configure your AI agent**:
   - Choose the model (GPT-4o Mini)
   - Provide your OpenAI API key
   - Select desired modules
   - Define behavior with a custom prompt

### 2. Using the Chat

1. **Connect MetaMask** for blockchain features
2. **Create a new chat session**
3. **Interact with the assistant**:
   ```
   "What's the Bitcoin price today?"
   "Send 0.01 ETH to 0xFa6D1Ff93Fa73f3105f24FF47911b8C544CDA195"
   "Analyze crypto market trends"
   ```

### 3. Transaction Management

- AI automatically detects transaction requests
- A confirmation modal appears before execution
- Validation via MetaMask for security
- Real-time transaction status tracking

## 🔧 Advanced Configuration

### Environment Variables

Create a `.env` file at the root with:

```env
# Database
POSTGRES_DB=cryptopilot
POSTGRES_USER=cryptopilot_user
POSTGRES_PASSWORD=your_password

# Backend
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-jwt-key

# Frontend
VITE_API_URL=http://localhost:5000

# OpenAI (optional for server)
OPENAI_API_KEY=sk-your-optional-key
```

### Adding New MCP Tools

1. **Create the tool** in `crypto_tools.py`
2. **Register in the MCP server** (`mcp_server_sdk.py`)
3. **Expose via API** (`api_routes.py`)

## 🤝 Contributing

This project uses [PoC Innovation's open-source template](https://github.com/PoCInnovation/open-source-project-template). Check the [contributing guide](./CONTRIBUTING.md) for more details.

### Development Process

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Open a Pull Request
5. Review and merge

## 👥 Our PoC Team ❤️

**Developers**
| [<img src="https://github.com/AurelienDEMEUSY.png?size=85" width=85><br><sub>Aurelien Demeusy</sub>](https://github.com/AurelienDEMEUSY) | [<img src="https://github.com/Nerzouille.png?size=85" width=85><br><sub>Noa Smoter</sub>](https://github.com/Nerzouille) | [<img src="https://github.com/MiloKow.png?size=85" width=85><br><sub>Milo Kowalska</sub>](https://github.com/MiloKow)
| :---: | :---: | :---: |

**Managers**
| [<img src="https://github.com/Intermarch3.png?size=85" width=85><br><sub>Lucas Leclerc</sub>](https://github.com/Intermarch3) | [<img src="https://github.com/ramosleandre.png?size=85" width=85><br><sub>Leandre Ramos</sub>](https://github.com/ramosleandre)
| :---: | :---: |

<h2 align=center>
Organization
</h2>

<p align='center'>
    <a href="https://www.linkedin.com/company/pocinnovation/mycompany/">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn logo">
    </a>
    <a href="https://www.instagram.com/pocinnovation/">
        <img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram logo">
    </a>
    <a href="https://twitter.com/PoCInnovation">
        <img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter logo">
    </a>
    <a href="https://discord.com/invite/Yqq2ADGDS7">
        <img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord logo">
    </a>
</p>
<p align=center>
    <a href="https://www.poc-innovation.fr/">
        <img src="https://img.shields.io/badge/WebSite-1a2b6d?style=for-the-badge&logo=GitHub Sponsors&logoColor=white" alt="Website logo">
    </a>
</p>

> 🚀 Don't hesitate to follow us on our different networks, and put a star 🌟 on `PoC's` repositories

> Made with ❤️ by PoC
