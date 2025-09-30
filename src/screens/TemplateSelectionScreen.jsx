import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

const TemplateSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, selectedModelData, deviceId, imageMode } = location.state || {}
  const { state: appState, actions } = useAppState()

  const [selectedTemplate, setSelectedTemplate] = useState('')

  // Get uploaded image from centralized state
  const uploadedImage = appState.uploadedImages.length > 0 ? appState.uploadedImages[0] : null

  // Programme definitions matching the 5 options specified
  const programmes = [
    {
      id: 'classic',
      name: 'Classic',
      category: 'basic',
      description: 'Single image with background',
      imageCount: 1
    },
    {
      id: 'retro-remix',
      name: 'Retro Remix',
      category: 'ai',
      description: 'AI retro style enhancement',
      imageCount: 1
    },
    {
      id: 'film-strip',
      name: 'Film Strip',
      category: 'film',
      description: '3 in 1 Film Strip',
      imageCount: 3
    },
    {
      id: 'toonify',
      name: 'Toonify',
      category: 'ai',
      description: 'Cartoon conversion',
      imageCount: 1
    },
    {
      id: 'footy-fan',
      name: 'Footy Fan',
      category: 'ai',
      description: 'Football team themes',
      imageCount: 1
    }
  ]

  const handleBack = () => {
    navigate('/customize-image', {
      state: {
        selectedModelData,
        deviceId
      }
    })
  }

  const handleProgrammeSelect = (programmeId) => {
    const programme = programmes.find(p => p.id === programmeId)
    setSelectedTemplate(programmeId)

    // Store template in centralized state
    actions.setTemplate(programme)

    // Prepare common state data (without uploadedImage since it's in centralized state)
    const commonState = {
      brand,
      model,
      color,
      template: programme,
      selectedModelData,
      deviceId,
      imageMode
    }

    // Navigate directly to main template screens
    if (programme.id === 'classic') {
      // Classic goes to phone preview (main classic interface)
      navigate('/phone-preview', {
        state: commonState
      })
    } else if (programme.id === 'retro-remix') {
      // Retro Remix goes to main retro remix screen
      navigate('/retro-remix', {
        state: commonState
      })
    } else if (programme.id === 'film-strip') {
      // Film Strip goes to main film strip screen
      // Images already in centralized state, but add film strip specific state
      const filmStripState = {
        ...commonState,
        imageTransforms: uploadedImage ? [{ x: 0, y: 0, scale: 2 }] : [],
        imageOrientations: uploadedImage ? ['portrait'] : []
      }
      navigate('/film-strip', {
        state: filmStripState
      })
    } else if (programme.id === 'toonify') {
      // Toonify goes to main funny toon screen
      navigate('/funny-toon', {
        state: {
          ...commonState,
          template: { ...programme, id: 'funny-toon' } // Map to existing funny-toon
        }
      })
    } else if (programme.id === 'footy-fan') {
      // Footy Fan goes to phone preview (placeholder until dedicated screen exists)
      navigate('/phone-preview', {
        state: commonState
      })
    }
  }

  // Get the appropriate SVG for the phone mockup
  const getPhoneSvg = () => {
    const brandName = selectedModelData?.brand || brand || 'iphone'
    switch(brandName) {
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
        aria-label="Go back to background options"
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
          margin: '0 0 40px 0',
          lineHeight: '1.1',
          fontFamily: '"GT Walsheim", "Proxima Nova", "Avenir Next", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
          letterSpacing: '-0.02em'
        }}
      >
        Choose Programme
      </h1>

      {/* Phone Mockup with Uploaded Image */}
      <div
        style={{
          position: 'relative',
          width: '180px',
          height: '360px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '40px'
        }}
      >
        {/* Phone outline */}
        <img
          src={getPhoneSvg()}
          alt="Phone mockup"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            filter: 'brightness(0) saturate(100%) invert(20%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)',
            position: 'absolute',
            zIndex: 2
          }}
        />

        {/* Image preview area */}
        <div
          style={{
            position: 'absolute',
            width: '85%',
            height: '85%',
            backgroundColor: uploadedImage ? 'transparent' : '#F5F5F5',
            borderRadius: '25px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            zIndex: 1,
            border: uploadedImage ? 'none' : '2px dashed #CCCCCC'
          }}
        >
          {uploadedImage ? (
            <img
              src={uploadedImage}
              alt="Uploaded preview"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                borderRadius: '25px'
              }}
            />
          ) : (
            <div
              style={{
                textAlign: 'center',
                color: '#999999',
                fontSize: '12px',
                fontWeight: '400'
              }}
            >
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>📱</div>
              <div>Preview</div>
            </div>
          )}
        </div>
      </div>

      {/* Programme Options Grid */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px',
          maxWidth: '400px',
          width: '100%'
        }}
      >
        {/* Row 1: Classic, Retro Remix */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            width: '100%'
          }}
        >
          <button
            onClick={() => handleProgrammeSelect('classic')}
            style={{
              padding: '20px 24px',
              backgroundColor: '#FFFFFF',
              border: '2px solid #E5E5E5',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center',
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
          >
            Classic
          </button>

          <button
            onClick={() => handleProgrammeSelect('retro-remix')}
            style={{
              padding: '20px 24px',
              backgroundColor: '#FFFFFF',
              border: '2px solid #E5E5E5',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center',
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
          >
            Retro Remix
          </button>
        </div>

        {/* Row 2: Film Strip, Toonify */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            width: '100%'
          }}
        >
          <button
            onClick={() => handleProgrammeSelect('film-strip')}
            style={{
              padding: '20px 24px',
              backgroundColor: '#FFFFFF',
              border: '2px solid #E5E5E5',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center',
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
          >
            Film Strip
          </button>

          <button
            onClick={() => handleProgrammeSelect('toonify')}
            style={{
              padding: '20px 24px',
              backgroundColor: '#FFFFFF',
              border: '2px solid #E5E5E5',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center',
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
          >
            Toonify
          </button>
        </div>

        {/* Row 3: Footy Fan (centered) */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%'
          }}
        >
          <button
            onClick={() => handleProgrammeSelect('footy-fan')}
            style={{
              padding: '20px 24px',
              backgroundColor: '#FFFFFF',
              border: '2px solid #E5E5E5',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#111111',
              textAlign: 'center',
              fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
              width: 'calc(50% - 8px)' // Same width as buttons above
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
          >
            Footy Fan
          </button>
        </div>
      </div>

      {/* Font Import */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');
      `}</style>
    </div>
  )
}

export default TemplateSelectionScreen