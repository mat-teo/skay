// frontend/src/components/stocks/StockService.js
import axios from 'axios';
import { API_URL } from '../../config';

export const StockService = {
  async getPortfolio() {
    const response = await axios.get(`${API_URL}/stocks/portfolio`);
    return response.data;
  },

  async addStock(stock) {
    const response = await axios.post(`${API_URL}/stocks`, stock);
    return response.data;
  },

  async updateStock(id, stock) {
    const response = await axios.put(`${API_URL}/stocks/${id}`, stock);
    return response.data;
  },

  async deleteStock(id) {
    await axios.delete(`${API_URL}/stocks/${id}`);
  },

  async refreshPrices() {
    const response = await axios.post(`${API_URL}/stocks/refresh-prices`);
    return response.data;
  }
};