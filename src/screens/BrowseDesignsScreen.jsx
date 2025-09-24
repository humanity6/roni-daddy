import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'

const BrowseDesignsScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { selectedModelData, deviceId, imageMode, brand, model } = location.state || {}
  const { state: appState, actions } = useAppState()

  const [selectedDesign, setSelectedDesign] = useState(null)
  const [isLoading, setIsLoading] = useState(false)


  const handleBack = () => {
    navigate('/customize-image', {
      state: {
        selectedModelData,
        deviceId
      }
    })
  }

  const handleDesignSelect = async (design) => {
    console.log('🚀 FUNCTION START - handleDesignSelect for design:', design.id)

    console.log('📝 Setting selectedDesign state...')
    setSelectedDesign(design)

    console.log('⏳ Setting isLoading to true...')
    setIsLoading(true)

    console.log('💾 Current uploadedImages count:', appState.uploadedImages.length)

    try {
      console.log('🧹 Starting image clearing process...')
      // Clear any existing uploaded images first (asynchronously)
      await new Promise((resolve) => {
        console.log('🎯 Inside requestAnimationFrame for clearing...')
        requestAnimationFrame(() => {
          console.log('🔄 Starting image clearing...')
          const currentImageCount = appState.uploadedImages.length
          console.log(`🗑️ Need to clear ${currentImageCount} images`)

          // Clear all images at once using a for loop with the initial count
          for (let i = 0; i < currentImageCount; i++) {
            actions.removeImage(0) // Always remove the first image
            console.log(`🗑️ Removed image ${i + 1}/${currentImageCount}`)
          }

          console.log('✅ Images cleared, total removed:', currentImageCount)
          resolve()
        })
      })

      console.log('🎨 Creating simple design image...')
      // Skip canvas entirely - use a simple placeholder SVG data URL
      const designImageData = await new Promise((resolve) => {
        console.log('🎯 Inside requestAnimationFrame for SVG creation...')
        requestAnimationFrame(() => {
          console.log('🎨 Creating SVG data...')
          const hue = (design.id * 60) % 360
          const svgData = `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" fill="hsl(${hue}, 70%, 50%)"/>
            <text x="100" y="110" font-family="Arial" font-size="40" fill="white" text-anchor="middle">${design.preview}</text>
          </svg>`
          console.log('🔗 Converting to data URL using URL encoding...')
          const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgData)}`
          console.log('✅ SVG created successfully')
          resolve(dataUrl)
        })
      })

      console.log('💾 Adding image to centralized state...')
      actions.addImage(designImageData)
      console.log('✅ Image added to state')

      console.log('🧭 Preparing navigation state...')
      const navigationState = {
        selectedModelData,
        deviceId,
        imageMode,
        brand,
        model
      }
      console.log('🧭 Navigation state:', navigationState)

      console.log('➡️ Navigating to add stickers...')
      navigate('/add-stickers', { state: navigationState })
      console.log('✅ Navigation initiated')

    } catch (error) {
      console.error('❌ ERROR in handleDesignSelect:', error)
      console.log('🚨 Attempting fallback navigation...')
      // Navigate without image if generation fails
      navigate('/add-stickers', {
        state: {
          selectedModelData,
          deviceId,
          imageMode,
          brand,
          model
        }
      })
    } finally {
      console.log('🏁 FINALLY BLOCK - Setting loading to false')
      setIsLoading(false)
      console.log('🏁 FUNCTION END - handleDesignSelect completed')
    }
  }

  // Design packs data
  const designPacks = [
    {
      name: "Monochrome Pack",
      designs: [
        { id: 1, preview: "⚫" },
        { id: 2, preview: "⚪" },
        { id: 3, preview: "◼️" },
        { id: 4, preview: "◻️" },
        { id: 5, preview: "▪️" }
      ]
    },
    {
      name: "Streetwear Pack",
      designs: [
        { id: 6, preview: "👟" },
        { id: 7, preview: "🧢" },
        { id: 8, preview: "🎽" },
        { id: 9, preview: "🥾" },
        { id: 10, preview: "👕" }
      ]
    },
    {
      name: "Festival Pack",
      designs: [
        { id: 11, preview: "🎪" },
        { id: 12, preview: "🎭" },
        { id: 13, preview: "🎨" },
        { id: 14, preview: "🎊" },
        { id: 15, preview: "🎈" }
      ]
    },
    {
      name: "Graffiti Pack",
      designs: [
        { id: 16, preview: "🖌️" },
        { id: 17, preview: "🎨" },
        { id: 18, preview: "✍️" },
        { id: 19, preview: "🏢" },
        { id: 20, preview: "🌈" }
      ]
    },
    {
      name: "Sports Pack",
      designs: [
        { id: 21, preview: "⚽" },
        { id: 22, preview: "🏀" },
        { id: 23, preview: "🏈" },
        { id: 24, preview: "⚾" },
        { id: 25, preview: "🎾" }
      ]
    },
    {
      name: "Retro Pack",
      designs: [
        { id: 26, preview: "📼" },
        { id: 27, preview: "📺" },
        { id: 28, preview: "🕹️" },
        { id: 29, preview: "💾" },
        { id: 30, preview: "📻" }
      ]
    },
    {
      name: "Space Pack",
      designs: [
        { id: 31, preview: "🚀" },
        { id: 32, preview: "🌌" },
        { id: 33, preview: "👨‍🚀" },
        { id: 34, preview: "🛸" },
        { id: 35, preview: "🌙" }
      ]
    },
    {
      name: "Animal Print Pack",
      designs: [
        { id: 36, preview: "🐆" },
        { id: 37, preview: "🦓" },
        { id: 38, preview: "🐅" },
        { id: 39, preview: "🦒" },
        { id: 40, preview: "🐍" }
      ]
    },
    {
      name: "Neon Cyber Pack",
      designs: [
        { id: 41, preview: "🔵" },
        { id: 42, preview: "🟢" },
        { id: 43, preview: "🟣" },
        { id: 44, preview: "🔴" },
        { id: 45, preview: "🟡" }
      ]
    },
    {
      name: "Skulls Pack",
      designs: [
        { id: 46, preview: "💀" },
        { id: 47, preview: "☠️" },
        { id: 48, preview: "🖤" },
        { id: 49, preview: "⚰️" },
        { id: 50, preview: "🦴" }
      ]
    },
    {
      name: "Rock Pack",
      designs: [
        { id: 51, preview: "🎸" },
        { id: 52, preview: "🥁" },
        { id: 53, preview: "🎤" },
        { id: 54, preview: "🤘" },
        { id: 55, preview: "⚡" }
      ]
    },
    {
      name: "Hip Hop Pack",
      designs: [
        { id: 56, preview: "🎵" },
        { id: 57, preview: "🎶" },
        { id: 58, preview: "🎧" },
        { id: 59, preview: "🔊" },
        { id: 60, preview: "💿" }
      ]
    },
    {
      name: "Floral Pack",
      designs: [
        { id: 61, preview: "🌸" },
        { id: 62, preview: "🌺" },
        { id: 63, preview: "🌼" },
        { id: 64, preview: "🌻" },
        { id: 65, preview: "🌷" }
      ]
    },
    {
      name: "Teddy Bears Pack",
      designs: [
        { id: 66, preview: "🧸" },
        { id: 67, preview: "🐻" },
        { id: 68, preview: "❤️" },
        { id: 69, preview: "🎀" },
        { id: 70, preview: "💝" }
      ]
    },
    {
      name: "Dark Energy Pack",
      designs: [
        { id: 71, preview: "🌑" },
        { id: 72, preview: "⚫" },
        { id: 73, preview: "🔮" },
        { id: 74, preview: "⚡" },
        { id: 75, preview: "🌪️" }
      ]
    },
    {
      name: "Black Matte Pack",
      designs: [
        { id: 76, preview: "⬛" },
        { id: 77, preview: "◼️" },
        { id: 78, preview: "▪️" },
        { id: 79, preview: "⚫" },
        { id: 80, preview: "🖤" }
      ]
    },
    {
      name: "Text Luxe Pack",
      designs: [
        { id: 81, preview: "💎" },
        { id: 82, preview: "✨" },
        { id: 83, preview: "🔸" },
        { id: 84, preview: "💫" },
        { id: 85, preview: "⭐" }
      ]
    },
    {
      name: "Shake Pack",
      designs: [
        { id: 86, preview: "🌊" },
        { id: 87, preview: "💨" },
        { id: 88, preview: "🌀" },
        { id: 89, preview: "💫" },
        { id: 90, preview: "⚡" }
      ]
    }
  ]

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#FFFFFF',
        padding: '20px',
        fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
      }}
    >
      {/* Back Arrow */}
      <button
        onClick={handleBack}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
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
        aria-label="Go back to background options"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="#111111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Header */}
      <div style={{ marginTop: '80px', marginBottom: '40px' }}>
        <h1
          style={{
            fontSize: '36px',
            fontWeight: '800',
            color: '#111111',
            textAlign: 'center',
            margin: '0 0 20px 0',
            lineHeight: '1.1',
            fontFamily: '"GT Walsheim", "Proxima Nova", "Avenir Next", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
            letterSpacing: '-0.02em'
          }}
        >
          Browse Our Designs
        </h1>
        <p
          style={{
            fontSize: '16px',
            color: '#666666',
            textAlign: 'center',
            margin: '0',
            maxWidth: '400px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}
        >
          Choose from our curated collection of design packs
        </p>
      </div>

      {/* Design Packs */}
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        {designPacks.map((pack, packIndex) => (
          <div key={packIndex} style={{ marginBottom: '40px' }}>
            {/* Pack Name */}
            <h2
              style={{
                fontSize: '24px',
                fontWeight: '600',
                color: '#111111',
                margin: '0 0 20px 0',
                textAlign: 'left',
                fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
              }}
            >
              {pack.name}
            </h2>

            {/* Pack Thumbnails */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(5, 1fr)',
                gap: '12px',
                marginBottom: '20px'
              }}
            >
              {pack.designs.map((design) => (
                <button
                  key={design.id}
                  onClick={() => {
                    console.log('🔘 BUTTON CLICKED - Design ID:', design.id)
                    handleDesignSelect(design)
                  }}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    aspectRatio: '1',
                    borderRadius: '12px',
                    border: selectedDesign?.id === design.id ? '3px solid #FF7CA3' : '2px solid #E5E5E5',
                    backgroundColor: isLoading ? '#F0F0F0' : '#F8F9FA',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '24px',
                    transition: 'all 200ms ease-out',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
                    opacity: isLoading && selectedDesign?.id !== design.id ? 0.5 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (selectedDesign?.id !== design.id) {
                      e.target.style.borderColor = '#111111'
                      e.target.style.transform = 'scale(1.05)'
                      e.target.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.08)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedDesign?.id !== design.id) {
                      e.target.style.borderColor = '#E5E5E5'
                      e.target.style.transform = 'scale(1)'
                      e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.04)'
                    }
                  }}
                  aria-label={`Select design ${design.id} from ${pack.name}`}
                >
                  {isLoading && selectedDesign?.id === design.id ? (
                    <div
                      style={{
                        width: '20px',
                        height: '20px',
                        border: '2px solid #ccc',
                        borderTop: '2px solid #FF7CA3',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}
                    />
                  ) : (
                    design.preview
                  )}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

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

export default BrowseDesignsScreen