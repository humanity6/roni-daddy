import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'
import CircleSubmitButton from '../components/CircleSubmitButton'

const SamsungModelScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { actions } = useAppState()
  const [selectedModel, setSelectedModel] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [samsungModels, setSamsungModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Get parameters from navigation state
  const { deviceId, chineseBrandId, apiModels, brandData } = location.state || {}
  
  // Extract brand information from Chinese API data or fallback
  const brandName = brandData?.name?.toUpperCase() || brandData?.display_name?.toUpperCase() || 'SAMSUNG'
  const brandDisplayName = brandData?.display_name || brandData?.name || 'Samsung'

  // No fallback models - Chinese API is required
  console.log('SamsungModelScreen - Parameters:', { deviceId, chineseBrandId, apiModels })

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      setLoading(true)
      setError(null)
      
      if (!deviceId) {
        throw new Error('Device ID is required for stock lookup')
      }
      
      // Use API models if passed from brand screen, otherwise fetch fresh data
      if (apiModels && apiModels.length > 0) {
        console.log('✅ SamsungModelScreen - Using pre-loaded API models:', apiModels.length)
        setSamsungModels(apiModels)
        setSelectedModel(apiModels[0]?.mobile_model_name || apiModels[0]?.name || apiModels[0]?.display_name || 'Unknown Model')
      } else {
        console.log(`🔄 SamsungModelScreen - Fetching models from Chinese API for ${brandDisplayName}...`)
        
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const response = await fetch(`${API_BASE_URL}/api/chinese/stock/${deviceId}/${chineseBrandId}`)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch ${brandDisplayName} models: ${response.status} ${response.statusText}`)
        }
        
        const result = await response.json()
        
        if (!result.success) {
          throw new Error(`${brandDisplayName} models API error: ${result.error || 'Unknown error'}`)
        }
        
        if (!result.available_items || result.available_items.length === 0) {
          throw new Error(`No ${brandDisplayName} models available with current stock`)
        }
        
        console.log(`✅ SamsungModelScreen - Models loaded from Chinese API:`, result.available_items)
        setSamsungModels(result.available_items)
        setSelectedModel(result.available_items[0]?.mobile_model_name || result.available_items[0]?.name || 'Unknown Model')
      }
    } catch (error) {
      console.error('❌ SamsungModelScreen - Error loading models:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = () => {
    if (!selectedModel) {
      alert('Please select a model')
      return
    }
    
    // Find the selected model object from the models array
    const selectedModelObj = samsungModels.find(model => 
      (model.mobile_model_name || model.name || model.display_name) === selectedModel
    )
    
    if (!selectedModelObj) {
      alert('Selected model not found')
      return
    }
    
    // Pass Chinese model data to app state including dimensions
    const selectedModelData = {
      brand: brandData?.name?.toLowerCase() || brandData?.display_name?.toLowerCase() || 'samsung',
      model: selectedModelObj.mobile_model_name || selectedModelObj.name || selectedModelObj.display_name,
      chinese_model_id: selectedModelObj.mobile_model_id || selectedModelObj.chinese_model_id || selectedModelObj.id,
      price: selectedModelObj.price,
      stock: selectedModelObj.stock,
      device_id: deviceId,
      // Chinese API dimensions in millimeters
      width: selectedModelObj.width ? parseFloat(selectedModelObj.width) : null,
      height: selectedModelObj.height ? parseFloat(selectedModelObj.height) : null,
      mobile_shell_id: selectedModelObj.mobile_shell_id
    }
    
    console.log('SamsungModelScreen - Selected model data:', selectedModelData)
    
    actions.setPhoneSelection(selectedModelData.brand, selectedModelData.model, selectedModelData)
    navigate('/template-selection', { 
      state: { 
        selectedModelData,
        deviceId 
      }
    })
  }

  const handleBack = () => {
    navigate('/phone-brand')
  }

  // Loading state
  if (loading) {
    return (
      <div 
        style={{ 
          height: '100vh',
          background: '#f8f8f8',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          position: 'relative',
          overflow: 'hidden',
          fontFamily: 'PoppinsLight, sans-serif',
        }}
      >
        <PastelBlobs />
        
        <div style={{ 
          position: 'relative', 
          zIndex: 10,
          textAlign: 'center',
          color: '#474746'
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
          <h2 style={{ fontSize: '24px', margin: '0' }}>Loading {brandDisplayName} Models...</h2>
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
    <div 
      style={{ 
        height: '100vh',
        background: '#f8f8f8',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        padding: '20px',
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'PoppinsLight, sans-serif'
      }}
    >
      {/* Pastel Blobs Background */}
      <PastelBlobs />

      {/* Back Arrow */}
      <button
        onClick={handleBack}
        style={{
          position: 'absolute',
          top: '20px',
          left: '30px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'white',
          border: `5px solid ${brandData?.button_color || '#0066cc'}`,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 20,
          transition: 'transform 0.2s ease'
        }}
        onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
        onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke={brandData?.button_color || "#0066cc"} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Header */}
      <div
        style={{
          position: 'relative',
          width: '380px',
          height: '140px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '0px',
          marginTop: '60px',
          zIndex: 10
        }}
      >
        <img
          src={brandData?.image_path || "/samsung blob.svg"}
          alt="Header Background"
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            zIndex: -1
          }}
        />
        <h1 
          style={{
            fontSize: '36px',
            fontWeight: 'bold',
            color: '#474746',
            textAlign: 'center',
            margin: '0',
            fontFamily: 'Cubano, sans-serif',
            letterSpacing: '1px',
            whiteSpace: 'nowrap',
            position: 'relative',
            zIndex: 1
          }}
        >
          {brandName} MODEL
        </h1>
      </div>

      {/* Phone Case Container - Centered */}
      <div
        style={{
          position: 'relative',
          width: '320px',
          height: '460px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10,
          alignSelf: 'center',
          marginTop: '20px'
        }}
      >
        {/* Phone Case Image */}
        <img 
          src="/phone cover cropped.png"
          alt="Phone Case"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain'
          }}
        />

        {/* Model Selector Dropdown - Moved above submit button */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '180px',
            zIndex: 200
          }}
        >
          <div
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{
              background: '#474746',
              borderRadius: '30px',
              padding: '10px 0px 10px 22px',
              cursor: 'pointer',
              border: '8px solid #ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: 'PoppinsLight, sans-serif',
              fontSize: '14px',
              fontWeight: '600',
              color: '#ffffff'
            }}
          >
            <span style={{ whiteSpace: 'wrap' }}>{selectedModel}</span>
            <div
              style={{
                width: '40px',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderLeft: '6px solid #ffffff',
                marginTop: '-20px',
                marginBottom: '-20px',
                paddingTop: '20px',
                paddingBottom: '20px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 9L12 15L18 9" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>

          {/* Dropdown Options */}
          {dropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: '0',
                right: '0',
                background: 'white',
                borderRadius: '15px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
                maxHeight: '200px',
                overflowY: 'auto',
                zIndex: 300,
                marginTop: '5px'
              }}
            >
              {samsungModels.map((model, index) => (
                <div
                  key={index}
                  onClick={() => {
                    setSelectedModel(model.mobile_model_name || model.name || model.display_name || 'Unknown Model')
                    setDropdownOpen(false)
                  }}
                  style={{
                    padding: '12px 20px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    color: '#333',
                    borderBottom: index < samsungModels.length - 1 ? '1px solid #eee' : 'none',
                    fontFamily: 'PoppinsLight, sans-serif',
                    transition: 'background-color 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  {model.mobile_model_name || model.name || model.display_name || 'Unknown Model'}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <CircleSubmitButton
          onClick={handleSubmit}
          label="Submit"
          color={brandData?.button_color || "#deecd0"}
          position="absolute"
          style={{
            bottom: '60px',
            left: '50%',
            transform: 'translateX(-50%)'
          }}
        />
      </div>
    </div>
  )
}

export default SamsungModelScreen 