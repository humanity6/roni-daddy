// AI Image Generation Service
// Handles communication with the FastAPI backend

const API_BASE_URL = 'http://192.168.100.4:8000'

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
  async generateImage(templateId, styleParams, imageFile = null, quality = 'medium', size = '1024x1024') {
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
   * @param {string} style - Photography style
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
  estimateCost(quality = 'medium', size = '1024x1024', hasReference = false) {
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