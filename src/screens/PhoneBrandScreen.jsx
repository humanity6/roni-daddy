import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PastelBlobs from '../components/PastelBlobs'

const PhoneBrandScreen = () => {
  const navigate = useNavigate()
  const [selectedBrand, setSelectedBrand] = useState('')

  const brands = [
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
      frameColor: '#d4eafb',
      buttonColor: '#b9ddf7',
      available: true
    }
  ]

  const handleBrandSelect = (brandId) => {
    if (brands.find(b => b.id === brandId)?.available) {
      setSelectedBrand(brandId)
      setTimeout(() => {
        // Navigate to specific model screen based on brand
        switch(brandId) {
          case 'iphone':
            navigate('/iphone-model')
            break
          case 'samsung':
            navigate('/samsung-model')
            break
          case 'google':
            navigate('/google-model')
            break
          default:
            navigate('/iphone-model')
        }
      }, 300)
    }
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
        marginBottom: '-50px',
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
              opacity: brand.available ? 1 : 0.7,
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
                gap: brand.subtitle ? '2px' : '0' 
              }}>
                <span
                  style={{
                    fontSize: '22px',
                    fontWeight: 'normal',
                    color: '#2c3e50',
                    letterSpacing: '0.5px',
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
                      fontFamily: 'Arial, sans-serif'
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
          style={{ height: '300px', width: 'auto' }} 
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