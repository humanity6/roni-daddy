import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppState } from '../contexts/AppStateContext'
import PastelBlobs from '../components/PastelBlobs'

const IPhoneModelScreen = () => {
  const navigate = useNavigate()
  const { actions } = useAppState()
  const [selectedModel, setSelectedModel] = useState('IPHONE 16')
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const iPhoneModels = [
    'IPHONE 16 PRO MAX',
    'IPHONE 16 PRO',
    'IPHONE 16 PLUS',
    'IPHONE 16',
    'IPHONE 15 PRO MAX',
    'IPHONE 15 PRO',
    'IPHONE 15 PLUS',
    'IPHONE 15',
    'IPHONE 14 PRO MAX',
    'IPHONE 14 PRO',
    'IPHONE 14 PLUS',
    'IPHONE 14',
    'IPHONE 13 PRO MAX',
    'IPHONE 13 PRO',
    'IPHONE 13 MINI',
    'IPHONE 13'
  ]

  const handleSubmit = () => {
    actions.setPhoneSelection('iphone', selectedModel.toLowerCase().replace(/\s+/g, '-'), null)
    navigate('/template-selection')
  }

  const handleBack = () => {
    navigate('/phone-brand')
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
        fontFamily: 'PoppinsLight, sans-serif',
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
          border: '5px solid #e277aa',
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
          <path d="M15 18L9 12L15 6" stroke="#e277aa" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
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
          src="/iphoneblob.svg"
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
          IPHONE MODEL
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
          alignSelf: 'center',
          marginTop: '20px',
          zIndex: 10
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
              background: 'white',
              borderRadius: '25px',
              padding: '12px 20px',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: 'PoppinsLight, sans-serif',
              fontSize: '14px',
              fontWeight: '500',
              color: '#333'
            }}
          >
            <span>{selectedModel}</span>
            <div
              style={{
                width: '20px',
                height: '20px',
                background: '#666',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 9L12 15L18 9" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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
              {iPhoneModels.map((model, index) => (
                <div
                  key={index}
                  onClick={() => {
                    setSelectedModel(model)
                    setDropdownOpen(false)
                  }}
                  style={{
                    padding: '12px 20px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    color: '#333',
                    borderBottom: index < iPhoneModels.length - 1 ? '1px solid #eee' : 'none',
                    fontFamily: 'PoppinsLight, sans-serif',
                    transition: 'background-color 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  {model}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button - Thinner border, consistent color */}
        <div
          onClick={handleSubmit}
          style={{
            position: 'absolute',
            bottom: '60px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            background: '#e277aa',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            transition: 'transform 0.2s ease',
            zIndex: 100
          }}
          onMouseDown={(e) => e.currentTarget.style.transform = 'translateX(-50%) scale(0.95)'}
          onMouseUp={(e) => e.currentTarget.style.transform = 'translateX(-50%) scale(1)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'translateX(-50%) scale(1)'}
        >
          {/* Inner Circle - Thinner border */}
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: '#e277aa',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              fontWeight: 'bold',
              color: '#2c3e50',
              fontFamily: 'PoppinsLight, sans-serif',
              border: '7px solid #474746'
            }}
          >
            Submit
          </div>
        </div>
      </div>
    </div>
  )
}

export default IPhoneModelScreen 