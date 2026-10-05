import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
});

export const getHealth = () => api.get('/api/health').then(({ data }) => data);
export const getModelInfo = () => api.get('/api/model-info').then(({ data }) => data);
export const getPrediction = (payload) => api.post('/api/predict', payload).then(({ data }) => data);

export function getApiErrorMessage(error) {
  if (error?.response?.status === 422) {
    const detail = error.response.data?.detail;
    if (Array.isArray(detail)) return 'Please review the highlighted fields and try again.';
    return detail || 'Some values were not accepted. Please review the form.';
  }
  if (error?.response) return error.response.data?.detail || 'The prediction service could not complete this request.';
  return 'The prediction service is unavailable. Check that the backend is running, then try again.';
}

export default api;
