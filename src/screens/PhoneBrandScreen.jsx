import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

// Device illustration components using back-view SVGs
const DeviceIllustration = ({ deviceType, isHovered, isSelected }) => {
  const getSvgPath = (type) => {
    switch (type) {
      case 'iphone':
        return '/iphone-back-dual.svg'
      case 'samsung':
        return '/samsung-back(1).svg'
      case 'google':
        return '/google-back(1).svg'
      default:
        return '/iphone-back-dual.svg'
    }
  }

  const svgPath = getSvgPath(deviceType)

  return (
    <div
      style={{
        width: '120px',
        height: '240px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
        transform: isHovered
          ? 'scale(1.05) translateY(-4px)'
          : isSelected
            ? 'scale(1.02) translateY(-2px)'
            : 'scale(1)',
        filter: isSelected
          ? 'drop-shadow(0 8px 24px rgba(0, 0, 0, 0.2))'
          : isHovered
            ? 'drop-shadow(0 4px 16px rgba(0, 0, 0, 0.15))'
            : 'drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1))',
        color: '#666666'
      }}
    >
      <img
        src={svgPath}
        alt={`${deviceType} device back view`}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          filter: 'brightness(0) saturate(100%) invert(40%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)'
        }}
      />

    </div>
  )
}

// Option Card Component - Now without boxes, just hover-responsive SVGs
const OptionCard = ({ brand, isSelected, onSelect, disabled }) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isPressed, setIsPressed] = useState(false)

  const baseStyle = {
    width: '100%',
    minHeight: '280px',
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '0',
    padding: '24px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 150ms ease-out',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '24px',
    fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
    boxShadow: 'none',
    transform: isPressed
      ? 'translateY(2px)'
      : 'translateY(0px)',
    opacity: disabled ? 0.6 : 1,
    outline: 'none',
    position: 'relative'
  }

  const textColor = disabled ? '#999999' : '#111111'

  return (
    <button
      style={baseStyle}
      onMouseEnter={() => !disabled && setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false)
        setIsPressed(false)
      }}
      onMouseDown={() => !disabled && setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onFocus={(e) => {
        e.target.style.outline = '2px solid #FF7CA3'
        e.target.style.outlineOffset = '4px'
      }}
      onBlur={(e) => {
        e.target.style.outline = 'none'
        e.target.style.outlineOffset = '0'
      }}
      onClick={() => !disabled && onSelect(brand.id)}
      disabled={disabled}
      role="radio"
      aria-checked={isSelected}
      aria-label={`Select ${brand.name} device`}
    >
      {/* Device illustration */}
      <DeviceIllustration
        deviceType={brand.id === 'iphone' ? 'iphone' : brand.id === 'samsung' ? 'samsung' : brand.id === 'google' ? 'google' : 'iphone'}
        isHovered={isHovered}
        isSelected={isSelected}
      />

      {/* Device name */}
      <span style={{
        fontSize: '18px',
        fontWeight: '600',
        color: textColor,
        textAlign: 'center',
        lineHeight: '1.2',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}>
        {brand.name}
      </span>

      {/* Availability indicator */}
      {!brand.available && (
        <span style={{
          fontSize: '14px',
          fontWeight: '400',
          color: '#999999',
          textAlign: 'center',
          fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
        }}>
          Not Available
        </span>
      )}
    </button>
  )
}

