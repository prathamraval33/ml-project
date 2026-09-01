import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchMovies = async (params = {}) => {
  const { data } = await api.get('/movies', { params });
  return data;
};

export const fetchMovieDetail = async (movieId) => {
  const { data } = await api.get(`/movies/${movieId}`);
  return data;
};

export const fetchTrends = async () => {
  const { data } = await api.get('/trends');
  return data;
};

export const fetchGlobalShap = async () => {
  const { data } = await api.get('/shap/global');
  return data;
};

export const fetchAblationResults = async () => {
  const { data } = await api.get('/shap/ablation');
  return data;
};

export const fetchMovieShap = async (movieId) => {
  const { data } = await api.get(`/shap/${movieId}`);
  return data;
};

export const predictMovie = async (payload) => {
  const { data } = await api.post('/predict', payload);
  return data;
};

export const runWhatIfSimulation = async (payload) => {
  const { data } = await api.post('/whatif', payload);
  return data;
};

export default api;
