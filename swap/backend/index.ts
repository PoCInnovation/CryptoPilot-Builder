import express from 'express';
import axios from 'axios';
import cors from 'cors';

const app = express();
const PORT = 3001;

app.use(cors());

app.get('/quote', async (req, res) => {
  const { fromAddress, fromAmount } = req.query;

  const params = {
    fromChain: '1', // Ethereum mainnet
    toChain: '1',
    fromToken: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', // Native ETH
    toToken: '0xA0b86a33E6417c7D0F2fd8C8024B92B3b6e08bD4',   // USDC mainnet
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

