import React from 'react'

const CircleSubmitButton = ({ 
  label = 'Submit', 
  onClick, 
  disabled = false,
  color = '#e277aa',
  borderColor = '#474746',
  textColor = '#2c3e50',
  position = 'relative',
  style = {},
  className = ''
}) => {
  const buttonStyle = {
    position: position,
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: disabled ? '#ccc' : color,
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    transition: 'transform 0.2s ease',
    zIndex: 100,
    ...style
  }

  const innerStyle = {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: disabled ? '#ccc' : color,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '8px',
    fontWeight: 'bold',
    textAlign: 'center',
    color: disabled ? '#999' : textColor,
    fontFamily: 'PoppinsLight, sans-serif',
    border: `7px solid ${disabled ? '#999' : borderColor}`,
    padding: '8px',
    // To make sure the text is not broken into multiple lines and is contained within the inner circle
    whiteSpace: 'nowrap',         // force single line
    overflow: 'hidden',           // hide overflow
  }

  const handleMouseDown = (e) => {
    if (!disabled) {
      e.currentTarget.style.transform = position === 'absolute' 
        ? 'translateX(-50%) scale(0.95)' 
        : 'scale(0.95)'
    }
  }

  const handleMouseUp = (e) => {
    if (!disabled) {
      e.currentTarget.style.transform = position === 'absolute' 
        ? 'translateX(-50%) scale(1)' 
        : 'scale(1)'
    }
  }

  const handleMouseLeave = (e) => {
    if (!disabled) {
      e.currentTarget.style.transform = position === 'absolute' 
        ? 'translateX(-50%) scale(1)' 
        : 'scale(1)'
    }
  }

  return (
    <div
      onClick={disabled ? undefined : onClick}
      style={buttonStyle}
      className={className}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
    >
      <div style={innerStyle}>
        {label}
      </div>
    </div>
  )
}

export default CircleSubmitButton 