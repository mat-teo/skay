import axios from 'axios';
import { API_URL } from '../config';

export const importService = {
  /**
   * Preview CSV before import
   * Uses the new JSON-based endpoint (not FormData)
   */
  async preview(file, options = {}) {
    const content = await file.text();
    const response = await axios.post(`${API_URL}/import/csv/preview`, {
      file_content: content,
      options
    });
    return response.data;
  },

  /**
   * Execute CSV import
   * Uses the new JSON-based endpoint (not FormData)
   */
  async execute(file, options = {}) {
    const content = await file.text();
    const response = await axios.post(`${API_URL}/import/csv/execute`, {
      file_content: content,
      options
    });
    return response.data;
  }
};