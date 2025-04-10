import axios from 'axios'

export const useApi = () => {
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  return { api }
} 