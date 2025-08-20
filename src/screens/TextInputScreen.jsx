import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Type, X, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import { useTextBoundaries, validateTextInput, createPositionHandlers, validateFontSize } from '../utils/textBoundaryManager'

const TextInputScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { 
    brand, 
    model, 
    color, 
    template, 
    uploadedImage, 
    uploadedImages, 
    transform: initialTransform, 
    imageTransforms, 
    inputText: initialText, 
    textPosition: initialPosition, 
    stripCount,
    fontSize: initialFontSize,
    selectedFont: initialFont,
    selectedTextColor,
    selectedModelData,
    deviceId
  } = location.state || {}
  const { generatedImage, keyword, optionalText, aiCredits } = location.state || {}
  
  const [inputText, setInputText] = useState(initialText || '')
  const [textPosition, setTextPosition] = useState(initialPosition || { x: 50, y: 50 })
  const [fontSize, setFontSize] = useState(initialFontSize || 30)
  const [selectedFont, setSelectedFont] = useState(initialFont || 'Arial')
  const [isPositionBeingAdjusted, setIsPositionBeingAdjusted] = useState(false)
  
  const textBoxRef = useRef(null)
  const filmStripTextBoxRef = useRef(null)

  // Use the enhanced text boundary management system
  const {
    textDimensions,
    containerDimensions,
    safeBoundaries,
    constrainPosition,
    validateTextFit,
    getMaxSafeCharacters,
    getFontStyle,
    measureRef
  } = useTextBoundaries(template, inputText, fontSize, selectedFont)

  // Handle text input validation
  const handleTextChange = (e) => {
    const validatedText = validateTextInput(e.target.value, 50)
    setInputText(validatedText)
  }

  // Update state when location state changes (e.g., when coming back from FontSelectionScreen)
  useEffect(() => {
    if (location.state?.fontSize !== undefined) {
      setFontSize(location.state.fontSize)
    }
    if (location.state?.selectedFont !== undefined) {
      setSelectedFont(location.state.selectedFont)
    }
    if (location.state?.textPosition !== undefined) {
      setTextPosition(location.state.textPosition)
    }
  }, [location.state?.fontSize, location.state?.selectedFont, location.state?.textPosition])

  // Adjust position when text size changes, but avoid infinite loops
  useEffect(() => {
    if (inputText.trim() && textDimensions.width > 0 && !isPositionBeingAdjusted) {
      const constrainedPosition = constrainPosition(textPosition)
      
      if (constrainedPosition.x !== textPosition.x || constrainedPosition.y !== textPosition.y) {
        setIsPositionBeingAdjusted(true)
        setTextPosition(constrainedPosition)
        
        // Reset the flag after a short delay
        setTimeout(() => {
          setIsPositionBeingAdjusted(false)
        }, 100)
      }
    }
  }, [textDimensions, inputText, constrainPosition, textPosition, isPositionBeingAdjusted])

  const handleBack = () => {
    if (template?.id?.startsWith('film-strip')) {
      navigate('/film-strip-upload', {
        state: {
          brand,
          model,
          color,
          template,
          stripCount,
          uploadedImages,
          imageTransforms,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.imageCount && template.imageCount > 1) {
      navigate('/multi-image-upload', {
        state: {
          brand,
          model,
          color,
          template,
          imageTransforms,
          stripCount,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id === 'retro-remix') {
      navigate('/retro-remix-generate', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          keyword,
          optionalText,
          aiCredits,
          transform: initialTransform,
          selectedModelData,
          deviceId
        }
      })
    } else {
      navigate('/phone-preview', { 
        state: { 
          brand, 
          model, 
          color, 
          template,
          uploadedImage,
          transform: initialTransform,
          imageTransforms,
          stripCount,
          selectedModelData,
          deviceId
        } 
      })
    }
  }

  const handleNext = () => {
    navigate('/font-selection', { 
      state: { 
        brand, 
        model, 
        color, 
        template, 
        uploadedImage,
        uploadedImages,
        imageTransforms,
        stripCount,
        inputText,
        textPosition,
        fontSize,
        selectedFont,
        selectedTextColor,
        transform: initialTransform,
        selectedModelData,
        deviceId
      } 
    })
  }

  const resetInput = () => {
    setInputText('')
    setTextPosition({ x: 50, y: 50 })
  }

  // Ensure text starts centered when first added
  useEffect(() => {
    if (inputText.trim() && !textPosition.x && !textPosition.y) {
      setTextPosition({ x: 50, y: 50 })
    }
  }, [inputText, textPosition])

  // Text positioning functions with enhanced boundary constraints
  const positionHandlers = createPositionHandlers(textPosition, safeBoundaries, setTextPosition)

  const getTextStyle = () => ({
    position: 'absolute',
    left: `${textPosition.x}%`,
    top: `${textPosition.y}%`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none',
    textAlign: 'center'
  })

  return (
    <div className="screen-container">
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
        <h1 className="text-lg font-semibold text-gray-800">Add Text</h1>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-6">
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
                      className="w-full h-full object-cover"
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
                    ref={filmStripTextBoxRef}
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
                              className="w-full h-full object-cover"
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
                              className="w-full h-full object-cover"
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
                    style={initialTransform ? { transform:`translate(${initialTransform.x}%, ${initialTransform.y}%) scale(${initialTransform.scale})`, transformOrigin:'center center' } : undefined}
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
                    ref={textBoxRef}
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
              
              {/* Case Template Overlay */}
              <div className="absolute inset-0 pointer-events-none">
                <img 
                  src="/phone-template.png" 
                  alt="Phone case overlay" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
        </div>

        {/* Text Input Section */}
        <div className="w-full max-w-xs mb-6">
          <div className="flex items-center space-x-2">
            {/* Left Arrow */}
            <button onClick={handleBack} className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform">
              <ChevronLeft size={20} className="text-gray-600" />
            </button>

            {/* Input field */}
            <div className="relative flex-1">
              <input
                type="text"
                value={inputText}
                onChange={handleTextChange}
                placeholder="Enter Text"
                className="w-full bg-white/80 backdrop-blur-sm border-2 border-gray-200 rounded-full px-6 py-4 text-center text-lg font-poppins font-bold shadow-lg focus:outline-none focus:border-pink-400 transition-colors"
                maxLength={getMaxSafeCharacters()}
              />
              {inputText && (
                <button
                  onClick={resetInput}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center"
                >
                  <X size={14} className="text-gray-600" />
                </button>
              )}
            </div>

            {/* Right Arrow */}
            <button onClick={handleNext} className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform">
              <ChevronRight size={20} className="text-gray-600" />
            </button>
          </div>
          <p className="text-center text-xs text-gray-500 mt-2">
            {inputText.length}/{getMaxSafeCharacters()} characters
          </p>
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
                <ArrowRight size={20} className="text-gray-600" />
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

        {/* Reset Button */}
        {inputText && (
          <button 
            onClick={resetInput}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}
      </div>

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

export default TextInputScreen