import { useNavigate } from 'react-router-dom'
import PastelBlobs from '../components/PastelBlobs'

const GoogleModelScreen = () => {
  const navigate = useNavigate()

  const handleBack = () => {
    navigate('/phone-brand')
  }

  // Google is not available yet - show coming soon message
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
          border: '5px solid #CBE8F4',
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
          <path d="M15 18L9 12L15 6" stroke="#CBE8F4" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
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
          src="/google blob.svg"
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
          GOOGLE PIXEL
        </h1>
      </div>

      {/* Coming Soon Message */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          zIndex: 10,
          textAlign: 'center',
          maxWidth: '400px',
          margin: '0 auto'
        }}
      >
        <div 
          style={{
            fontSize: '72px',
            marginBottom: '30px',
            opacity: 0.3
          }}
        >
          🚧
        </div>
        
        <h2 
          style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#474746',
            margin: '0 0 15px 0',
            fontFamily: 'Cubano, sans-serif'
          }}
        >
          COMING SOON
        </h2>
        
        <p 
          style={{
            fontSize: '18px',
            color: '#666',
            margin: '0 0 30px 0',
            fontFamily: 'PoppinsLight, sans-serif',
            lineHeight: '1.6'
          }}
        >
          Google Pixel phone cases will be available soon.
          <br />
          Check back later for more options!
        </p>
        
        <button
          onClick={handleBack}
          style={{
            backgroundColor: '#CBE8F4',
            color: '#474746',
            border: 'none',
            borderRadius: '25px',
            padding: '15px 30px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            fontFamily: 'Cubano, sans-serif',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}
          onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
          onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          BACK TO BRANDS
        </button>
      </div>
    </div>
  )
}

export default GoogleModelScreen