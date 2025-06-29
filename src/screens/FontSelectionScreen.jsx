import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Type, Minus, Plus, ChevronDown } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import CircleSubmitButton from '../components/CircleSubmitButton'

const FontSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, inputText, textPosition } = location.state || {}
  
  const [selectedFont, setSelectedFont] = useState('Arial')
  const [fontSize, setFontSize] = useState(18)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const fonts = [
    { name: 'Arial', className: 'font-sans', style: 'Arial, sans-serif' },
    { name: 'Georgia', className: 'font-serif', style: 'Georgia, serif' },
    { name: 'Helvetica', className: 'font-sans', style: 'Helvetica, sans-serif' },
    { name: 'Times New Roman', className: 'font-serif', style: 'Times New Roman, serif' },
    { name: 'Verdana', className: 'font-sans', style: 'Verdana, sans-serif' },
    { name: 'Comic Sans', className: 'font-mono', style: 'Comic Sans MS, cursive' },
    { name: 'Impact', className: 'font-bold', style: 'Impact, sans-serif' },
    { name: 'Palatino', className: 'font-serif', style: 'Palatino, serif' },
    { name: 'Roboto', className: 'font-sans', style: 'Roboto, sans-serif' },
    { name: 'Open Sans', className: 'font-sans', style: 'Open Sans, sans-serif' },
    { name: 'Montserrat', className: 'font-sans', style: 'Montserrat, sans-serif' },
    { name: 'Lato', className: 'font-sans', style: 'Lato, sans-serif' }
  ]

  const handleBack = () => {
    navigate('/text-input', { 
      state: { 
        brand, 
        model, 
        color, 
        template, 
        uploadedImage,
        inputText,
        selectedFont,
        fontSize,
        textPosition
      } 
    })
  }

  const handleNext = () => {
    navigate('/text-color-selection', { 
      state: { 
        brand, 
        model, 
        color, 
        template, 
        uploadedImage,
        inputText,
        selectedFont,
        fontSize,
        textPosition
      } 
    })
  }

  const increaseFontSize = () => {
    if (fontSize < 32) {
      setFontSize(prev => prev + 2)
    }
  }

  const decreaseFontSize = () => {
    if (fontSize > 12) {
      setFontSize(prev => prev - 2)
    }
  }

  const getPreviewStyle = () => ({
    fontFamily: fonts.find(f => f.name === selectedFont)?.style || 'Arial, sans-serif',
    fontSize: `${fontSize}px`
  })

  const handleFontSelect = (fontName) => {
    setSelectedFont(fontName)
    setIsDropdownOpen(false)
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button 
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-pink-400 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-white" />
        </button>
        <h1 className="text-lg font-semibold text-gray-800">Choose Font</h1>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          <div className="relative w-72 h-[480px]">
            {/* User's uploaded image */}
            <div className="phone-case-content">
              {uploadedImage ? (
                <img 
                  src={uploadedImage} 
                  alt="Uploaded design" 
                  className="phone-case-image"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <Type size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Your design here</p>
                  </div>
                </div>
              )}
            </div>

            {/* Text overlay preview */}
            {inputText && (
              <div 
                className="absolute pointer-events-none"
                style={{
                  left: `${textPosition?.x || 50}%`,
                  top: `${textPosition?.y || 50}%`,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                <div className="bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm whitespace-nowrap">
                  <p style={getPreviewStyle()}>{inputText}</p>
                </div>
              </div>
            )}
            
            {/* Phone Template Overlay */}
            <div className="absolute inset-0">
              <img 
                src="/phone-template.png" 
                alt="Phone template overlay" 
                className="w-full h-full object-contain pointer-events-none"
              />
            </div>
          </div>
        </div>

        {/* Font Size Controls */}
        <div className="w-full max-w-xs mb-6">
          <div className="flex items-center justify-between bg-white/80 backdrop-blur-sm rounded-full p-4 shadow-lg">
            <button 
              onClick={decreaseFontSize}
              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center active:scale-95 transition-transform"
              disabled={fontSize <= 12}
            >
              <Minus size={16} className="text-gray-600" />
            </button>
            <div className="text-center">
              <span className="text-lg font-medium text-gray-800">{fontSize}px</span>
              <p className="text-xs text-gray-500">Font Size</p>
            </div>
            <button 
              onClick={increaseFontSize}
              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center active:scale-95 transition-transform"
              disabled={fontSize >= 32}
            >
              <Plus size={16} className="text-gray-600" />
            </button>
          </div>
        </div>

        {/* Font Selection Dropdown */}
        <div className="w-full max-w-sm mb-8 relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full bg-white/80 backdrop-blur-sm border-2 border-gray-200 rounded-2xl p-4 shadow-lg active:scale-95 transition-all duration-200 flex items-center justify-between"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center">
                <Type size={16} className="text-pink-600" />
              </div>
              <div className="text-left">
                <p className="font-medium text-gray-800" style={{ fontFamily: fonts.find(f => f.name === selectedFont)?.style }}>
                  {selectedFont}
                </p>
                <p className="text-xs text-gray-500">Font Family</p>
              </div>
            </div>
            <ChevronDown 
              size={20} 
              className={`text-gray-600 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} 
            />
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="dropdown-menu absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-200 max-h-64 overflow-y-auto z-50">
              {fonts.map((font) => (
                <button
                  key={font.name}
                  onClick={() => handleFontSelect(font.name)}
                  className="w-full p-4 text-left hover:bg-gray-50 first:rounded-t-2xl last:rounded-b-2xl transition-colors duration-200 border-b border-gray-100 last:border-b-0"
                >
                  <p 
                    className="font-medium text-gray-800"
                    style={{ fontFamily: font.style }}
                  >
                    {font.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1" style={{ fontFamily: font.style }}>
                    The quick brown fox jumps
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sample Text Preview */}
        <div className="w-full max-w-xs mb-6">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
            <p className="text-center text-gray-600 text-sm mb-2">Preview:</p>
            <p 
              className="text-center text-gray-800"
              style={getPreviewStyle()}
            >
              {inputText || 'Sample Text'}
            </p>
          </div>
        </div>
      </div>

      {/* Overlay to close dropdown */}
      {isDropdownOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsDropdownOpen(false)}
        />
      )}

      {/* Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        <CircleSubmitButton onClick={handleNext} label="Submit" />
      </div>
    </div>
  )
}

export default FontSelectionScreen 