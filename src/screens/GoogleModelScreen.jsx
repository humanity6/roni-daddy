import { useNavigate } from 'react-router-dom'

const GoogleModelScreen = () => {
  const navigate = useNavigate()

  const handleBack = () => {
    navigate('/phone-brand')
  }

  // Google is not available yet - show coming soon message
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
        Select Google Model
      </h1>

      {/* Coming Soon Message */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          maxWidth: '480px'
        }}
      >
        <div
          style={{
            fontSize: '64px',
            marginBottom: '32px',
            opacity: 0.3
          }}
        >
          🚧
        </div>

        <h2
          style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#111111',
            margin: '0 0 24px 0',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace'
          }}
        >
          Coming Soon
        </h2>

        <p
          style={{
            fontSize: '16px',
            color: '#666666',
            margin: '0 0 48px 0',
            fontFamily: 'IBM Plex Mono, Menlo, Monaco, Consolas, monospace',
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
        >
          Back to Brands
        </button>
      </div>

      {/* Font Import */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');
      `}</style>
    </div>
  )
}

export default GoogleModelScreen