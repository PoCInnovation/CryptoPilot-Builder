import express from 'express';
import axios from 'axios';
import cors from 'cors';

const app = express();
const PORT = 3001;

app.use(cors());

app.get('/quote', async (req, res) => {
  const { fromAddress, fromAmount } = req.query;

  const params = {
    fromChain: '11155111', // Sepolia
    toChain: '11155111',
    fromToken: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', // Native ETH
    toToken: '0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8',   // USDC Sepolia
    fromAmount,
    fromAddress,
  };

  try {
    const { data } = await axios.get('https://li.quest/v1/quote', { params });
    res.json(data.transactionRequest);
  } catch (err: any) {
    console.error('LIFI API Error:', err.response?.data || err.message);
    res.status(500).json({
      error: 'Failed to fetch quote',
      details: err.response?.data || err.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

