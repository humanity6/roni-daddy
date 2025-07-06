// AI Image Generation Service
// Handles communication with the FastAPI backend with Chinese API integration

// Use environment variable for API URL, fallback to Render production URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://pimpmycase.onrender.com'

class AIImageService {
  /**
   * Generate AI image based on template and style parameters
   * @param {string} templateId - Template identifier (e.g., 'retro-remix', 'funny-toon')
   * @param {Object} styleParams - Style parameters specific to the template
   * @param {File|null} imageFile - Reference image file (optional)
   * @param {string} quality - Image quality ('low', 'medium', 'high')
   * @param {string} size - Image size ('1024x1024', '1024x1536', '1536x1024')
   * @returns {Promise<Object>} Generation result
   */
  async generateImage(templateId, styleParams, imageFile = null, quality = 'medium', size = '1024x1536') {
    try {
      console.log('🔍 Service - generateImage called')
      console.log('🔍 Service - templateId:', templateId)
      console.log('🔍 Service - styleParams:', styleParams)
      console.log('🔍 Service - imageFile:', imageFile ? `${imageFile.name} (${imageFile.size} bytes)` : 'null')
      console.log('🔍 Service - quality:', quality)
      
      const formData = new FormData()
      formData.append('template_id', templateId)
      formData.append('style_params', JSON.stringify(styleParams))
      formData.append('quality', quality)
      formData.append('size', size)
      
      if (imageFile) {
        formData.append('image', imageFile)
        console.log('🔍 Service - Image file attached to form data')
      } else {
        console.log('🔍 Service - No image file provided')
      }

      console.log('🔍 Service - Making request to:', `${API_BASE_URL}/generate`)
      
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        body: formData,
      })

      console.log('🔍 Service - Response status:', response.status)
      console.log('🔍 Service - Response ok:', response.ok)

      if (!response.ok) {
        const errorData = await response.json()
        console.log('🔍 Service - Error response:', errorData)
        throw new Error(errorData.detail || 'Generation failed')
      }

