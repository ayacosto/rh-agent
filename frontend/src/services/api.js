import axios from "axios"
import { getToken, logout } from "./auth"

const api = axios.create({
  baseURL: "/api"
})

// Injecter le token JWT dans chaque requête
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Rediriger vers login si token expiré
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout()
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

export async function loginRequest(email, password) {
  const response = await api.post("/auth/login", { email, password })
  return response.data
}

export async function fetchMe() {
  const response = await api.get("/auth/me")
  return response.data
}

export async function sendMessage(question) {
  const response = await api.post("/chat", { question })
  return response.data
}

export async function fetchHistory() {
  const response = await api.get("/chat/history")
  return response.data
}