const PhoneBrandScreen = () => {
  const navigate = useNavigate()
  const { state: appState, actions } = useAppState()
  const [selectedBrand, setSelectedBrand] = useState('')
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)
  const [apiModels, setApiModels] = useState({})
  const [error, setError] = useState(null)
  const loadingRef = useRef(false) // Prevent multiple simultaneous API calls
  const lastDeviceIdRef = useRef(null) // Track last processed device ID

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

  // Memoized function to prevent unnecessary re-renders
  const loadBrandsAndModels = useCallback(async () => {
    // Prevent multiple simultaneous API calls
    if (loadingRef.current) {
      console.log('🚫 PhoneBrandScreen - Skipping API call, already loading')
      return
    }

    // Check session-level cache first
    const cache = appState.brandsCache
    if (cache.loaded && cache.deviceId === deviceId && cache.brands.length > 0) {
      // Cache hit - use cached data
      console.log('🎯 PhoneBrandScreen - Using session cache for deviceId:', deviceId)
      setBrands(cache.brands)
      setApiModels(cache.apiModels || {})
      setLoading(false)
      setError(null)
      lastDeviceIdRef.current = deviceId
      return
    }

    // Skip if we already loaded for this deviceId (fallback check)
    if (lastDeviceIdRef.current === deviceId && brands.length > 0) {
      console.log('📋 PhoneBrandScreen - Using local cached brands for deviceId:', deviceId)
      return
    }
    try {
      loadingRef.current = true
      setLoading(true)
      setError(null)
      console.log('🔄 PhoneBrandScreen - Loading brands from Chinese API for deviceId:', deviceId)
      
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
      lastDeviceIdRef.current = deviceId // Store the deviceId we loaded for
      
      // Pre-load models for available brands if device_id is available
      const modelsData = {}
      if (deviceId) {
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
      }
      
      setApiModels(modelsData)
      
      // Cache the data in session-level state
      actions.setBrandsCache(brandsResult.brands, modelsData, deviceId)
      console.log('💾 PhoneBrandScreen - Brands and models cached for session')
      
    } catch (error) {
      console.error('❌ PhoneBrandScreen - Failed to load brands from Chinese API:', error)
      setError(`Failed to load brands: ${error.message}`)
    } finally {
      loadingRef.current = false
      setLoading(false)
    }
  }, [deviceId, brands.length, appState.brandsCache, actions]) // Include cache dependencies

  // Load brands and models on component mount with optimized dependencies
  useEffect(() => {
    loadBrandsAndModels()
  }, [loadBrandsAndModels])

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
          chineseBrandId: selectedBrandData.chinese_brand_id,
          brandData: selectedBrandData // Pass complete brand data for dynamic rendering
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
          backgroundColor: '#FFFFFF',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
        }}
      >
        <div style={{
          textAlign: 'center',
          color: '#111111'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #E5E5E5',
            borderTop: '4px solid #FF7CA3',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 32px'
          }}></div>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            margin: '0 0 16px 0',
            color: '#111111'
          }}>
            Loading Devices
          </h2>
          {deviceId && (
            <p style={{
              fontSize: '16px',
              margin: '0',
              opacity: 0.7,
              fontWeight: '400'
            }}>
              Device: {deviceId}
            </p>
          )}
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
          backgroundColor: '#FFFFFF',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
        }}
      >
        <div style={{
          textAlign: 'center',
          maxWidth: '480px',
          color: '#111111'
        }}>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '700',
            margin: '0 0 24px 0',
            color: '#EB5757'
          }}>
            Connection Error
          </h2>
          <p style={{
            fontSize: '16px',
            fontWeight: '400',
            margin: '0 0 24px 0',
            lineHeight: '1.5',
            color: '#666666'
          }}>
            {error}
          </p>
          {!deviceId && (
            <p style={{
              fontSize: '14px',
              margin: '0 0 32px 0',
              opacity: 0.7,
              fontWeight: '400'
            }}>
              Please scan a QR code from a vending machine to access device information.
            </p>
          )}
          <button
            onClick={loadBrandsAndModels}
            style={{
              padding: '16px 32px',
              backgroundColor: '#FF7CA3',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              transition: 'all 150ms ease-out',
              boxShadow: '0 4px 12px rgba(255, 124, 163, 0.24)'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#FF69A0'
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 6px 16px rgba(255, 124, 163, 0.32)'
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#FF7CA3'
              e.target.style.transform = 'translateY(0px)'
              e.target.style.boxShadow = '0 4px 12px rgba(255, 124, 163, 0.24)'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#FFFFFF',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}
    >
      {/* Header */}
      <h1
        style={{
          fontSize: '36px',
          fontWeight: '800',
          color: '#111111',
          textAlign: 'center',
          margin: '0 0 56px 0',
          lineHeight: '1.1',
          fontFamily: '"GT Walsheim", "Proxima Nova", "Avenir Next", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
          letterSpacing: '-0.02em'
        }}
      >
        Select Your Device
      </h1>

      {/* Option Stack */}
      <div
        role="radiogroup"
        aria-label="Device selection"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          width: '100%',
          maxWidth: '320px',
          marginBottom: '48px'
        }}
        aria-live="polite"
      >
        {brands.map((brand) => (
          <OptionCard
            key={brand.id}
            brand={brand}
            isSelected={selectedBrand === brand.id}
            onSelect={handleBrandSelect}
            disabled={!brand.available}
          />
        ))}
      </div>

      {/* Load IBM Plex Mono font and animations */}
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');

          @keyframes pulse-glow {
            0%, 100% {
              opacity: 0.3;
              transform: scale(1);
            }
            50% {
              opacity: 0.6;
              transform: scale(1.05);
            }
          }
        `}
      </style>
    </div>
  )
}

export default PhoneBrandScreen