import axios from 'axios';
import { API_URL } from '../../config';

export const GoalService = {
  async getGoals() {
    const response = await axios.get(`${API_URL}/goals`);
    return response.data;
  },
  async getGoalsStatus() {
    const response = await axios.get(`${API_URL}/goals/status`);
    return response.data;
  },
  async getGoalsSummary() {
    const response = await axios.get(`${API_URL}/goals/summary`);
    return response.data;
  },
  async createGoal(goal) {
    const response = await axios.post(`${API_URL}/goals`, goal);
    return response.data;
  },
  async updateGoal(id, goal) {
    const response = await axios.put(`${API_URL}/goals/${id}`, goal);
    return response.data;
  },
  async archiveGoal(id) {
    const response = await axios.post(`${API_URL}/goals/${id}/archive`);
    return response.data;
  },
  async deleteGoal(id) {
    await axios.delete(`${API_URL}/goals/${id}`);
  }
};