import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PastelBlobs from '../components/PastelBlobs'
import aiImageService from '../services/aiImageService'

const PhoneBrandScreen = () => {
  const navigate = useNavigate()
  const [selectedBrand, setSelectedBrand] = useState('')
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)
  const [apiModels, setApiModels] = useState({})

  // Default brands with exact UI styling from previous version
  const defaultBrands = [
    { 
      id: 'iphone', 
      name: 'IPHONE', 
      frameColor: '#d7efd4',
      buttonColor: '#b9e4b4',
      available: true
    },
    { 
      id: 'samsung', 
      name: 'SAMSUNG', 
      frameColor: '#f9e1eb',
      buttonColor: '#f5bed3',
      available: true
    },
    { 
      id: 'google', 
      name: 'GOOGLE', 
      frameColor: '#d8ecf4',
      buttonColor: '#d8ecf4',
      available: false, // Google is coming soon
      subtitle: 'Coming Soon'
    }
  ]

  // Load brands and models on component mount
  useEffect(() => {
    loadBrandsAndModels()
  }, [])

  const loadBrandsAndModels = async () => {
    try {
      setLoading(true)
      console.log('🔄 PhoneBrandScreen - Loading brands and models from Chinese API...')
      
      // Always use the default brands for UI
      setBrands(defaultBrands)
      
      // Try to fetch models from Chinese API for each brand
      const modelsData = {}
      
      for (const brand of defaultBrands) {
        if (brand.available) {
          try {
            const response = await aiImageService.getPhoneModels(brand.id)
            if (response.success && response.models) {
              modelsData[brand.id] = response.models
              console.log(`✅ PhoneBrandScreen - Models loaded for ${brand.name}:`, response.models.length)
            }
          } catch (error) {
            console.error(`❌ PhoneBrandScreen - Failed to load models for ${brand.name}:`, error)
            // Will fall back to hardcoded models in individual screens
          }
        }
      }
      
      setApiModels(modelsData)
      console.log('✅ PhoneBrandScreen - All models loaded')
    } catch (error) {
      console.error('❌ PhoneBrandScreen - Failed to load brands:', error)
      // Use default brands anyway
      setBrands(defaultBrands)
    } finally {
      setLoading(false)
    }
  }

  const handleBrandSelect = (brandId) => {
    const selectedBrandData = brands.find(b => b.id === brandId)
    if (selectedBrandData?.available) {
      setSelectedBrand(brandId)
      setTimeout(() => {
        // Navigate to specific model screen based on brand
        switch(brandId) {
          case 'iphone':
            navigate('/iphone-model', {
              state: { apiModels: apiModels.iphone }
            })
            break
          case 'samsung':
            navigate('/samsung-model', {
              state: { apiModels: apiModels.samsung }
            })
            break
          case 'google':
            navigate('/google-model', {
              state: { apiModels: apiModels.google }
            })
            break
          default:
            navigate('/iphone-model')
        }
      }, 300)
    }
  }

  // Loading state - simplified version without API indicators
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
          <h2 style={{ fontSize: '24px', margin: '0' }}>Loading...</h2>
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
              background: brand.frameColor,
              border: 'none',
              opacity: brand.available ? 1 : 1,
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
                  background: brand.buttonColor,
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
                      color: '#2c3e50',
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