import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function loginUser(payload) {
  return api.post('/auth/login', payload)
}

export async function registerUser(payload) {
  return api.post('/auth/register', payload)
}

export async function fetchCurrentUser() {
  return api.get('/users/me')
}

export function getApiErrorMessage(error, fallback = 'Something went wrong.') {
  const data = error.response?.data

  if (!data) {
    return fallback
  }

  if (typeof data.detail === 'string') {
    return data.detail
  }

  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg).filter(Boolean).join(' ')
  }

  if (Array.isArray(data.details)) {
    return data.details
      .map((item) => {
        if (typeof item === 'string') return item
        if (item.field && item.message) return `${item.field}: ${item.message}`
        return item.message
      })
      .filter(Boolean)
      .join(' ')
  }

  return data.message || fallback
}

export async function fetchDashboard() {
  return api.get('/analytics/sales')
}

export async function fetchDashboardOverview() {
  return api.get('/analytics/dashboard')
}

export async function fetchCustomerInsights() {
  return api.get('/analytics/customers')
}

export async function fetchBasketAnalysis() {
  return api.get('/analytics/basket')
}

export async function fetchRecommendations(userId) {
  return api.get(`/recommendations/user/${userId}`)
}

export async function fetchForecast(productId) {
  return api.get(`/forecasting/product/${productId}`)
}

export async function fetchInsights(question) {
  return api.get('/insights/summary', { params: { question } })
}

export async function fetchProducts() {
  return api.get('/products')
}

export async function createProduct(payload) {
  return api.post('/products', payload)
}

export async function fetchReviewSentiment() {
  return api.get('/reviews/sentiment')
}

export async function ingestTransaction(payload) {
  return api.post('/transactions/ingest', payload)
}

export async function ingestOnlineOrder(payload) {
  return api.post('/transactions/orders', payload)
}

export async function ingestBrowsingEvent(payload) {
  return api.post('/transactions/browse', payload)
}

export async function fetchStreamEvents() {
  return api.get('/transactions/stream-events')
}
