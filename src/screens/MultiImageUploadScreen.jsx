import { useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Upload, RefreshCw, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, ArrowRight as ArrowForward, ArrowUp, ArrowDown, ArrowLeft as ArrowBack } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const MultiImageUploadScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template } = location.state || {}
  const requiredCount = template?.imageCount || 2

  // Each slot keeps src + transform data
  const [images, setImages] = useState(
    Array(requiredCount).fill(null).map(() => ({ src: null, x: 0, y: 0, scale: 2 }))
  )
  const [currentIdx, setCurrentIdx] = useState(0)
  const fileInputRef = useRef(null)

  const handleBack = () => {
    navigate('/template-selection', {
      state: { brand, model, color }
    })
  }

  // Open picker for current slot
  const openPickerForCurrent = () => {
    fileInputRef.current?.click()
  }

  const handleFilesSelected = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (ev) => {
      setImages((prev) => {
        const next = [...prev]
        next[currentIdx] = { ...next[currentIdx], src: ev.target.result, scale: 2 }
        return next
      })
      // Stay on current image so user can crop/adjust before moving to next
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  // Helper to update transform fields
  const updateCurrentImage = (delta) => {
    setImages((prev) => {
      const next = [...prev]
      const img = next[currentIdx]
      next[currentIdx] = { ...img, ...delta }
      return next
    })
  }

  // Control handlers - work on currently selected image OR the image that was just uploaded
  const getActiveImageIndex = () => {
    // Find the most recently uploaded image or current selection
    return currentIdx
  }

  const moveLeft = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Moving left, current x:', images[activeIdx].x, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, x: Math.max(-100, img.x - 10) }
        return next
      })
    }
  }
  const moveRight = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Moving right, current x:', images[activeIdx].x, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, x: Math.min(100, img.x + 10) }
        return next
      })
    }
  }
  const moveUp = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Moving up, current y:', images[activeIdx].y, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, y: Math.max(-100, img.y - 10) }
        return next
      })
    }
  }
  const moveDown = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Moving down, current y:', images[activeIdx].y, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, y: Math.min(100, img.y + 10) }
        return next
      })
    }
  }
  const zoomInImg = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Zooming in, current scale:', images[activeIdx].scale, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, scale: Math.min(5, img.scale + 0.2) }
        return next
      })
    }
  }
  const zoomOutImg = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Zooming out, current scale:', images[activeIdx].scale, 'for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        const img = next[activeIdx]
        next[activeIdx] = { ...img, scale: Math.max(0.1, img.scale - 0.2) }
        return next
      })
    }
  }
  const resetTransform = () => {
    const activeIdx = getActiveImageIndex()
    if (images[activeIdx]?.src) {
      console.log('Resetting transform for image', activeIdx)
      setImages((prev) => {
        const next = [...prev]
        next[activeIdx] = { ...next[activeIdx], x: 0, y: 0, scale: 2 }
        return next
      })
    }
  }

  const resetImages = () => setImages(Array(requiredCount).fill(null).map(() => ({ src: null, x: 0, y: 0, scale: 2 })))

  const handleNext = () => {
    navigate('/text-input', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImages: images,
        uploadedImage: images[0] // keep first for backward compat
      }
    })
  }

  const filledCount = images.filter((i) => i.src).length
  const canSubmit = filledCount === requiredCount

  const frameClass = () => {
    switch (requiredCount) {
      case 2:
        return 'w-full h-1/2'
      case 3:
        return 'w-full h-1/3'
      case 4:
        return 'w-1/2 h-1/2'
      default:
        return 'w-full h-1/2'
    }
  }

  const goPrev = () => setCurrentIdx((prev) => Math.max(0, prev - 1))
  const goNext = () => setCurrentIdx((prev) => Math.min(requiredCount - 1, prev + 1))

  return (
    <div className="screen-container">
      <PastelBlobs />

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-pink-400" />
        </button>
        <h2 className="font-cubano text-lg text-gray-800">Upload Images</h2>
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        <div className="relative mb-6">
          {/* Phone mockup */}
          <div className="relative w-72 h-[480px]">
            {/* User image(s) */}
            <div className="phone-case-content">
              {requiredCount === 4 ? (
                <div className="w-full h-full flex flex-wrap">
                  {images.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentIdx(idx)}
                      className={`w-1/2 h-1/2 overflow-hidden border-gray-900 ${
                        idx === 0 ? 'border-t-4 border-l-4 border-r-2 border-b-2' :
                        idx === 1 ? 'border-t-4 border-r-4 border-l-2 border-b-2' :
                        idx === 2 ? 'border-b-4 border-l-4 border-r-2 border-t-2' :
                        'border-b-4 border-r-4 border-l-2 border-t-2'
                      }`}
                      style={{ borderColor: '#0a0a0a' }}
                    >
                      {img.src ? (
                        <div className="w-full h-full overflow-hidden relative bg-gray-100">
                          <img
                            src={img.src}
                            alt={`img-${idx}`}
                            className="absolute w-full h-full object-cover"
                            style={{ 
                              transform: `translate(${img.x}%, ${img.y}%) scale(${img.scale})`,
                              transformOrigin: 'center center'
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-50">
                          <Upload size={24} className="text-gray-400" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="w-full h-full flex flex-col">
                  {images.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentIdx(idx)}
                      className={`flex-1 overflow-hidden border-gray-900 ${
                        idx === 0 ? 'border-t-4 border-l-4 border-r-4 border-b-2' :
                        idx === requiredCount - 1 ? 'border-b-4 border-l-4 border-r-4 border-t-2' :
                        'border-l-4 border-r-4 border-t-2 border-b-2'
                      }`}
                      style={{ borderColor: '#0a0a0a' }}
                    >
                      {img.src ? (
                        <div className="w-full h-full overflow-hidden relative bg-gray-100">
                          <img
                            src={img.src}
                            alt={`img-${idx}`}
                            className="absolute w-full h-full object-cover"
                            style={{ 
                              transform: `translate(${img.x}%, ${img.y}%) scale(${img.scale})`,
                              transformOrigin: 'center center'
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-50">
                          <Upload size={24} className="text-gray-400" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Template overlay */}
            <img
              src="/phone-template.png"
              alt="phone template"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />
          </div>
        </div>

        {/* Control Buttons Row (green squares) */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          <button 
            onClick={zoomOutImg} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ZoomOut size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={zoomInImg} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ZoomIn size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={resetTransform} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <RefreshCw size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={moveRight} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ArrowForward size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={moveLeft} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ArrowBack size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={moveDown} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ArrowDown size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
          <button 
            onClick={moveUp} 
            disabled={!images[getActiveImageIndex()]?.src}
            className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${images[getActiveImageIndex()]?.src ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
          >
            <ArrowUp size={20} className={images[getActiveImageIndex()]?.src ? "text-gray-700" : "text-gray-400"}/>
          </button>
        </div>

        {/* Transform info display */}
        {images[getActiveImageIndex()]?.src && (
          <div className="text-center text-xs text-gray-500 mb-4">
            Editing Image {getActiveImageIndex() + 1} - X: {images[getActiveImageIndex()].x}% | Y: {images[getActiveImageIndex()].y}% | Scale: {images[getActiveImageIndex()].scale.toFixed(1)}x
          </div>
        )}

        {/* Navigation Arrows below */}
        <div className="flex items-center justify-between w-full max-w-xs mb-4 px-2">
          <button onClick={goPrev} disabled={currentIdx === 0} className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform disabled:opacity-40">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>
          <button onClick={goNext} disabled={currentIdx === requiredCount - 1} className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform disabled:opacity-40">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Upload & reset */}
        <div className="w-full max-w-xs space-y-4">
          <button onClick={openPickerForCurrent} className="w-full bg-blue-100 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <Upload size={20} />
              <span>Upload Image {currentIdx + 1}{images[currentIdx]?.src ? ' (Replace)' : ''}</span>
            </div>
          </button>

          {/* Show current selection info */}
          <div className="text-center text-sm text-gray-600">
            Selected: Image {currentIdx + 1} of {requiredCount}
            {images[currentIdx]?.src && <span className="text-green-600"> ✓</span>}
          </div>

          {filledCount > 0 && (
            <button onClick={resetImages} className="w-full bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg">
              Reset Inputs
            </button>
          )}
        </div>

        {/* Hidden file input */}
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          className="hidden"
          onChange={handleFilesSelected}
        />
      </div>

      {/* Submit */}
      <div className="relative z-10 p-6 flex justify-center">
        <button
          disabled={!canSubmit}
          onClick={handleNext}
          className={`w-16 h-16 rounded-full flex items-center justify-center shadow-xl transition-transform active:scale-95 ${canSubmit ? 'bg-pink-400 text-white' : 'bg-gray-300 text-white cursor-not-allowed'}`}
        >
          <span className="text-sm">Submit</span>
        </button>
      </div>
    </div>
  )
}

export default MultiImageUploadScreen 