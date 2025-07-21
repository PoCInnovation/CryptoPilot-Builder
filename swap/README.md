# ETH to USDC Swap

Simple swap interface using LIFI API to exchange ETH for USDC on Ethereum mainnet.

## Setup

1. **Install dependencies:**
   ```bash
   cd backend
   npm install
   ```

2. **Start backend:**
   ```bash
   npm run dev
   ```

3. **Serve frontend:**
   ```bash
   cd ../frontend
   python3 -m http.server 8000
   ```

## Usage

1. Open `http://localhost:8000`
2. Connect MetaMask (ensure you're on Ethereum mainnet)
3. Enter ETH amount to swap
4. Click "Swap ETH → USDC"

## Requirements

- MetaMask wallet
- Ethereum mainnet network
- ETH for gas fees and swap amount

## ⚠️ Warning

This uses **real ETH** on mainnet. Start with small amounts (0.001 ETH) for testing.
