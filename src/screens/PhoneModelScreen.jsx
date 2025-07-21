import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import aiImageService from '../services/aiImageService'

const PhoneModelScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, apiSource } = location.state || {}
  
  const [selectedModel, setSelectedModel] = useState('')
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  // Fallback models based on brand
  const getFallbackModels = (brandId) => {
    switch (brandId?.toLowerCase()) {
      case 'iphone':
        return [
          'iPhone 16 Pro Max', 'iPhone 16 Pro', 'iPhone 16 Plus', 'iPhone 16',
          'iPhone 15 Pro Max', 'iPhone 15 Pro', 'iPhone 15 Plus', 'iPhone 15',
          'iPhone 14 Pro Max', 'iPhone 14 Pro', 'iPhone 14 Plus', 'iPhone 14',
          'iPhone 13 Pro Max', 'iPhone 13 Pro', 'iPhone 13 Mini', 'iPhone 13'
        ]
      case 'samsung':
        return [
          'Galaxy S24 Ultra', 'Galaxy S24+', 'Galaxy S24',
          'Galaxy S23 Ultra', 'Galaxy S23+', 'Galaxy S23',
          'Galaxy S22 Ultra', 'Galaxy S22+', 'Galaxy S22',
          'Galaxy Note 20 Ultra', 'Galaxy Note 20'
        ]
      case 'google':
        return [
          'Pixel 8 Pro', 'Pixel 8', 'Pixel 7a', 'Pixel 7 Pro', 'Pixel 7',
          'Pixel 6a', 'Pixel 6 Pro', 'Pixel 6'
        ]
      default:
        return ['Model 1', 'Model 2', 'Model 3']
    }
  }

  // Load models on component mount
  useEffect(() => {
    if (brand) {
      loadModels()
    } else {
      // Redirect back if no brand data
      navigate('/phone-brand')
    }
  }, [brand])

  const loadModels = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔄 PhoneModelScreen - Loading models for brand:', brand.chinese_api_id || brand.id)
      
      if (apiSource === 'chinese_api' && brand.chinese_api_id) {
        // Try Chinese API first
        const response = await aiImageService.getPhoneModels(brand.chinese_api_id)
        
        if (response.success && response.models) {
          setModels(response.models)
          // Set first available model as default
          const availableModel = response.models.find(m => m.available)
          if (availableModel) {
            setSelectedModel(availableModel.name)
          }
          console.log('✅ PhoneModelScreen - Models loaded from Chinese API')
          return
        }
      }
      
      // Fallback to hardcoded models
      console.log('🔄 PhoneModelScreen - Using fallback models')
      const fallbackModelNames = getFallbackModels(brand.id)
      const fallbackModels = fallbackModelNames.map((name, index) => ({
        id: `${brand.id}-model-${index}`,
        name: name,
        price: 17.99,
        stock: 10,
        available: true
      }))
      
      setModels(fallbackModels)
      
      // Set preferred default model based on brand
      let defaultModel = fallbackModelNames[0]
      if (brand.id?.toLowerCase() === 'iphone') {
        const iphone16Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('iphone 16') && !name.toLowerCase().includes('pro') && !name.toLowerCase().includes('plus')
        )
        if (iphone16Index >= 0) {
          defaultModel = fallbackModelNames[iphone16Index]
        }
      } else if (brand.id?.toLowerCase() === 'samsung') {
        const galaxyS24Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('galaxy s24') && !name.toLowerCase().includes('ultra') && !name.toLowerCase().includes('+')
        )
        if (galaxyS24Index >= 0) {
          defaultModel = fallbackModelNames[galaxyS24Index]
        }
      } else if (brand.id?.toLowerCase() === 'google') {
        const pixel8Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('pixel 8') && !name.toLowerCase().includes('pro')
        )
        if (pixel8Index >= 0) {
          defaultModel = fallbackModelNames[pixel8Index]
        }
      }
      
      setSelectedModel(defaultModel)
      setError('Using fallback data - Chinese API unavailable')
      
    } catch (error) {
      console.error('❌ PhoneModelScreen - Failed to load models:', error)
      
      // Use fallback models
      const fallbackModelNames = getFallbackModels(brand.id)
      const fallbackModels = fallbackModelNames.map((name, index) => ({
        id: `${brand.id}-model-${index}`,
        name: name,
        price: 17.99,
        stock: 10,
        available: true
      }))
      
      setModels(fallbackModels)
      
      // Set preferred default model based on brand
      let defaultModel = fallbackModelNames[0]
      if (brand.id?.toLowerCase() === 'iphone') {
        const iphone16Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('iphone 16') && !name.toLowerCase().includes('pro') && !name.toLowerCase().includes('plus')
        )
        if (iphone16Index >= 0) {
          defaultModel = fallbackModelNames[iphone16Index]
        }
      } else if (brand.id?.toLowerCase() === 'samsung') {
        const galaxyS24Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('galaxy s24') && !name.toLowerCase().includes('ultra') && !name.toLowerCase().includes('+')
        )
        if (galaxyS24Index >= 0) {
          defaultModel = fallbackModelNames[galaxyS24Index]
        }
      } else if (brand.id?.toLowerCase() === 'google') {
        const pixel8Index = fallbackModelNames.findIndex(name => 
          name.toLowerCase().includes('pixel 8') && !name.toLowerCase().includes('pro')
        )
        if (pixel8Index >= 0) {
          defaultModel = fallbackModelNames[pixel8Index]
        }
      }
      
      setSelectedModel(defaultModel)
      setError(`Failed to load models: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = () => {
    const selectedModelData = models.find(m => m.name === selectedModel)
    navigate('/template-selection', {
      state: {
        brand: brand,
        model: selectedModelData,
        apiSource: apiSource
      }
    })
  }

  const handleBack = () => {
    navigate('/phone-brand')
  }

  // Loading state
  if (loading) {
    return (
      <div className="screen-container" style={{ background: '#FFFFFF' }}>
        <PastelBlobs />
        
        <div style={{ 
          position: 'relative', 
          zIndex: 10,
          textAlign: 'center',
          color: '#474746',
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e3e3e3',
            borderTop: '4px solid #474746',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <h2 style={{ fontSize: '24px', margin: '0', fontFamily: 'Cubano, sans-serif' }}>
            Loading {brand?.display_name} Models...
          </h2>
          <p style={{ fontSize: '16px', margin: '10px 0 0', opacity: 0.7 }}>
            Getting latest inventory...
          </p>
        </div>
        
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      <PastelBlobs />

      {/* API Source Indicator */}
      {!error && (
        <div
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: apiSource === 'chinese_api' ? '#d7efd4' : '#fff2cc',
            padding: '8px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            color: '#474746',
            zIndex: 10,
            border: '1px solid rgba(71, 71, 70, 0.1)'
          }}
        >
          {apiSource === 'chinese_api' ? '🟢 Live Inventory' : '🟡 Fallback Mode'}
        </div>
      )}

      {/* Error indicator with retry */}
      {error && (
        <div
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            right: '20px',
            background: '#ffe6e6',
            padding: '12px',
            borderRadius: '12px',
            fontSize: '14px',
            color: '#cc0000',
            textAlign: 'center',
            zIndex: 10,
            border: '1px solid #ffcccc'
          }}
        >
          <div style={{ marginBottom: '8px' }}>
            {error}
          </div>
          <button
            onClick={loadModels}
            style={{
              background: '#474746',
              color: 'white',
              border: 'none',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      )}

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-12">
        {/* Back Arrow */}
        <div className="w-full flex justify-start mb-8">
          <button
            onClick={handleBack}
            className="w-12 h-12 rounded-full bg-white border-4 border-blue-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
          >
            <ArrowLeft size={20} className="text-blue-500" />
          </button>
        </div>

        {/* Brand Header */}
        <div className="mb-8">
          <h1 
            className="text-4xl font-black text-[#2F3842] leading-tight text-center"
            style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}
          >
            {brand?.display_name} MODELS
          </h1>
          <p className="text-lg text-gray-600 text-center mt-2" style={{ fontFamily: 'Poppins, sans-serif' }}>
            Choose your {brand?.display_name} model
          </p>
        </div>

        {/* Model Dropdown */}
        <div className="w-full max-w-sm mb-8">
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="w-full bg-blue-100 text-gray-800 font-medium py-4 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg border-2 border-blue-200"
              style={{ fontFamily: 'Poppins, sans-serif' }}
            >
              {selectedModel || 'Select Model'}
              <span className="absolute right-6 top-1/2 transform -translate-y-1/2">
                {dropdownOpen ? '▲' : '▼'}
              </span>
            </button>
            
            {dropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-200 max-h-60 overflow-y-auto z-20">
                {models.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => {
                      setSelectedModel(model.name)
                      setDropdownOpen(false)
                    }}
                    disabled={!model.available}
                    className={`w-full text-left px-6 py-3 hover:bg-blue-50 transition-colors ${
                      selectedModel === model.name ? 'bg-blue-100 font-semibold' : ''
                    } ${!model.available ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    style={{ fontFamily: 'Poppins, sans-serif' }}
                  >
                    <div className="flex justify-between items-center">
                      <span>{model.name}</span>
                      <div className="text-sm text-gray-500">
                        {model.price ? `£${model.price}` : ''}
                        {model.stock !== undefined && (
                          <span className="ml-2">
                            {model.available ? `(${model.stock} left)` : '(Out of stock)'}
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Selected Model Info */}
        {selectedModel && (
          <div className="w-full max-w-sm mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
              <div className="text-center">
                <p className="text-lg font-medium text-gray-800" style={{ fontFamily: 'Poppins, sans-serif' }}>
                  {selectedModel}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {brand?.display_name} • Ready to customize
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={!selectedModel}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-transform ${
            selectedModel 
              ? 'bg-pink-400 text-white active:scale-95 cursor-pointer shadow-xl' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          style={{ fontFamily: 'Cubano, sans-serif' }}
        >
          <span className="font-semibold text-sm">Next</span>
        </button>
      </div>
    </div>
  )
}

export default PhoneModelScreen 