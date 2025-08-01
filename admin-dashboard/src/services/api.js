import axios from 'axios'

// API base URL - use environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('🔄 API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

// API functions
export const adminApi = {
  // Dashboard stats
  getStats: () => api.get('/api/admin/stats'),
  getTemplateAnalytics: () => api.get('/api/admin/template-analytics'),
  
  // Orders
  getOrders: (limit = 50) => api.get(`/api/admin/orders?limit=${limit}`),
  getOrder: (orderId) => api.get(`/api/orders/${orderId}`),
  updateOrderStatus: (orderId, status, chineseData = {}) => {
    return api.put(`/api/orders/${orderId}/status`, {
      status,
      chinese_data: chineseData
    })
  },
  
  // Brands
  getBrands: (includeUnavailable = true) => api.get(`/api/brands?include_unavailable=${includeUnavailable}`),
  
  // Phone Models
  getModels: (brandId, includeUnavailable = true) => api.get(`/api/brands/${brandId}/models?include_unavailable=${includeUnavailable}`),
  updateModelStock: (modelId, stock) => {
    return api.put(`/api/admin/models/${modelId}/stock`, { stock })
  },
  // Batch update for models
  batchUpdateModels: (updates) => {
    return api.put('/api/admin/models/batch', { updates })
  },
  createModel: (modelData) => {
    const formData = new FormData()
    Object.keys(modelData).forEach(key => {
      formData.append(key, modelData[key])
    })
    return api.post('/api/admin/models', formData)
  },
  updateModel: (modelId, modelData) => {
    const formData = new FormData()
    Object.keys(modelData).forEach(key => {
      formData.append(key, modelData[key])
    })
    return api.put(`/api/admin/models/${modelId}`, formData)
  },
  deleteModel: (modelId) => api.delete(`/api/admin/models/${modelId}`),
  toggleModelFeatured: (modelId) => api.put(`/api/admin/models/${modelId}/toggle-featured`),
  
  // Templates
  getTemplates: (includeInactive = true) => api.get(`/api/templates?include_inactive=${includeInactive}`),
  updateTemplatePrice: (templateId, price) => {
    return api.put(`/api/admin/templates/${templateId}/price`, { price })
  },
  // Batch update for template prices
  batchUpdateTemplatePrices: (updates) => {
    return api.put('/api/admin/templates/batch-price', { updates })
  },
  
  // Fonts
  getFonts: (includeInactive = true) => api.get(`/api/fonts?include_inactive=${includeInactive}`),
  createFont: (fontData) => {
    const formData = new FormData()
    Object.keys(fontData).forEach(key => {
      formData.append(key, fontData[key])
    })
    return api.post('/api/admin/fonts', formData)
  },
  updateFont: (fontId, fontData) => {
    const formData = new FormData()
    Object.keys(fontData).forEach(key => {
      formData.append(key, fontData[key])
    })
    return api.put(`/api/admin/fonts/${fontId}`, formData)
  },
  deleteFont: (fontId) => api.delete(`/api/admin/fonts/${fontId}`),
  toggleFontActivation: (fontId) => api.put(`/api/admin/fonts/${fontId}/toggle`),
  
  // Colors
  getColors: (colorType, includeInactive = true) => api.get(`/api/colors/${colorType}?include_inactive=${includeInactive}`),
  createColor: (colorData) => {
    const formData = new FormData()
    Object.keys(colorData).forEach(key => {
      if (key === 'css_classes' && typeof colorData[key] === 'object') {
        formData.append(key, JSON.stringify(colorData[key]))
      } else {
        formData.append(key, colorData[key])
      }
    })
    return api.post('/api/admin/colors', formData)
  },
  updateColor: (colorId, colorData) => {
    const formData = new FormData()
    Object.keys(colorData).forEach(key => {
      if (key === 'css_classes' && typeof colorData[key] === 'object') {
        formData.append(key, JSON.stringify(colorData[key]))
      } else {
        formData.append(key, colorData[key])
      }
    })
    return api.put(`/api/admin/colors/${colorId}`, formData)
  },
  deleteColor: (colorId) => api.delete(`/api/admin/colors/${colorId}`),
  toggleColorActivation: (colorId) => api.put(`/api/admin/colors/${colorId}/toggle`),
  
  
  // Health check
  getHealth: () => api.get('/health'),
  getDatabaseStats: () => api.get('/api/admin/database-stats'),
  
  // Chinese API integration
  submitOrderToChinese: (orderId) => {
    return api.post('/api/chinese/submit-order', { order_id: orderId })
  },
  
  // Images
  getImages: (limit = 100, imageType = null) => {
    const params = new URLSearchParams({ limit })
    if (imageType && imageType !== 'all') {
      params.append('image_type', imageType)
    }
    return api.get(`/api/admin/images?${params}`)
  },
  
  // Image serving
  getImageUrl: (filename) => `${API_BASE_URL}/image/${filename}`,
}

export default api