import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Type, X, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import CircleSubmitButton from '../components/CircleSubmitButton'

const TextColorSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, inputText, selectedFont, fontSize, textPosition } = location.state || {}
  
  const [selectedTextColor, setSelectedTextColor] = useState('#ffffff')

  const colors = [
    { name: 'White', value: '#ffffff', bg: 'bg-white', border: 'border-gray-300' },
    { name: 'Black', value: '#000000', bg: 'bg-black', border: 'border-gray-800' },
    { name: 'Red', value: '#ef4444', bg: 'bg-red-500', border: 'border-red-500' },
    { name: 'Blue', value: '#3b82f6', bg: 'bg-blue-500', border: 'border-blue-500' },
    { name: 'Green', value: '#22c55e', bg: 'bg-green-500', border: 'border-green-500' },
    { name: 'Yellow', value: '#eab308', bg: 'bg-yellow-500', border: 'border-yellow-500' },
    { name: 'Purple', value: '#a855f7', bg: 'bg-purple-500', border: 'border-purple-500' },
    { name: 'Pink', value: '#ec4899', bg: 'bg-pink-500', border: 'border-pink-500' },
    { name: 'Orange', value: '#f97316', bg: 'bg-orange-500', border: 'border-orange-500' },
    { name: 'Teal', value: '#14b8a6', bg: 'bg-teal-500', border: 'border-teal-500' },
    { name: 'Indigo', value: '#6366f1', bg: 'bg-indigo-500', border: 'border-indigo-500' },
    { name: 'Gray', value: '#6b7280', bg: 'bg-gray-500', border: 'border-gray-500' },
    { name: 'Rose', value: '#f43f5e', bg: 'bg-rose-500', border: 'border-rose-500' },
    { name: 'Emerald', value: '#10b981', bg: 'bg-emerald-500', border: 'border-emerald-500' },
    { name: 'Sky', value: '#0ea5e9', bg: 'bg-sky-500', border: 'border-sky-500' },
    { name: 'Violet', value: '#8b5cf6', bg: 'bg-violet-500', border: 'border-violet-500' },
    { name: 'Amber', value: '#f59e0b', bg: 'bg-amber-500', border: 'border-amber-500' },
    { name: 'Lime', value: '#84cc16', bg: 'bg-lime-500', border: 'border-lime-500' },
    { name: 'Cyan', value: '#06b6d4', bg: 'bg-cyan-500', border: 'border-cyan-500' },
    { name: 'Fuchsia', value: '#d946ef', bg: 'bg-fuchsia-500', border: 'border-fuchsia-500' },
    { name: 'Slate', value: '#64748b', bg: 'bg-slate-500', border: 'border-slate-500' },
    { name: 'Stone', value: '#78716c', bg: 'bg-stone-500', border: 'border-stone-500' },
    { name: 'Zinc', value: '#71717a', bg: 'bg-zinc-500', border: 'border-zinc-500' },
    { name: 'Neutral', value: '#737373', bg: 'bg-neutral-500', border: 'border-neutral-500' }
  ]

  const handleBack = () => {
    navigate('/font-selection', { 
      state: { 
        brand, 
        model, 
        color, 
        template, 
        uploadedImage,
        inputText,
        selectedFont,
        textPosition
      } 
    })
  }

  const handleNext = () => {
    navigate('/payment', {
      state: {
        designImage: uploadedImage,
        price: 16.99 // or default
      }
    })
  }

  const getPreviewStyle = () => {
    const fonts = [
      { name: 'Arial', style: 'Arial, sans-serif' },
      { name: 'Georgia', style: 'Georgia, serif' },
      { name: 'Helvetica', style: 'Helvetica, sans-serif' },
      { name: 'Times New Roman', style: 'Times New Roman, serif' },
      { name: 'Verdana', style: 'Verdana, sans-serif' },
      { name: 'Comic Sans', style: 'Comic Sans MS, cursive' },
      { name: 'Impact', style: 'Impact, sans-serif' },
      { name: 'Palatino', style: 'Palatino, serif' },
      { name: 'Roboto', style: 'Roboto, sans-serif' },
      { name: 'Open Sans', style: 'Open Sans, sans-serif' },
      { name: 'Montserrat', style: 'Montserrat, sans-serif' },
      { name: 'Lato', style: 'Lato, sans-serif' }
    ]
    
    return {
      fontFamily: fonts.find(f => f.name === selectedFont)?.style || 'Arial, sans-serif',
      fontSize: `${fontSize}px`,
      color: selectedTextColor
    }
  }

  const getSelectedColorInfo = () => {
    return colors.find(c => c.value === selectedTextColor) || colors[0]
  }

  const getTextStyle = () => ({
    position: 'absolute',
    left: `${textPosition?.x || 50}%`,
    top: `${textPosition?.y || 50}%`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none'
  })

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
        <h1 className="text-lg font-semibold text-gray-800">Text Color</h1>
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
              <div style={getTextStyle()}>
                <div className="bg-black/20 px-4 py-2 rounded-lg backdrop-blur-sm whitespace-nowrap">
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

        {/* Selected Color Info */}
        <div className="w-full max-w-xs mb-6">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
            <div className="flex items-center justify-center space-x-3">
              <div className={`w-8 h-8 rounded-full ${getSelectedColorInfo().bg} border-2 ${getSelectedColorInfo().border} shadow-md`}></div>
              <div className="text-center">
                <p className="text-lg font-medium text-gray-800">{getSelectedColorInfo().name}</p>
                <p className="text-xs text-gray-500">{selectedTextColor.toUpperCase()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Horizontal Color Slider */}
        <div className="w-full mb-8">
          <div className="relative">
                         <div 
               className="color-slider flex space-x-4 px-4 pb-4 overflow-x-auto"
             >
              {colors.map((colorOption, index) => (
                <button
                  key={colorOption.value}
                  onClick={() => setSelectedTextColor(colorOption.value)}
                                     className={`
                     color-option w-12 h-12 rounded-full border-3 transition-all duration-300 shadow-lg
                     ${colorOption.bg}
                     ${selectedTextColor === colorOption.value 
                       ? 'border-pink-400 scale-125 shadow-xl' 
                       : `${colorOption.border} hover:scale-110 active:scale-95`
                     }
                   `}
                  title={colorOption.name}
                  style={{
                    minWidth: '3rem',
                    marginRight: index === colors.length - 1 ? '1rem' : '0'
                  }}
                >
                  {selectedTextColor === colorOption.value && (
                    <div className="w-full h-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse shadow-sm"></div>
                    </div>
                  )}
                </button>
              ))}
            </div>
            
            {/* Scroll Indicators */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-6 h-12 bg-gradient-to-r from-white/80 to-transparent pointer-events-none rounded-r-full"></div>
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-6 h-12 bg-gradient-to-l from-white/80 to-transparent pointer-events-none rounded-l-full"></div>
          </div>
          
          {/* Scroll hint */}
          <p className="text-center text-xs text-gray-500 mt-2">
            Slide to see more colors →
          </p>
        </div>

        {/* Sample Text Preview */}
        <div className="w-full max-w-xs mb-6">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
            <p className="text-center text-gray-600 text-sm mb-2">Preview:</p>
            <div className="bg-gray-100 rounded-lg p-3">
              <p 
                className="text-center"
                style={getPreviewStyle()}
              >
                {inputText || 'Sample Text'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        <CircleSubmitButton onClick={handleNext} label="Submit" />
      </div>


    </div>
  )
}

export default TextColorSelectionScreen 