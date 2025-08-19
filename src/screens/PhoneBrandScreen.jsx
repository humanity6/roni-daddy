import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PastelBlobs from '../components/PastelBlobs'
import aiImageService from '../services/aiImageService'
import { useAppState } from '../contexts/AppStateContext'

const PhoneBrandScreen = () => {
  const navigate = useNavigate()
  const { state: appState } = useAppState()
  const [selectedBrand, setSelectedBrand] = useState('')
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)
  const [apiModels, setApiModels] = useState({})
  const [error, setError] = useState(null)

  // Get device_id from vending machine session or directly from URL parameters
  const currentUrl = window.location.href
  const urlParams = new URLSearchParams(window.location.search)
  
  // Also try manual extraction as backup
  const deviceIdMatch = currentUrl.match(/device_id=([^&]+)/)
  const deviceIdFromUrl = urlParams.get('device_id') || (deviceIdMatch ? deviceIdMatch[1] : null)
  const deviceId = appState.vendingMachineSession?.deviceId || deviceIdFromUrl
  
  console.log('PhoneBrandScreen - Device ID from session:', appState.vendingMachineSession?.deviceId)
  console.log('PhoneBrandScreen - Device ID from URL:', deviceIdFromUrl)
  console.log('PhoneBrandScreen - Final Device ID:', deviceId)
  console.log('PhoneBrandScreen - Vending Machine Session:', appState.vendingMachineSession)

  // Load brands and models on component mount
  useEffect(() => {
    loadBrandsAndModels()
  }, [])

  const loadBrandsAndModels = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('🔄 PhoneBrandScreen - Loading brands from Chinese API...')
      
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      
      // Fetch brands from Chinese API via our backend
      const brandsResponse = await fetch(`${API_BASE_URL}/api/brands?device_id=${deviceId || ''}`)
      
      if (!brandsResponse.ok) {
        throw new Error(`Failed to fetch brands: ${brandsResponse.status} ${brandsResponse.statusText}`)
      }
      
      const brandsResult = await brandsResponse.json()
      
      if (!brandsResult.success) {
        throw new Error(`Brands API error: ${brandsResult.detail || 'Unknown error'}`)
      }
      
      console.log('✅ PhoneBrandScreen - Brands loaded from Chinese API:', brandsResult.brands)
      setBrands(brandsResult.brands)
      
      // Pre-load models for available brands if device_id is available
      if (deviceId) {
        const modelsData = {}
        
        for (const brand of brandsResult.brands) {
          if (brand.available) {
            try {
              const modelsResponse = await fetch(`${API_BASE_URL}/api/brands/${brand.id}/models?device_id=${deviceId}`)
              if (modelsResponse.ok) {
                const modelsResult = await modelsResponse.json()
                if (modelsResult.success && modelsResult.models) {
                  modelsData[brand.id] = modelsResult.models
                  console.log(`✅ PhoneBrandScreen - Models loaded for ${brand.name}:`, modelsResult.models.length)
                }
              }
            } catch (error) {
              console.error(`❌ PhoneBrandScreen - Failed to load models for ${brand.name}:`, error)
            }
          }
        }
        
        setApiModels(modelsData)
      }
      
    } catch (error) {
      console.error('❌ PhoneBrandScreen - Failed to load brands from Chinese API:', error)
      setError(`Failed to load brands: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleBrandSelect = (brandId) => {
    const selectedBrandData = brands.find(b => b.id === brandId)
    if (selectedBrandData?.available) {
      if (!deviceId) {
        alert('Device ID is required for stock lookup. Please scan the QR code from a vending machine.')
        return
      }
      
      setSelectedBrand(brandId)
      setTimeout(() => {
        // Navigate to specific model screen based on brand with device_id
        const navigationState = { 
          apiModels: apiModels[brandId],
          deviceId: deviceId,
          chineseBrandId: selectedBrandData.chinese_brand_id
        }
        
        switch(brandId) {
          case 'iphone':
            navigate('/iphone-model', { state: navigationState })
            break
          case 'samsung':
            navigate('/samsung-model', { state: navigationState })
            break
          case 'google':
            navigate('/google-model', { state: navigationState })
            break
          default:
            navigate('/iphone-model', { state: navigationState })
        }
      }, 300)
    }
  }

  // Loading state
  if (loading) {
    return (
      <div 
        style={{ 
          minHeight: '100vh',
          background: '#f8f8f8',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          position: 'relative',
          overflow: 'hidden',
          fontFamily: 'Cubano, sans-serif'
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
          <h2 style={{ fontSize: '24px', margin: '0' }}>Loading Chinese API...</h2>
          {deviceId && <p style={{ fontSize: '14px', margin: '10px 0 0 0', opacity: 0.7 }}>Device: {deviceId}</p>}
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
  
  // Error state
  if (error) {
    return (
      <div 
        style={{ 
          minHeight: '100vh',
          background: '#f8f8f8',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          position: 'relative',
          overflow: 'hidden',
          fontFamily: 'Cubano, sans-serif'
        }}
      >
        <PastelBlobs />
        
        <div style={{ 
          position: 'relative', 
          zIndex: 10,
          textAlign: 'center',
          color: '#474746',
          maxWidth: '400px'
        }}>
          <h2 style={{ fontSize: '24px', margin: '0 0 20px 0', color: '#d32f2f' }}>Chinese API Error</h2>
          <p style={{ fontSize: '16px', margin: '0 0 20px 0' }}>{error}</p>
          {!deviceId && (
            <p style={{ fontSize: '14px', margin: '0', opacity: 0.7 }}>
              Please scan a QR code from a vending machine to access stock information.
            </p>
          )}
          <button 
            onClick={loadBrandsAndModels}
            style={{
              marginTop: '20px',
              padding: '12px 24px',
              backgroundColor: '#474746',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div 
      style={{ 
        minHeight: '100vh',
        background: '#f8f8f8',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'Cubano, sans-serif'
      }}
    >
      {/* Pastel Blobs Background */}
      <PastelBlobs />

      {/* Header Blob */}
      <div
        style={{
          position: 'relative',
          width: '380px',
          height: '140px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
          zIndex: 10
        }}
      >
        <img
          src="/blueblob.svg"
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
            fontSize: '40px',
            fontWeight: 'normal',
            color: '#474746',
            textAlign: 'center',
            width: '100%',
            margin: '0',
            padding: '0',
            lineHeight: '1.1',
            fontFamily: 'Cubano, sans-serif',
            position: 'relative',
            zIndex: 1
          }}
        >CHOOSE YOUR<br/>PHONE
        </h1>
      </div>

      {/* Phone option cards */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '32px', 
        width: '100%',
        maxWidth: '200px',
        marginBottom: '40px',
        position: 'relative',
        zIndex: 10
      }}>
        {brands.map((brand) => (
          <button
            key={brand.id}
            onClick={() => handleBrandSelect(brand.id)}
            disabled={!brand.available}
            style={{
              borderRadius: '28px',
              padding: '18px',
              cursor: brand.available ? 'pointer' : 'not-allowed',
              transition: 'transform 0.25s ease',
              position: 'relative',
              background: brand.frame_color || brand.frameColor,
              border: 'none',
              opacity: brand.available ? 1 : 0.6,
              minWidth: '210px'
            }}
            onMouseEnter={(e) => {
              if (brand.available) {
                e.currentTarget.style.transform = 'translateY(-6px)'
              }
            }}
            onMouseLeave={(e) => {
              if (brand.available) {
                e.currentTarget.style.transform = 'translateY(0px)'
              }
            }}
          >
            {/* Inner white section */}
            <div
              style={{
                background: '#ffffff',
                borderRadius: '18px',
                padding: '28px 24px 32px 28px',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                minHeight: '100px'
              }}
            >
              {/* Power button - top right */}
              <div
                style={{
                  width: '60px',
                  height: '36px',
                  borderRadius: '20px',
                  position: 'absolute',
                  top: '10px',
                  right: '16px',
                  background: brand.button_color || brand.buttonColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <div
                  style={{
                    width: '25px',
                    height: '10px',
                    background: '#ffffff',
                    borderRadius: '5px'
                  }}
                />
              </div>

              {/* Phone label - bottom left */}
              <div style={{ 
                position: 'absolute',
                bottom: '5px',
                left: '8px',
                display: 'flex', 
                flexDirection: 'column', 
                gap: brand.subtitle ? '0px' : '0' 
              }}>
                                  <span
                    style={{
                      fontSize: '22px',
                      fontWeight: 'normal',
                      color: brand.available ? '#2c3e50' : '#7f8c8d',
                      letterSpacing: '-1px',
                      fontFamily: 'Cubano, sans-serif'
                    }}
                  >
                    {brand.name}
                  </span>
                  {brand.subtitle && (
                    <span
                      style={{
                        fontSize: '11px',
                        color: '#7f8c8d',
                        fontWeight: '400',
                        fontFamily: 'Cubano, sans-serif',
                        marginTop: '-2px'
                      }}
                    >
                      {brand.subtitle}
                    </span>
                  )}
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Logo at bottom */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        position: 'relative',
        zIndex: 10
      }}>
        <img 
          src="/logo.png" 
          alt="Pimp My Case Logo" 
          style={{ height: '125px', width: 'auto' }} 
        />
      </div>

      {/* Load Cubano font */}
      <style>
        {`
          @font-face {
            font-family: 'Cubano';
            src: url('/fonts/Cubano.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
          }
        `}
      </style>
    </div>
  )
}

export default PhoneBrandScreen