import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Type, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RefreshCw, ArrowRight as ArrowForward, ArrowUp, ArrowDown } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import CircleSubmitButton from '../components/CircleSubmitButton'
import { fonts as availableFonts } from '../utils/fontManager'
import { useAppState } from '../contexts/AppStateContext'
import { composeFinalImage } from '../utils/finalImageComposer'

const BackgroundColorSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: appState } = useAppState()

  // First extract location state to get deviceIdFromState
  const { 
    brand, 
    model, 
    color, 
    template, 
    uploadedImage, 
    uploadedImages, 
    imageTransforms: initialImageTransforms, 
    inputText, 
    selectedFont, 
    fontSize, 
    textPosition, 
    transform: initialTransform, 
    stripCount,
    selectedTextColor,
    selectedModelData,
    deviceId: deviceIdFromState
  } = location.state || {}

  // Extract device_id (needed later on PaymentScreen)
  const currentUrl = window.location.href
  const urlParams = new URLSearchParams(window.location.search)
  const deviceIdMatch = currentUrl.match(/device_id=([^&]+)/)
  const deviceIdFromUrl = urlParams.get('device_id') || (deviceIdMatch ? deviceIdMatch[1] : null)
  const deviceId = deviceIdFromState || appState?.vendingMachineSession?.deviceId || deviceIdFromUrl || null

  // Maintain local copy of image transforms for live editing
  const [imageTransforms, setImageTransforms] = useState(initialImageTransforms || (uploadedImages ? uploadedImages.map(() => ({ x: 0, y: 0, scale: 1 })) : []))

  // We'll edit only the first image for now (or single image template)
  const activeIdx = 0

  const hasImage = uploadedImages && uploadedImages[activeIdx]

  const updateTransform = (delta) => {
    setImageTransforms((prev) => {
      const next = [...prev]
      const current = next[activeIdx] || { x: 0, y: 0, scale: 1 }
      next[activeIdx] = { ...current, ...delta }
      return next
    })
  }

  // Control handlers
  const moveLeft = () => hasImage && updateTransform({ x: Math.max(-100, (imageTransforms[activeIdx]?.x || 0) - 10) })
  const moveRight = () => hasImage && updateTransform({ x: Math.min(100, (imageTransforms[activeIdx]?.x || 0) + 10) })
  const moveUp = () => hasImage && updateTransform({ y: Math.max(-100, (imageTransforms[activeIdx]?.y || 0) - 10) })
  const moveDown = () => hasImage && updateTransform({ y: Math.min(100, (imageTransforms[activeIdx]?.y || 0) + 10) })
  const zoomInImg = () => hasImage && updateTransform({ scale: Math.min(5, (imageTransforms[activeIdx]?.scale || 1) + 0.2) })
  const zoomOutImg = () => hasImage && updateTransform({ scale: Math.max(0.1, (imageTransforms[activeIdx]?.scale || 1) - 0.2) })
  const resetTransform = () => hasImage && updateTransform({ x: 0, y: 0, scale: 1 })

  const [selectedBackgroundColor, setSelectedBackgroundColor] = useState('#ffffff')

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
        textPosition,
        transform: initialTransform,
        stripCount,
        selectedTextColor,
        selectedModelData,
        deviceId
      } 
    })
  }

  const handleNext = async () => {
    try {
      console.log('🔄 Composing and uploading final image...')
      
      // Compose the final image with all customizations
      const finalImageData = await composeFinalImage({
        template,
        uploadedImages,
        uploadedImage,
        imageTransforms,
        inputText,
        selectedFont,
        fontSize,
        selectedTextColor,
        selectedBackgroundColor,
        textPosition,
        transform: initialTransform
      })
      
      console.log('✅ Final image composed successfully')
      
      // Upload final composed image to server
      const uploadResult = await uploadFinalImage(finalImageData, template)
      
      let finalImageUrl = finalImageData // Fallback to local blob URL
      let imageSessionId = null
      
      if (uploadResult && uploadResult.success) {
        console.log('✅ Final image uploaded successfully')
        console.log('📄 Public URL:', uploadResult.public_url)
        finalImageUrl = uploadResult.public_url // Use the permanent URL
        imageSessionId = uploadResult.session_id
      } else {
        console.warn('⚠️ Final image upload failed, continuing with local image')
      }
      
      // Preserve original query parameters (keeps device_id & session data in URL for refresh safety)
      const search = window.location.search || ''
      navigate('/payment' + search, {
        state: {
          designImage: finalImageUrl, // Use permanent URL if available, fallback to blob URL
          finalImagePublicUrl: uploadResult?.public_url, // Store separately for Chinese API
          imageSessionId: imageSessionId, // For tracking
          uploadedImages,
          imageTransforms,
          inputText,
          selectedFont,
          fontSize,
          selectedTextColor,
          selectedBackgroundColor,
          textPosition,
          transform: initialTransform,
          template,
          stripCount,
          deviceId // pass through explicitly so PaymentScreen can still read it even if query params are lost
        }
      })
      
    } catch (error) {
      console.error('❌ Error creating final image:', error)
      // Fallback to original behavior if composition fails
      const search = window.location.search || ''
      navigate('/payment' + search, {
        state: {
          designImage: uploadedImage, // Fallback to original image
          uploadedImages,
          imageTransforms,
          inputText,
          selectedFont,
          fontSize,
          selectedTextColor,
          selectedBackgroundColor,
          textPosition,
          transform: initialTransform,
          template,
          stripCount,
          deviceId
        }
      })
    }
  }

  const uploadFinalImage = async (finalImageData, template) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/images/upload-final`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          template_id: template?.id || 'classic',
          final_image_data: finalImageData,
          metadata: JSON.stringify({
            inputText,
            selectedFont,
            fontSize,
            selectedTextColor,
            selectedBackgroundColor,
            textPosition,
            uploadTimestamp: new Date().toISOString()
          })
        })
      })
      
      if (!response.ok) {
        console.error('Final image upload failed:', response.status, await response.text())
        return false
      }
      
      const result = await response.json()
      console.log('Final image upload result:', result)
      
      // Return both success status and the image data for tracking
      return {
        success: true,
        public_url: result.public_url,
        filename: result.filename,
        session_id: result.session_id
      }
      
    } catch (error) {
      console.error('Error uploading final image:', error)
      return false
    }
  }

  const getPreviewStyle = () => {
    const fonts = availableFonts
    return {
      fontFamily: fonts.find(f => f.name === selectedFont)?.style || 'Arial, sans-serif',
      fontSize: `${fontSize}px`,
      color: selectedTextColor || '#ffffff',
      whiteSpace: 'nowrap',
      fontWeight: '500',
      lineHeight: '1.2'
    }
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
        <h1 className="text-lg font-semibold text-gray-800">background colour</h1>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          {template?.id?.startsWith('film-strip') ? (
            <div className="relative w-[525px] h-[525px] overflow-hidden pointer-events-none">
              {/* Background color layer for film strip - using proper film strip constraints */}
              <div
                className="absolute z-5"
                style={{ 
                  backgroundColor: selectedBackgroundColor,
                  top: '2%',
                  bottom: '2%',
                  left: '28%',
                  right: '28%',
                  borderRadius: '16px'
                }}
              ></div>
              
              {/* Images container */}
              <div
                className="absolute inset-0 flex flex-col justify-center items-center z-10"
                style={{ 
                  paddingTop:'0px', 
                  paddingBottom:'0px', 
                  paddingLeft:'180px', 
                  paddingRight:'180px'
                }}
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
              
              {/* Film strip case overlay */}
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
                  <p style={getPreviewStyle()}>{inputText}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="relative w-72 h-[480px]">
              {/* Background color layer - positioned to match phone case content area */}
              <div 
                className="absolute z-5"
                style={{
                  backgroundColor: selectedBackgroundColor,
                  position: 'absolute',
                  top: '1px',
                  left: '8%',
                  right: '8%',
                  bottom: '1px',
                  borderRadius: '42px',
                  overflow: 'hidden'
                }}
              ></div>
              
              {/* Phone case border - separate decorative element */}
              <div className="phone-case-border absolute z-8"></div>
              
              {/* User's uploaded image content - above background but below text */}
              <div 
                className="relative z-10"
                style={{
                  position: 'absolute',
                  top: '1px',
                  left: '8%',
                  right: '8%',
                  bottom: '1px',
                  borderRadius: '42px',
                  overflow: 'hidden'
                }}
              >
                {uploadedImages && uploadedImages.length > 0 ? (
                  // Multi-image layouts
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
                    style={imageTransforms && imageTransforms[0] ? { transform: `translate(${imageTransforms[0].x}%, ${imageTransforms[0].y}%) scale(${imageTransforms[0].scale})`, transformOrigin: 'center center' } : initialTransform ? { transform: `translate(${initialTransform.x}%, ${initialTransform.y}%) scale(${initialTransform.scale})`, transformOrigin: 'center center' } : undefined}
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

              {/* Text overlay preview - highest layer for user content */}
              {inputText && (
                <div className="absolute z-15" style={getTextStyle()}>
                  <p style={getPreviewStyle()}>{inputText}</p>
                </div>
              )}
              
              {/* Phone Template Overlay - decorative elements above everything */}
              <div className="absolute inset-0 z-20">
                <img 
                  src="/phone-template.png" 
                  alt="Phone template overlay" 
                  className="w-full h-full object-contain pointer-events-none"
                />
              </div>
            </div>
          )}
        </div>

        {/* Selection Label with Arrows */}
        <div className="w-full max-w-xs mb-6 flex items-center justify-between">
          {/* Left Arrow */}
          <button
            onClick={handleBack}
            className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform"
          >
            <ChevronLeft size={20} className="text-gray-600" />
          </button>

          {/* Label Pill */}
          <div className="bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-md text-sm font-medium text-gray-800 border-2 border-black">
            Background Color
          </div>

          {/* Right Arrow */}
          <button
            onClick={handleNext}
            className="w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform"
          >
            <ChevronRight size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Control Buttons Row (green squares) */}
        {uploadedImages && uploadedImages.length > 0 && (
          <div className="flex items-center justify-center space-x-3 mb-6">
            <button onClick={zoomOutImg} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ZoomOut size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={zoomInImg} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ZoomIn size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={resetTransform} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <RefreshCw size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={moveRight} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ArrowForward size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={moveLeft} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ArrowLeft size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={moveDown} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ArrowDown size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
            <button onClick={moveUp} disabled={!hasImage} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${hasImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}>
              <ArrowUp size={20} className={hasImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
          </div>
        )}

        {/* Horizontal Color Slider */}
        <div className="w-full mb-8">
          <div className="relative">
            <div className="color-slider flex space-x-3 px-4 py-2 overflow-x-auto">
              {colors.map((colorOption, index) => (
                <button
                  key={colorOption.value}
                  onClick={() => setSelectedBackgroundColor(colorOption.value)}
                  className={`
                    color-option w-10 h-10 rounded-full border-2 transition-all duration-300 shadow-lg
                    ${colorOption.bg}
                    ${selectedBackgroundColor === colorOption.value 
                      ? 'border-pink-400 scale-125 shadow-xl' 
                      : `${colorOption.border} hover:scale-110 active:scale-95`}
                  `}
                  title={colorOption.name}
                  style={{
                    minWidth: '2.5rem',
                    marginRight: index === colors.length - 1 ? '1rem' : '0'
                  }}
                />
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

export default BackgroundColorSelectionScreen 