import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Type, X, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const TextInputScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, uploadedImages, transform: initialTransform, imageTransforms, inputText: initialText, textPosition: initialPosition, stripCount } = location.state || {}
  const { generatedImage, keyword, optionalText, aiCredits } = location.state || {}
  
  const [inputText, setInputText] = useState(initialText || '')
  const [textPosition, setTextPosition] = useState(initialPosition || { x: 50, y: 50 }) // percentage from top-left
  const [textBoxSize, setTextBoxSize] = useState({ width: 0, height: 0 })
  const [phoneCaseSize, setPhoneCaseSize] = useState({ width: 220, height: 400 }) // Default phone case size (w-72 h-[480px])
  const textBoxRef = useRef(null)
  const filmStripTextBoxRef = useRef(null)

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
          imageTransforms
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
          stripCount
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
          transform: initialTransform
          // Removed generatedImage to reset it
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
          stripCount
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
        transform: initialTransform
      } 
    })
  }

  const resetInput = () => {
    setInputText('')
    setTextPosition({ x: 50, y: 50 })
  }

  // Calculate dynamic boundaries based on text box size
  const getDynamicBoundaries = () => {
    if (textBoxSize.width === 0 || textBoxSize.height === 0) {
      return { minX: 20, maxX: 80, minY: 15, maxY: 85 }
    }
    
    // Calculate boundaries to keep text box fully within phone case
    const minX = (textBoxSize.width / 2) / phoneCaseSize.width * 100
    const maxX = 100 - (textBoxSize.width / 2) / phoneCaseSize.width * 100
    const minY = (textBoxSize.height / 2) / phoneCaseSize.height * 100
    const maxY = 100 - (textBoxSize.height / 2) / phoneCaseSize.height * 100
    
    return { minX, maxX, minY, maxY }
  }

  // Ensure text position stays within dynamic boundaries
  useEffect(() => {
    const boundaries = getDynamicBoundaries()
    let newPosition = { ...textPosition }
    let changed = false
    
    if (textPosition.x < boundaries.minX) {
      newPosition.x = boundaries.minX
      changed = true
    }
    if (textPosition.x > boundaries.maxX) {
      newPosition.x = boundaries.maxX
      changed = true
    }
    if (textPosition.y < boundaries.minY) {
      newPosition.y = boundaries.minY
      changed = true
    }
    if (textPosition.y > boundaries.maxY) {
      newPosition.y = boundaries.maxY
      changed = true
    }
    
    if (changed) {
      setTextPosition(newPosition)
    }
  }, [textPosition, textBoxSize, phoneCaseSize])

  // Measure text box size when text changes
  useEffect(() => {
    let rect = null
    if (template?.id?.startsWith('film-strip')) {
      if (filmStripTextBoxRef.current && inputText) {
        rect = filmStripTextBoxRef.current.getBoundingClientRect()
      }
    } else {
      if (textBoxRef.current && inputText) {
        rect = textBoxRef.current.getBoundingClientRect()
      }
    }
    
    if (rect) {
      setTextBoxSize({ width: rect.width, height: rect.height })
    } else {
      setTextBoxSize({ width: 0, height: 0 })
    }
  }, [inputText, template])

  // Text positioning functions with dynamic boundary constraints
  const moveTextLeft = () => {
    const boundaries = getDynamicBoundaries()
    setTextPosition(prev => ({ ...prev, x: Math.max(boundaries.minX, prev.x - 5) }))
  }

  const moveTextRight = () => {
    const boundaries = getDynamicBoundaries()
    setTextPosition(prev => ({ ...prev, x: Math.min(boundaries.maxX, prev.x + 5) }))
  }

  const moveTextUp = () => {
    const boundaries = getDynamicBoundaries()
    setTextPosition(prev => ({ ...prev, y: Math.max(boundaries.minY, prev.y - 5) }))
  }

  const moveTextDown = () => {
    const boundaries = getDynamicBoundaries()
    setTextPosition(prev => ({ ...prev, y: Math.min(boundaries.maxY, prev.y + 5) }))
  }

  const getTextStyle = () => ({
    position: 'absolute',
    left: `${textPosition.x}%`,
    top: `${textPosition.y}%`,
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
              
              {/* Text overlay for film strip - positioned above everything */}
              {inputText && (
                <div 
                  className="absolute z-30 pointer-events-none"
                  style={{
                    left: `${textPosition?.x || 50}%`,
                    top: `${textPosition?.y || 50}%`,
                    transform: 'translate(-50%, -50%)'
                  }}
                >
                  <div 
                    ref={filmStripTextBoxRef}
                    className="bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm max-w-[160px] overflow-hidden"
                  >
                    <p className="text-lg font-medium break-words leading-tight">{inputText}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="relative w-72 h-[480px]">
              {/* Separate border element - positioned independently */}
              <div className="phone-case-border"></div>
              
              {/* User's uploaded image */}
              <div className="phone-case-content">
                {uploadedImages && uploadedImages.length > 0 ? (
                  // Default layouts for other templates
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
                    className="bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm max-w-[160px] overflow-hidden"
                  >
                    <p className="text-lg font-medium break-words leading-tight">{inputText}</p>
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
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter Text"
                className="w-full bg-white/80 backdrop-blur-sm border-2 border-gray-200 rounded-full px-6 py-4 text-center text-lg font-poppins font-bold shadow-lg focus:outline-none focus:border-pink-400 transition-colors"
                maxLength={50}
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
            {inputText.length}/50 characters
          </p>
        </div>

        {/* Position Control Buttons */}
        {inputText && (
          <div className="mb-6">
            <p className="text-center text-sm font-medium text-gray-700 mb-3">Position Text</p>
            
            {/* Up button */}
            <div className="flex justify-center mb-2">
              <button 
                onClick={moveTextUp}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowUp size={20} className="text-gray-600" />
              </button>
            </div>

            {/* Left and Right buttons */}
            <div className="flex items-center justify-center space-x-12 mb-2">
              <button 
                onClick={moveTextLeft}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
              <button 
                onClick={moveTextRight}
                className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform"
              >
                <ArrowRight size={20} className="text-gray-600" />
              </button>
            </div>

            {/* Down button */}
            <div className="flex justify-center">
              <button 
                onClick={moveTextDown}
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
        {/* Outer Pink Ring */}
        <div className="w-24 h-24 rounded-full border-8 border-pink-400 flex items-center justify-center shadow-xl">
          {/* Updated: minimal gap between circles */}
          <div className="w-17 h-17 rounded-full border-0.5 border-white bg-white flex items-center justify-center">
            {/* Inner Pink Circle */}
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