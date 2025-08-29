import { useState, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  ArrowLeft, 
  ArrowRight, 
  Upload, 
  ZoomIn, 
  ZoomOut, 
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import { enhanceImage } from '../utils/imageEnhancer'
import { useAppState } from '../contexts/AppStateContext'

const PhonePreviewScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: appState } = useAppState()
  const { brand, model, color, template, selectedModelData, deviceId } = location.state || {}
  
  const [uploadedImage, setUploadedImage] = useState(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 2 })

  // Calculate model-specific dimensions from Chinese API data (memoized to prevent excessive logging)
  const modelDimensions = useMemo(() => {
    const modelData = selectedModelData || appState.modelData
    
    if (modelData?.width && modelData?.height) {
      // Convert millimeters to pixels at 96 DPI (standard web resolution)
      // 1 inch = 25.4 mm, 96 pixels per inch
      const mmToPixels = (mm) => (mm / 25.4) * 96
      
      const widthPx = mmToPixels(modelData.width)
      const heightPx = mmToPixels(modelData.height)
      
      // Apply same scaling factors as before to maintain UI proportions
      const containerWidth = widthPx * 0.84  // 8% margins on each side
      const containerHeight = heightPx * 0.98 // 1px margins top/bottom
      
      // Log once when dimensions are calculated
      console.log(`📐 Using model-specific dimensions: ${modelData.width}mm x ${modelData.height}mm = ${widthPx.toFixed(1)}px x ${heightPx.toFixed(1)}px`)
      return { containerWidth, containerHeight, widthPx, heightPx }
    } else {
      // Chinese API data should be available - log error if missing
      console.error('❌ Chinese API dimensions missing from modelData:', modelData)
      console.error('❌ This will cause image cropping and incorrect preview proportions')
      
      // Use minimal fallback for debugging only
      const containerWidth = 288 // w-72 in Tailwind
      const containerHeight = 480 // h-[480px] in Tailwind  
      return { containerWidth, containerHeight, widthPx: 288, heightPx: 480 }
    }
  }, [selectedModelData, appState.modelData])

  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    if (file) {
      try {
        const processed = await enhanceImage(file)
        setUploadedImage(processed)
        
        // Calculate auto-fit scale based on image dimensions and model-specific phone case size
        const img = new Image()
        img.onload = () => {
          const { containerWidth, containerHeight } = modelDimensions
          
          const scaleX = containerWidth / img.width
          const scaleY = containerHeight / img.height
          
          // For object-fit: contain, use the smaller scale to ensure no cropping
          const autoScale = Math.min(scaleX, scaleY)
          
          // Scale up slightly to fill more space while still preventing cropping
          const finalScale = Math.max(autoScale * 3, 1.0)
          
          setTransform({ x: 0, y: 0, scale: finalScale })
        }
        img.src = processed
      } catch (err) {
        console.error('Image processing failed', err)
      }
    }
  }

  const handleBack = () => {
    navigate('/template-selection', { 
      state: { 
        brand, 
        model, 
        color,
        selectedModelData,
        deviceId
      } 
    })
  }

  const handleNext = () => {
    if (template?.id === 'retro-remix') {
      navigate('/retro-remix', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id === 'funny-toon') {
      navigate('/funny-toon', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id === 'footy-fan') {
      navigate('/footy-fan', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id === 'glitch-pro') {
      navigate('/glitch', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id === 'cover-shoot') {
      navigate('/cover-shoot', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    } else if (template?.id?.startsWith('film-strip')) {
      navigate('/film-strip', {
        state: {
          brand,
          model,
          color,
          template,
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
          selectedModelData,
          deviceId
        }
      })
    } else {
      navigate('/text-input', {
        state: {
          brand,
          model,
          color,
          template,
          uploadedImage,
          transform,
          selectedModelData,
          deviceId
        }
      })
    }
  }

  const resetInputs = () => {
    setUploadedImage(null)
    resetTransform()
  }

  const getColorClass = (colorId) => {
    const colorMap = {
      black: 'bg-gray-900',
      white: 'bg-gray-100',
      blue: 'bg-blue-500',
      pink: 'bg-pink-400',
      green: 'bg-green-600'
    }
    return colorMap[colorId] || 'bg-gray-900'
  }

  /* --------------------------------------------------------------------
   * IMAGE TRANSFORM HELPERS
   * ------------------------------------------------------------------*/
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 1 })

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        {/* Back Arrow – outlined pastel-pink circle */}
        <button 
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-pink-400" />
        </button>
        <div className="w-12 h-12"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          {/* Phone Case Container - Dynamic dimensions based on Chinese API model data */}
          <div 
            className="relative"
            style={{
              width: `${Math.min(modelDimensions.containerWidth, 288)}px`, // Cap at 288px (w-72) for UI constraints
              height: `${Math.min(modelDimensions.containerHeight, 480)}px`, // Cap at 480px for UI constraints
              aspectRatio: `${modelDimensions.containerWidth} / ${modelDimensions.containerHeight}`
            }}
          >
            
            {/* User's uploaded image - positioned to fit exactly within phone template boundaries */}
            <div className="phone-case-content">
              {uploadedImage ? (
                <img 
                  src={uploadedImage} 
                  alt="Uploaded design" 
                  className="phone-case-image-contain"
                  style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors">
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Click to upload image</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Phone Template Overlay - camera holes and edges on top */}
            <div className="absolute inset-0">
              <img 
                src="/phone-template.png" 
                alt="Phone template overlay" 
                className="w-full h-full object-contain pointer-events-none"
              />
            </div>
            
            {/* Hidden file input and clickable overlay for upload */}
            {!uploadedImage && (
              <div className="absolute inset-0 z-10">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="phone-upload-input"
                />
                <label 
                  htmlFor="phone-upload-input"
                  className="w-full h-full block cursor-pointer"
                />
              </div>
            )}
          </div>
        </div>

        {/* Control Buttons Row – pastel-green squares */}
        <div className="flex items-center justify-center gap-2.5 mb-6 px-4">
          {[
            { Icon: ZoomOut, action: zoomOut },
            { Icon: ZoomIn, action: zoomIn },
            { Icon: RefreshCw, action: resetTransform },
            { Icon: ArrowRight, action: moveRight },
            { Icon: ArrowLeft, action: moveLeft },
            { Icon: ArrowDown, action: moveDown },
            { Icon: ArrowUp, action: moveUp },
          ].map(({ Icon, action }, idx) => (
            <button
              key={idx}
              onClick={action}
              disabled={!uploadedImage}
              className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${uploadedImage ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
            >
              <Icon size={20} className={uploadedImage ? 'text-gray-700' : 'text-gray-400'} />
            </button>
          ))}
        </div>

        {/* Navigation Arrows below – square white buttons */}
        <div className="flex items-center justify-between w-full max-w-xs mb-6 px-2">
          <button 
            onClick={handleBack}
            className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform"
          >
            <ChevronLeft size={24} className="text-gray-600" />
          </button>
          <button 
            onClick={handleNext}
            disabled={!uploadedImage && !template?.id?.startsWith('film-strip') && !(template?.imageCount && template.imageCount > 1)}
            className={`w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform ${
              uploadedImage || template?.id?.startsWith('film-strip') || (template?.imageCount && template.imageCount > 1)
                ? 'bg-white cursor-pointer'
                : 'bg-gray-100 cursor-not-allowed'
            }`}
          >
            <ChevronRight size={24} className={`${
              uploadedImage || template?.id?.startsWith('film-strip') || (template?.imageCount && template.imageCount > 1)
                ? 'text-gray-600'
                : 'text-gray-400'
            }`} />
          </button>
        </div>

        {/* Upload Image Button */}
        <div className="w-full max-w-xs mb-4">
          <label className="block">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <div className="w-full bg-blue-100 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform cursor-pointer shadow-lg">
              <div className="flex items-center justify-center space-x-2">
                <Upload size={20} />
                <span>Upload Image</span>
              </div>
            </div>
          </label>
        </div>

        {/* Reset Inputs Button */}
        {uploadedImage && (
          <button 
            onClick={resetInputs}
            className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
          >
            Reset Inputs
          </button>
        )}
      </div>

      {/* Submit Button */}
      <div className="relative z-10 p-6 flex justify-center">
        {(template?.id?.startsWith('film-strip') || (template?.imageCount && template.imageCount > 1) || uploadedImage) ? (
          /* Outer Pink Ring - only show when ready to submit */
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
        ) : (
          /* Simple grey button when not ready to submit */
          <button 
            disabled={true}
            className="w-16 h-16 rounded-full bg-gray-300 text-white cursor-not-allowed flex items-center justify-center shadow-xl"
          >
            <span className="font-semibold text-xs">Submit</span>
          </button>
        )}
      </div>
    </div>
  )
}

export default PhonePreviewScreen 