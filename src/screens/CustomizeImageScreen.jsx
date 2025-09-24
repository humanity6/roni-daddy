import { useRef, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

const CustomizeImageScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { selectedModelData, deviceId } = location.state || {}
  const { state: appState, actions } = useAppState()

  const fileInputRef = useRef(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleBack = () => {
    // Navigate back to the appropriate model screen based on the brand
    const brand = selectedModelData?.brand || 'iphone'
    switch(brand) {
      case 'iphone':
        navigate('/iphone-model', { state: { deviceId } })
        break
      case 'samsung':
        navigate('/samsung-model', { state: { deviceId } })
        break
      case 'google':
        navigate('/google-model', { state: { deviceId } })
        break
      default:
        navigate('/phone-brand')
    }
  }

  const handleUploadPhoto = () => {
    fileInputRef.current?.click()
  }

  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    if (file) {
      setIsLoading(true)

      try {
        const reader = new FileReader()

        const imageData = await new Promise((resolve, reject) => {
          reader.onload = (e) => resolve(e.target.result)
          reader.onerror = reject
          reader.readAsDataURL(file)
        })

        // Clear any existing uploaded images first (asynchronously)
        await new Promise((resolve) => {
          requestAnimationFrame(() => {
            const currentImageCount = appState.uploadedImages.length
            for (let i = 0; i < currentImageCount; i++) {
              actions.removeImage(0) // Always remove the first image
            }
            resolve()
          })
        })

        // Add image to centralized state
        actions.addImage(imageData)

        // Navigate to template selection
        navigate('/template-selection', {
          state: {
            selectedModelData,
            deviceId,
            imageMode: 'full-background',
            brand: selectedModelData?.brand,
            model: selectedModelData?.model
          }
        })
      } catch (error) {
        console.error('Error uploading image:', error)
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleBrowseDesigns = () => {
    // Navigate to browse designs screen
    navigate('/browse-designs', {
      state: {
        selectedModelData,
        deviceId,
        imageMode: 'full-background',
        brand: selectedModelData?.brand,
        model: selectedModelData?.model
      }
    })
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
        aria-label="Go back to model selection"
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
        Pick a background option
      </h1>

      {/* Primary Action Buttons */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px',
          maxWidth: '400px',
          width: '100%'
        }}
      >
        {/* Upload Photo Button */}
        <button
          onClick={handleUploadPhoto}
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '24px 32px',
            backgroundColor: isLoading ? '#F0F0F0' : '#FFFFFF',
            border: '2px solid #E5E5E5',
            borderRadius: '16px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            transition: 'all 200ms ease-out',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
            opacity: isLoading ? 0.7 : 1
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.target.style.borderColor = '#111111'
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.08)'
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading) {
              e.target.style.borderColor = '#E5E5E5'
              e.target.style.transform = 'translateY(0px)'
              e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.04)'
            }
          }}
          onFocus={(e) => {
            if (!isLoading) {
              e.target.style.outline = '2px solid #FF7CA3'
              e.target.style.outlineOffset = '4px'
            }
          }}
          onBlur={(e) => {
            e.target.style.outline = 'none'
            e.target.style.outlineOffset = '0'
          }}
          aria-label="Upload your own photo"
        >
          {/* Upload Icon or Loading Spinner */}
          {isLoading ? (
            <div
              style={{
                width: '32px',
                height: '32px',
                border: '3px solid #ccc',
                borderTop: '3px solid #FF7CA3',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}
            />
          ) : (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M7 10L12 5L17 10" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 5V15" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}

          {/* Button Text */}
          <span
            style={{
              fontSize: '18px',
              fontWeight: '500',
              color: isLoading ? '#666666' : '#111111',
              textAlign: 'center'
            }}
          >
            {isLoading ? 'Processing...' : 'Upload Photo'}
          </span>
        </button>

        {/* Browse Our Designs Button */}
        <button
          onClick={handleBrowseDesigns}
          style={{
            width: '100%',
            padding: '24px 32px',
            backgroundColor: '#FFFFFF',
            border: '2px solid #E5E5E5',
            borderRadius: '16px',
            cursor: 'pointer',
            transition: 'all 200ms ease-out',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
          }}
          onMouseEnter={(e) => {
            e.target.style.borderColor = '#111111'
            e.target.style.transform = 'translateY(-2px)'
            e.target.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.08)'
          }}
          onMouseLeave={(e) => {
            e.target.style.borderColor = '#E5E5E5'
            e.target.style.transform = 'translateY(0px)'
            e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.04)'
          }}
          onFocus={(e) => {
            e.target.style.outline = '2px solid #FF7CA3'
            e.target.style.outlineOffset = '4px'
          }}
          onBlur={(e) => {
            e.target.style.outline = 'none'
            e.target.style.outlineOffset = '0'
          }}
          aria-label="Browse our design templates"
        >
          {/* Button Text */}
          <span
            style={{
              fontSize: '18px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center'
            }}
          >
            Browse Our Designs
          </span>
        </button>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        style={{ display: 'none' }}
      />

      {/* Font Import and Animation */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default CustomizeImageScreen