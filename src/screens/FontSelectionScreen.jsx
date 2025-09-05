import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, ArrowUp, ArrowDown, ArrowRight as ArrowRightIcon, Type, Minus, Plus, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import CircleSubmitButton from '../components/CircleSubmitButton'
import { useTextBoundaries, validateFontSize, createPositionHandlers } from '../utils/textBoundaryManager'
import { fonts as availableFonts } from '../utils/fontManager'

const FontSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, uploadedImages, imageTransforms, inputText, textPosition, transform: initialTransform, stripCount, selectedTextColor, selectedModelData, deviceId } = location.state || {}
  
  const [selectedFont, setSelectedFont] = useState(location.state?.selectedFont || 'Arial')
  const [fontSize, setFontSize] = useState(location.state?.fontSize || 30)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [adjustedTextPosition, setAdjustedTextPosition] = useState(textPosition || { x: 50, y: 50 })
  const [isPositionBeingAdjusted, setIsPositionBeingAdjusted] = useState(false)

  // Use the enhanced text boundary management system with model-specific dimensions
  const {
    textDimensions,
    containerDimensions,
    safeBoundaries,
    constrainPosition,
    validateTextFit,
    getFontStyle,
    measureRef
  } = useTextBoundaries(template, inputText, fontSize, selectedFont, selectedModelData)

  // Position handlers for manual adjustment
  const positionHandlers = createPositionHandlers(adjustedTextPosition, safeBoundaries, setAdjustedTextPosition)

  // The centralised font catalogue
  const fonts = availableFonts

  // Initialize adjusted position when component mounts
  useEffect(() => {
    if (textPosition) {
      setAdjustedTextPosition(textPosition)
    }
  }, [textPosition])

  // Adjust position when text size changes due to font/size changes
  useEffect(() => {
    if (inputText?.trim() && textDimensions.width > 0 && !isPositionBeingAdjusted) {
      const constrainedPosition = constrainPosition(adjustedTextPosition)
      
      if (constrainedPosition.x !== adjustedTextPosition.x || constrainedPosition.y !== adjustedTextPosition.y) {
        setIsPositionBeingAdjusted(true)
        setAdjustedTextPosition(constrainedPosition)
        
        // Reset the flag after a short delay
        setTimeout(() => {
          setIsPositionBeingAdjusted(false)
        }, 100)
      }
    }
  }, [textDimensions, inputText, selectedFont, fontSize, constrainPosition, adjustedTextPosition, isPositionBeingAdjusted])

  const handleBack = () => {
    navigate('/text-input', { 
      state: { 
        brand, 
        model, 
        color, 
        template, 
        uploadedImage,
        uploadedImages,
        imageTransforms,
        inputText,
        selectedFont,
        fontSize,
        textPosition: adjustedTextPosition, // Pass the adjusted position back
        selectedTextColor,
        transform: initialTransform,
        stripCount,
        selectedModelData,
        deviceId
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
        uploadedImages,
        imageTransforms,
        inputText,
        selectedFont,
        fontSize,
        textPosition: adjustedTextPosition, // Pass the adjusted position forward
        selectedTextColor,
        transform: initialTransform,
        stripCount,
        selectedModelData,
        deviceId
      } 
    })
  }

  const increaseFontSize = () => {
    const newSize = validateFontSize(Math.min(30, fontSize + 2), inputText?.length || 0, containerDimensions)
    setFontSize(newSize)
  }

  const decreaseFontSize = () => {
    const newSize = validateFontSize(Math.max(12, fontSize - 2), inputText?.length || 0, containerDimensions)
    setFontSize(newSize)
  }

  const getPreviewStyle = () => ({
    ...getFontStyle(),
    color: selectedTextColor || '#ffffff'
  })

  const handleFontSelect = (fontName) => {
    setSelectedFont(fontName)
    setIsDropdownOpen(false)
  }

  const getTextStyle = () => ({
    position: 'absolute',
    left: `${adjustedTextPosition.x}%`,
    top: `${adjustedTextPosition.y}%`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none',
    textAlign: 'center'
  })

  return (
    <div className="screen-container" style={{ overflow: 'visible' }}>
      <PastelBlobs />
      
      {/* Hidden measurement div */}
      <div className="fixed -top-[9999px] -left-[9999px] pointer-events-none">
        <div
          ref={measureRef}
          style={getFontStyle()}
        >
          {inputText || 'M'}
        </div>
      </div>
      
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
      <div className="relative z-50 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          {template?.id?.startsWith('film-strip') ? (
            <div className="relative w-[525px] h-[525px] overflow-hidden pointer-events-none">
              <div
                className="absolute inset-0 flex flex-col justify-center items-center z-10"
                style={{ paddingTop:'0px', paddingBottom:'0px', paddingLeft:'180px', paddingRight:'179px'}}
              >
                {uploadedImages && uploadedImages.map((img, idx) => (
                  <div
                    key={idx}
                    className="w-full overflow-hidden rounded-sm transition-all duration-300 border-t-[8px] border-b-[8px] border-black"
                    style={{ height: `${100 / (stripCount || 3) - 2}%` }}
                  >
                    <img 
                      src={img} 
                      alt={`Photo ${idx + 1}`} 
                      className="w-full h-full object-contain"
                      style={{
                        objectPosition: `${imageTransforms?.[idx]?.x || 50}% ${imageTransforms?.[idx]?.y || 50}%`,
                        transform: `scale(${imageTransforms?.[idx]?.scale || 1})`
                      }}
                    />
                  </div>
                ))}
              </div>
              <div className="absolute inset-0 z-20 pointer-events-none">
                <img src="/filmstrip-case.png" alt="Film strip case" className="w-full h-full object-contain" />
              </div>
              
              {/* Text overlay for film strip */}
              {inputText && (
                <div 
                  className="absolute z-30 pointer-events-none"
                  style={getTextStyle()}
                >
                  <div 
                    className="text-white"
                    style={{
                      ...getFontStyle(),
                      color: selectedTextColor || '#ffffff'
                    }}
                  >
                    {inputText}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="relative w-72 h-[480px]">
              {/* Separate border element */}
              <div className="phone-case-border"></div>
              
              {/* User's uploaded image */}
              <div className="phone-case-content">
                {uploadedImages && uploadedImages.length > 0 ? (
                  <div className="w-full h-full overflow-hidden">
                    {uploadedImages.length === 4 ? (
                      <div className="w-full h-full flex flex-wrap">
                        {uploadedImages.map((img, idx) => (
                          <div key={idx} className="w-1/2 h-1/2 overflow-hidden">
                            <img 
                              src={img} 
                              alt={`design ${idx+1}`} 
                              className="w-full h-full object-contain"
                              style={{
                                transform: imageTransforms && imageTransforms[idx] 
                                  ? `translate(${imageTransforms[idx].x}%, ${imageTransforms[idx].y}%) scale(${imageTransforms[idx].scale})`
                                  : 'translate(0%, 0%) scale(1)',
                                transformOrigin: 'center center'
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="w-full h-full flex flex-col">
                        {uploadedImages.map((img, idx) => (
                          <div key={idx} className="flex-1 overflow-hidden">
                            <img 
                              src={img} 
                              alt={`design ${idx+1}`} 
                              className="w-full h-full object-contain"
                              style={{
                                transform: imageTransforms && imageTransforms[idx] 
                                  ? `translate(${imageTransforms[idx].x}%, ${imageTransforms[idx].y}%) scale(${imageTransforms[idx].scale})`
                                  : 'translate(0%, 0%) scale(1)',
                                transformOrigin: 'center center'
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : uploadedImage ? (
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded design" 
                    className="phone-case-image-contain"
                    style={initialTransform ? { transform: `translate(${initialTransform.x}%, ${initialTransform.y}%) scale(${initialTransform.scale})`, transformOrigin: 'center center' } : undefined}
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
                  <div 
                    className="text-white"
                    style={{
                      ...getFontStyle(),
                      color: selectedTextColor || '#ffffff'
                    }}
                  >
                    {inputText}
                  </div>
                </div>
              )}
              
              {/* Phone Template Overlay */}
              <div className="absolute inset-0 pointer-events-none">
                <img 
                  src="/phone-template.png" 
                  alt="Phone template overlay" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
        </div>

        {/* Navigation Arrows with Font Size Controls */}
        <div className="w-full max-w-xs mb-6 flex items-center justify-between">
          {/* Left Arrow */}
          <button
            onClick={handleBack}
            className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform"
          >
            <ChevronLeft size={20} className="text-gray-600" />
          </button>

          {/* Font Size Controls */}
          <div className="flex items-center justify-between bg-white/80 backdrop-blur-sm rounded-full p-4 shadow-lg mx-2 flex-1">
            <button 
              onClick={decreaseFontSize}
              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center active:scale-95 transition-transform"
              disabled={fontSize <= 12}
            >
              <Minus size={16} className="text-gray-600" />
            </button>
            <div className="text-center px-2 flex-1">
              <span className="text-lg font-medium text-gray-800">{fontSize}px</span>
              <p className="text-xs text-gray-500">Font Size</p>
            </div>
            <button 
              onClick={increaseFontSize}
              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center active:scale-95 transition-transform"
              disabled={fontSize >= 30}
            >
              <Plus size={16} className="text-gray-600" />
            </button>
          </div>

          {/* Right Arrow */}
          <button
            onClick={handleNext}
            className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform"
          >
            <ChevronRight size={20} className="text-gray-600" />
          </button>
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
            <div className="dropdown-menu absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-200 max-h-64 overflow-y-auto pointer-events-auto z-50">
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



        {/* Position Control Buttons */}
        {inputText && (
          <div className="mb-6">
            <p className="text-center text-sm font-medium text-gray-700 mb-3">Position Text</p>

            {/* Up button */}
            <div className="flex justify-center mb-2">
              <button 
                onClick={positionHandlers.moveUp}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowUp size={20} className="text-gray-600" />
              </button>
            </div>

            {/* Left and Right buttons */}
            <div className="flex items-center justify-center space-x-12 mb-2">
              <button 
                onClick={positionHandlers.moveLeft}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
              <button 
                onClick={positionHandlers.moveRight}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowRightIcon size={20} className="text-gray-600" />
              </button>
            </div>

            {/* Down button */}
            <div className="flex justify-center">
              <button 
                onClick={positionHandlers.moveDown}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowDown size={20} className="text-gray-600" />
              </button>
            </div>
          </div>
        )}
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
        <div className="w-24 h-24 rounded-full border-8 border-pink-400 flex items-center justify-center shadow-xl">
          <div className="w-17 h-17 rounded-full border-0.5 border-white bg-white flex items-center justify-center">
            <button 
              onClick={handleNext}
              className="w-16 h-16 rounded-full bg-pink-400 text-white flex items-center justify-center active:scale-95 transition-transform"
            >
              <span className="font-semibold text-xs">Submit</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FontSelectionScreen