      const result = await response.json()
      console.log('🔍 Service - Success response:', result)
      return result
    } catch (error) {
      console.error('AI Generation Error:', error)
      throw error
    }
  }

  /**
   * Get generated image URL
   * @param {string} filename - Generated image filename
   * @returns {string} Image URL
   */
  getImageUrl(filename) {
    return `${API_BASE_URL}/image/${filename}`
  }

  /**
   * Chinese API Integration Methods
   */

  /**
   * Check Chinese API health status
   * @returns {Promise<Object>} Health status response
   */
  async checkChineseAPIHealth() {
    try {
      console.log('🔍 Service - Checking Chinese API health')
      
      const response = await fetch(`${API_BASE_URL}/chinese-api/health`)
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Chinese API health:', result)
      return result
    } catch (error) {
      console.error('Chinese API Health Check Error:', error)
      return {
        chinese_api_available: false,
        fallback_available: true,
        message: `Health check failed: ${error.message}`
      }
    }
  }

  /**
   * Get available phone brands from Chinese API
   * @returns {Promise<Object>} Brands response with fallback
   */
  async getPhoneBrands() {
    try {
      console.log('🔍 Service - Getting phone brands from Chinese API')
      
      const response = await fetch(`${API_BASE_URL}/chinese-api/brands`)
      
      if (!response.ok) {
        throw new Error(`Brands request failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Brands received:', result)
      return result
    } catch (error) {
      console.error('Get Phone Brands Error:', error)
      throw error
    }
  }

  /**
   * Get available phone models for a specific brand
   * @param {string} brandId - Brand ID from Chinese API
   * @returns {Promise<Object>} Models response with fallback
   */
  async getPhoneModels(brandId) {
    try {
      console.log('🔍 Service - Getting phone models for brand:', brandId)
      
      const response = await fetch(`${API_BASE_URL}/chinese-api/brands/${brandId}/models`)
      
      if (!response.ok) {
        throw new Error(`Models request failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Models received:', result)
      return result
    } catch (error) {
      console.error('Get Phone Models Error:', error)
      throw error
    }
  }

  /**
   * Generate AI image and create order using Chinese API
   * @param {string} templateId - Template identifier
   * @param {Object} styleParams - Style parameters
   * @param {string} mobileModelId - Chinese API model ID
   * @param {File|null} imageFile - Reference image file
   * @param {string} quality - Image quality
   * @param {string} size - Image size
   * @returns {Promise<Object>} Generation and order result
   */
  async generateAndOrder(templateId, styleParams, mobileModelId, imageFile = null, quality = 'medium', size = '1024x1536') {
    try {
      console.log('🔍 Service - Generate and Order with Chinese API')
      console.log('🔍 Service - templateId:', templateId)
      console.log('🔍 Service - mobileModelId:', mobileModelId)
      console.log('🔍 Service - styleParams:', styleParams)
      
      const formData = new FormData()
      formData.append('template_id', templateId)
      formData.append('style_params', JSON.stringify(styleParams))
      formData.append('mobile_model_id', mobileModelId)
      formData.append('quality', quality)
      formData.append('size', size)
      
      if (imageFile) {
        formData.append('image', imageFile)
        console.log('🔍 Service - Image file attached to form data')
      }

      console.log('🔍 Service - Making request to:', `${API_BASE_URL}/chinese-api/generate-and-order`)
      
      const response = await fetch(`${API_BASE_URL}/chinese-api/generate-and-order`, {
        method: 'POST',
        body: formData,
      })

      console.log('🔍 Service - Response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json()
        console.log('🔍 Service - Error response:', errorData)
        throw new Error(errorData.detail || 'Generation and order failed')
      }

      const result = await response.json()
      console.log('🔍 Service - Success response:', result)
      return result
    } catch (error) {
      console.error('Generate and Order Error:', error)
      throw error
    }
  }

  /**
   * Get order status from Chinese API
   * @param {Array<string>} thirdIds - Array of third-party order IDs
   * @returns {Promise<Object>} Order status response
   */
  async getOrderStatus(thirdIds) {
    try {
      console.log('🔍 Service - Getting order status for:', thirdIds)
      
      const thirdIdsParam = thirdIds.join(',')
      const response = await fetch(`${API_BASE_URL}/chinese-api/orders/status?third_ids=${encodeURIComponent(thirdIdsParam)}`)
      
      if (!response.ok) {
        throw new Error(`Order status request failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Order status received:', result)
      return result
    } catch (error) {
      console.error('Get Order Status Error:', error)
      throw error
    }
  }

  /**
   * Get payment status from Chinese API
   * @param {Array<string>} thirdIds - Array of third-party payment IDs
   * @returns {Promise<Object>} Payment status response
   */
  async getPaymentStatus(thirdIds) {
    try {
      console.log('🔍 Service - Getting payment status for:', thirdIds)
      
      const thirdIdsParam = thirdIds.join(',')
      const response = await fetch(`${API_BASE_URL}/chinese-api/payment/status?third_ids=${encodeURIComponent(thirdIdsParam)}`)
      
      if (!response.ok) {
        throw new Error(`Payment status request failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Payment status received:', result)
      return result
    } catch (error) {
      console.error('Get Payment Status Error:', error)
      throw error
    }
  }

  /**
   * Get printing queue from Chinese API
   * @returns {Promise<Object>} Printing queue response
   */
  async getPrintingQueue() {
    try {
      console.log('🔍 Service - Getting printing queue')
      
      const response = await fetch(`${API_BASE_URL}/chinese-api/printing-queue`)
      
      if (!response.ok) {
        throw new Error(`Printing queue request failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('🔍 Service - Printing queue received:', result)
      return result
    } catch (error) {
      console.error('Get Printing Queue Error:', error)
      throw error
    }
  }

  /**
   * Get available styles for a template
   * @param {string} templateId - Template identifier
   * @returns {Promise<Object>} Available styles/options
   */
  async getTemplateStyles(templateId) {
    try {
      const response = await fetch(`${API_BASE_URL}/styles/${templateId}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch template styles')
      }

      return await response.json()
    } catch (error) {
      console.error('Template Styles Error:', error)
      throw error
    }
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      return await response.json()
    } catch (error) {
      console.error('Health Check Error:', error)
      throw error
    }
  }

  /**
   * Convert image file to data URL for preview
   * @param {File} file - Image file
   * @returns {Promise<string>} Data URL
   */
  async fileToDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  /**
   * Template-specific generation helpers
   */

  /**
   * Generate Retro Remix image
   * @param {string} keyword - Retro style keyword
   * @param {string} optionalText - Optional text to include
   * @param {File} imageFile - Reference image
   * @param {string} quality - Image quality
   * @returns {Promise<Object>} Generation result
   */
  async generateRetroRemix(keyword, optionalText = '', imageFile, quality = 'medium') {
    const styleParams = {
      keyword,
      optional_text: optionalText
    }
    
    return this.generateImage('retro-remix', styleParams, imageFile, quality)
  }

  /**
   * Generate Funny Toon image
   * @param {string} style - Cartoon style
   * @param {File} imageFile - Reference image
   * @param {string} quality - Image quality
   * @returns {Promise<Object>} Generation result
   */
  async generateFunnyToon(style, imageFile, quality = 'medium') {
    const styleParams = { style }
    
    return this.generateImage('funny-toon', styleParams, imageFile, quality)
  }

  /**
   * Generate Cover Shoot image
   * @param {string} style - Cover shoot style
   * @param {File} imageFile - Reference image
   * @param {string} quality - Image quality
   * @returns {Promise<Object>} Generation result
   */
  async generateCoverShoot(style, imageFile, quality = 'medium') {
    const styleParams = { style }
    return this.generateImage('cover-shoot', styleParams, imageFile, quality)
  }

  /**
   * Generate Glitch Pro image
   * @param {string} mode - Glitch mode
   * @param {File} imageFile - Reference image
   * @param {string} quality - Image quality
   * @returns {Promise<Object>} Generation result
   */
  async generateGlitchPro(mode, imageFile, quality = 'medium') {
    const styleParams = { style: mode }
    
    return this.generateImage('glitch-pro', styleParams, imageFile, quality)
  }

  /**
   * Generate Footy Fan image
   * @param {string} team - Team name
   * @param {string} style - Fan style
   * @param {File} imageFile - Reference image
   * @param {string} quality - Image quality
   * @returns {Promise<Object>} Generation result
   */
  async generateFootyFan(team, style, imageFile, quality = 'medium') {
    const styleParams = { team, style }
    
    return this.generateImage('footy-fan', styleParams, imageFile, quality)
  }

  /**
   * Estimate generation cost (placeholder - can be enhanced)
   * @param {string} quality - Image quality
   * @param {string} size - Image size
   * @param {boolean} hasReference - Whether reference image is used
   * @returns {Object} Cost estimation
   */
  estimateCost(quality = 'medium', size = '1024x1536', hasReference = false) {
    const tokenMap = {
      'low': { '1024x1024': 272, '1024x1536': 408, '1536x1024': 400 },
      'medium': { '1024x1024': 1056, '1024x1536': 1584, '1536x1024': 1568 },
      'high': { '1024x1024': 4160, '1024x1536': 6240, '1536x1024': 6208 }
    }

    const outputTokens = tokenMap[quality]?.[size] || 1056
    const outputCost = (outputTokens * 40.00) / 1_000_000  // $40 per 1M output tokens
    
    let inputCost = 0.0001  // Base input text cost
    if (hasReference) {
      inputCost += (1000 * 10.00) / 1_000_000  // ~1000 tokens per reference image at $10 per 1M
    }

    return {
      outputTokens,
      totalCost: outputCost + inputCost,
      breakdown: `${outputTokens} output tokens, ${hasReference ? 'with' : 'no'} reference image`
    }
  }
}

// Export singleton instance
export default new AIImageService() 