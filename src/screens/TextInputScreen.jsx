import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Type, X, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const TextInputScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage, uploadedImages, transform: initialTransform, imageTransforms, inputText: initialText, textPosition: initialPosition } = location.state || {}
  const { stripCount } = location.state || {}
  
  const [inputText, setInputText] = useState(initialText || '')
  const [textPosition, setTextPosition] = useState(initialPosition || { x: 50, y: 50 }) // percentage from top-left

  const handleBack = () => {
    if (template?.id?.startsWith('film-strip')) {
      navigate('/film-strip-upload', {
        state: {
          brand,
          model,
          color,
          template,
          stripCount
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
    } else {
      navigate('/phone-preview', { 
        state: { 
          brand, 
          model, 
          color, 
          template,
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
        textPosition
      } 
    })
  }

  const resetInput = () => {
    setInputText('')
    setTextPosition({ x: 50, y: 50 })
  }

  // Text positioning functions
  const moveTextLeft = () => {
    setTextPosition(prev => ({ ...prev, x: Math.max(0, prev.x - 5) }))
  }

  const moveTextRight = () => {
    setTextPosition(prev => ({ ...prev, x: Math.min(100, prev.x + 5) }))
  }

  const moveTextUp = () => {
    setTextPosition(prev => ({ ...prev, y: Math.max(0, prev.y - 5) }))
  }

  const moveTextDown = () => {
    setTextPosition(prev => ({ ...prev, y: Math.min(100, prev.y + 5) }))
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
            <div className="relative w-[525px] h-[525px] overflow-hidden">
              <div
                className="absolute inset-0 flex flex-col justify-center items-center z-10"
                style={{ paddingTop:'0px', paddingBottom:'0px', paddingLeft:'180px', paddingRight:'179px'}}
              >
                {uploadedImages && uploadedImages.map((img, idx) => (
                  <div
                    key={idx}
                    className="w-full overflow-hidden border-t-[8px] border-b-[8px] border-black"
                    style={{ height: `${100 / (stripCount || 3) - 2}%` }}
                  >
                    <img 
                      src={img} 
                      alt={`design ${idx+1}`} 
                      className="w-full h-full object-cover"
                      style={{
                        objectPosition: imageTransforms && imageTransforms[idx] 
                          ? `${imageTransforms[idx].x}% ${imageTransforms[idx].y}%`
                          : '50% 50%',
                        transform: imageTransforms && imageTransforms[idx] 
                          ? `scale(${imageTransforms[idx].scale})`
                          : 'scale(1)'
                      }}
                    />
                  </div>
                ))}
              </div>
              <div className="absolute inset-0 z-20 pointer-events-none">
                <img src="/filmstrip-case.png" alt="Film strip case" className="w-full h-full object-contain" />
              </div>
            </div>
          ) : (
            <div className="relative w-72 h-[480px]">
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
                                objectPosition: imageTransforms && imageTransforms[idx] 
                                  ? `${imageTransforms[idx].x}% ${imageTransforms[idx].y}%`
                                  : '50% 50%',
                                transform: imageTransforms && imageTransforms[idx] 
                                  ? `scale(${imageTransforms[idx].scale})`
                                  : 'scale(1)'
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
                                objectPosition: imageTransforms && imageTransforms[idx] 
                                  ? `${imageTransforms[idx].x}% ${imageTransforms[idx].y}%`
                                  : '50% 50%',
                                transform: imageTransforms && imageTransforms[idx] 
                                  ? `scale(${imageTransforms[idx].scale})`
                                  : 'scale(1)'
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
                    className="phone-case-image"
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
                  <div className="bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm whitespace-nowrap">
                    <p className="text-lg font-medium">{inputText}</p>
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
        <div className="w-24 h-24 rounded-full border-4 border-pink-400 flex items-center justify-center shadow-xl">
          {/* Updated: thicker outer ring */}
          <div className="w-20 h-20 rounded-full border-2 border-white bg-white flex items-center justify-center">
            {/* Inner Pink Circle */}
            <button 
              onClick={handleNext}
              className="w-16 h-16 rounded-full bg-pink-500 text-white flex items-center justify-center active:scale-95 transition-transform"
            >
              <span className="font-semibold text-sm">Submit</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TextInputScreen 