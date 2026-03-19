import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// Usar proxy de Vite en desarrollo (puerto 5173)
const API_BASE_URL = '/api/v1'

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Servicios de API
export const authService = {
  login: (username, password) => 
    apiClient.post('/auth/login', { username, password }),
  
  register: (username, email, password) => 
    apiClient.post('/auth/register', { username, email, password }),
  
  getMe: () => apiClient.get('/auth/me'),
}

export const characterService = {
  getAll: (params) => apiClient.get('/characters', { params }),
  getById: (id) => apiClient.get(`/characters/${id}`),
  create: (data) => apiClient.post('/characters', data),
  update: (id, data) => apiClient.put(`/characters/${id}`, data),
  delete: (id) => apiClient.delete(`/characters/${id}`),
}

export const chatService = {
  getAll: () => apiClient.get('/chat'),
  getById: (id) => apiClient.get(`/chat/${id}`),
  getMessages: (id, limit = 50) => apiClient.get(`/chat/${id}/messages`, { params: { limit } }),
  create: (characterId, title) => apiClient.post('/chat', { character_id: characterId, title }),
  sendMessage: (chatId, message, options = {}) => 
    apiClient.post(`/chat/${chatId}/message`, { 
      message, 
      generate_image: options.generateImage || false,
      generate_audio: options.generateAudio || false,
      image_prompt: options.imagePrompt || null,
    }),
  delete: (id) => apiClient.delete(`/chat/${id}`),
}

export const imageService = {
  generate: (data) => apiClient.post('/images/generate', data),
  getCharacterImages: (characterId) => apiClient.get(`/images/character/${characterId}`),
}

export default apiClient
