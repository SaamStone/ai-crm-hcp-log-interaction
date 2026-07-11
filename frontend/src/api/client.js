import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL: API_BASE })

export const sendChatMessage = (sessionId, message, formState) =>
  api.post('/api/chat', { session_id: sessionId, message, form_state: formState }).then((r) => r.data)

export const saveInteraction = (formState) =>
  api.post('/api/interactions', formState).then((r) => r.data)

export const fetchHcps = () => api.get('/api/hcps').then((r) => r.data)
