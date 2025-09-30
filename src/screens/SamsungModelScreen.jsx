import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

// Device illustration component using same back-view SVG from brand screen
const ModelIllustration = ({ isHovered, isSelected }) => {
  return (
    <div
      style={{
        width: '80px',
        height: '160px',
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
        src="/samsung-back(1).svg"
        alt="Samsung model back view"
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

// Model Card Component for horizontal sliding
const ModelCard = ({ model, isSelected, onSelect, disabled }) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isPressed, setIsPressed] = useState(false)

  const modelName = model.mobile_model_name || model.name || model.display_name || 'Unknown Model'
  const modelStock = typeof model === 'object' ? model.stock : null

  const baseStyle = {
    minWidth: '200px',
    width: '200px',
    height: '280px',
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
    gap: '16px',
    fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
    boxShadow: 'none',
    transform: isPressed
      ? 'translateY(2px)'
      : 'translateY(0px)',
    opacity: disabled ? 0.6 : 1,
    outline: 'none',
    position: 'relative',
    scrollSnapAlign: 'start',
    flexShrink: 0
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
      onClick={() => !disabled && onSelect(model)}
      disabled={disabled}
      role="radio"
      aria-checked={isSelected}
      aria-label={`Select ${modelName}`}
    >
      {/* Model illustration */}
      <ModelIllustration
        isHovered={isHovered}
        isSelected={isSelected}
      />

      {/* Model name */}
      <span style={{
        fontSize: '16px',
        fontWeight: '600',
        color: textColor,
        textAlign: 'center',
        lineHeight: '1.2',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
        wordBreak: 'break-word'
      }}>
        {modelName}
      </span>

      {/* Availability indicator */}
      {modelStock === 0 && (
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

const SamsungModelScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { actions } = useAppState()
  const [selectedModel, setSelectedModel] = useState('')
  const [samsungModels, setSamsungModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const scrollContainerRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [startX, setStartX] = useState(0)
  const [scrollLeft, setScrollLeft] = useState(0)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)
  const [isScrolling, setIsScrolling] = useState(false)

  // Get parameters from navigation state
  const { deviceId, chineseBrandId, apiModels, brandData } = location.state || {}

  // Extract brand information from Chinese API data or fallback
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
        setSelectedModel(apiModels[0])
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
        setSelectedModel(result.available_items[0])
      }
    } catch (error) {
      console.error('❌ SamsungModelScreen - Error loading models:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleModelSelect = (model) => {
    setSelectedModel(model)
  }

  // Update scroll button visibility
  const updateScrollButtons = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1)
    }
  }

  // Enhanced scroll functions with better animation
  const scrollLeftFn = () => {
    if (scrollContainerRef.current && !isScrolling) {
      setIsScrolling(true)
      const cardWidth = 224 // 200px width + 24px gap
      const container = scrollContainerRef.current
      const currentScroll = container.scrollLeft
      const targetScroll = Math.max(0, currentScroll - cardWidth)

      container.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      })

      // Reset scrolling flag after animation
      setTimeout(() => {
        setIsScrolling(false)
        updateScrollButtons()
      }, 300)
    }
  }

  const scrollRightFn = () => {
    if (scrollContainerRef.current && !isScrolling) {
      setIsScrolling(true)
      const cardWidth = 224 // 200px width + 24px gap
      const container = scrollContainerRef.current
      const currentScroll = container.scrollLeft
      const maxScroll = container.scrollWidth - container.clientWidth
      const targetScroll = Math.min(maxScroll, currentScroll + cardWidth)

      container.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      })

      // Reset scrolling flag after animation
      setTimeout(() => {
        setIsScrolling(false)
        updateScrollButtons()
      }, 300)
    }
  }

  // Handle scroll events to update button visibility
  const handleScroll = () => {
    if (!isDragging) {
      updateScrollButtons()
    }
  }

  // Enhanced touch/swipe handlers with momentum
  const handleTouchStart = (e) => {
    setIsDragging(true)
    setStartX(e.touches[0].clientX - scrollContainerRef.current.offsetLeft)
    setScrollLeft(scrollContainerRef.current.scrollLeft)
  }

  const handleTouchMove = (e) => {
    if (!isDragging) return
    e.preventDefault()
    const x = e.touches[0].clientX - scrollContainerRef.current.offsetLeft
    const walk = (x - startX) * 1.5 // Reduced multiplier for smoother feel
    scrollContainerRef.current.scrollLeft = scrollLeft - walk
  }

  const handleTouchEnd = () => {
    setIsDragging(false)
    setTimeout(updateScrollButtons, 100)
  }

  // Enhanced mouse drag handlers for desktop
  const handleMouseDown = (e) => {
    setIsDragging(true)
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft)
    setScrollLeft(scrollContainerRef.current.scrollLeft)
    e.preventDefault() // Prevent text selection
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    e.preventDefault()
    const x = e.pageX - scrollContainerRef.current.offsetLeft
    const walk = (x - startX) * 1.5 // Reduced multiplier for smoother feel
    scrollContainerRef.current.scrollLeft = scrollLeft - walk
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setTimeout(updateScrollButtons, 100)
  }

  const handleMouseLeave = () => {
    setIsDragging(false)
    setTimeout(updateScrollButtons, 100)
  }

  // Initialize scroll buttons on component mount and model load
  useEffect(() => {
    if (samsungModels.length > 0) {
      setTimeout(updateScrollButtons, 100)
    }
  }, [samsungModels])

  const handleSubmit = () => {
    if (!selectedModel) {
      alert('Please select a model')
      return
    }
    
    // Pass Chinese model data to app state including dimensions
    const selectedModelData = {
      brand: brandData?.name?.toLowerCase() || brandData?.display_name?.toLowerCase() || 'samsung',
      model: selectedModel.mobile_model_name || selectedModel.name || selectedModel.display_name,
      chinese_model_id: selectedModel.mobile_model_id || selectedModel.chinese_model_id || selectedModel.id,
      price: selectedModel.price,
      stock: selectedModel.stock,
      device_id: deviceId,
      // Chinese API dimensions in millimeters
      width: selectedModel.width ? parseFloat(selectedModel.width) : null,
      height: selectedModel.height ? parseFloat(selectedModel.height) : null,
      mobile_shell_id: selectedModel.mobile_shell_id
    }
    
    console.log('SamsungModelScreen - Selected model data:', selectedModelData)
    
    actions.setPhoneSelection(selectedModelData.brand, selectedModelData.model, selectedModelData)
    navigate('/customize-image', {
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
            Loading {brandDisplayName} Models
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
            {brandDisplayName} Models Error
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
            onClick={loadModels}
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
              boxShadow: '0 4px 12px rgba(255, 124, 163, 0.24)',
              marginRight: '12px'
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
          <button
            onClick={handleBack}
            style={{
              padding: '16px 32px',
              backgroundColor: 'transparent',
              color: '#111111',
              border: '2px solid #E5E5E5',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              transition: 'all 150ms ease-out'
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = '#111111'
              e.target.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = '#E5E5E5'
              e.target.style.transform = 'translateY(0px)'
            }}
          >
            Go Back
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
        padding: '40px 20px',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}
    >
      {/* Back Arrow */}
      <button
        onClick={handleBack}
        style={{
          position: 'absolute',
          top: '40px',
          left: '40px',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: '#FFFFFF',
          border: '2px solid #E5E5E5',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 20,
          transition: 'all 150ms ease-out',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}
        onMouseEnter={(e) => {
          e.target.style.borderColor = '#111111'
          e.target.style.transform = 'scale(1.05)'
        }}
        onMouseLeave={(e) => {
          e.target.style.borderColor = '#E5E5E5'
          e.target.style.transform = 'scale(1)'
        }}
        onFocus={(e) => {
          e.target.style.outline = '2px solid #FF7CA3'
          e.target.style.outlineOffset = '4px'
        }}
        onBlur={(e) => {
          e.target.style.outline = 'none'
          e.target.style.outlineOffset = '0'
        }}
        aria-label="Go back to phone brands"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

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
        Select {brandDisplayName} Model
      </h1>

      {/* Horizontal Model Slider */}
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '800px',
        marginBottom: '48px'
      }}>
        {/* Left scroll button */}
        <button
          onClick={scrollLeftFn}
          disabled={!canScrollLeft || isScrolling}
          style={{
            position: 'absolute',
            left: '-16px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: '#FFFFFF',
            border: '2px solid #E5E5E5',
            cursor: (canScrollLeft && !isScrolling) ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10,
            transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: canScrollLeft ? '0 2px 8px rgba(0, 0, 0, 0.1)' : '0 1px 4px rgba(0, 0, 0, 0.05)',
            opacity: canScrollLeft ? 1 : 0.4,
            scale: isScrolling ? 0.95 : 1
          }}
          onMouseEnter={(e) => {
            if (canScrollLeft && !isScrolling) {
              e.target.style.borderColor = '#111111'
              e.target.style.transform = 'translateY(-50%) scale(1.05)'
              e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)'
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E5'
            e.target.style.transform = 'translateY(-50%) scale(1)'
            e.target.style.boxShadow = canScrollLeft ? '0 2px 8px rgba(0, 0, 0, 0.1)' : '0 1px 4px rgba(0, 0, 0, 0.05)'
          }}
          aria-label="Scroll models left"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 18L9 12L15 6" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        {/* Right scroll button */}
        <button
          onClick={scrollRightFn}
          disabled={!canScrollRight || isScrolling}
          style={{
            position: 'absolute',
            right: '-16px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: '#FFFFFF',
            border: '2px solid #E5E5E5',
            cursor: (canScrollRight && !isScrolling) ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10,
            transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: canScrollRight ? '0 2px 8px rgba(0, 0, 0, 0.1)' : '0 1px 4px rgba(0, 0, 0, 0.05)',
            opacity: canScrollRight ? 1 : 0.4,
            scale: isScrolling ? 0.95 : 1
          }}
          onMouseEnter={(e) => {
            if (canScrollRight && !isScrolling) {
              e.target.style.borderColor = '#111111'
              e.target.style.transform = 'translateY(-50%) scale(1.05)'
              e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)'
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E5'
            e.target.style.transform = 'translateY(-50%) scale(1)'
            e.target.style.boxShadow = canScrollRight ? '0 2px 8px rgba(0, 0, 0, 0.1)' : '0 1px 4px rgba(0, 0, 0, 0.05)'
          }}
          aria-label="Scroll models right"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 18L15 12L9 6" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        {/* Horizontal scrolling container */}
        <div
          ref={scrollContainerRef}
          role="radiogroup"
          aria-label={`${brandDisplayName} model selection`}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
          onScroll={handleScroll}
          style={{
            display: 'flex',
            gap: '24px',
            overflowX: 'auto',
            scrollBehavior: isDragging ? 'auto' : 'smooth',
            padding: '16px 0',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            WebkitScrollbar: 'none',
            cursor: isDragging ? 'grabbing' : 'grab',
            userSelect: 'none',
            scrollSnapType: 'x proximity'
          }}
        >
          {samsungModels.map((model, index) => {
            const modelName = model.mobile_model_name || model.name || model.display_name || 'Unknown Model'
            const isSelected = selectedModel === model
            const isDisabled = typeof model === 'object' && model.stock === 0

            return (
              <ModelCard
                key={`${modelName}-${index}`}
                model={model}
                isSelected={isSelected}
                onSelect={handleModelSelect}
                disabled={isDisabled}
              />
            )
          })}
        </div>
      </div>

      {/* Submit Button */}
      {selectedModel && (
        <button
          onClick={handleSubmit}
          style={{
            padding: '16px 48px',
            backgroundColor: '#FF7CA3',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '18px',
            fontWeight: '600',
            transition: 'all 150ms ease-out',
            boxShadow: '0 4px 12px rgba(255, 124, 163, 0.24)',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
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
          onFocus={(e) => {
            e.target.style.outline = '2px solid #FF7CA3'
            e.target.style.outlineOffset = '4px'
          }}
          onBlur={(e) => {
            e.target.style.outline = 'none'
            e.target.style.outlineOffset = '0'
          }}
          aria-label="Continue with selected model"
        >
          Continue
        </button>
      )}

      {/* Hide scrollbar with CSS */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');

        div::-webkit-scrollbar {
          display: none;
        }

        div {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  )
}

export default SamsungModelScreen 