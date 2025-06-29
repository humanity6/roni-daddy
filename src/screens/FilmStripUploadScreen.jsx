import { useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  Upload,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
// Using public filmstrip case image

const FilmStripUploadScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, stripCount } = location.state || {}
  const totalSlots = stripCount || 3

  const [uploadedImages, setUploadedImages] = useState(Array(totalSlots).fill(null))
  const [currentIdx, setCurrentIdx] = useState(0)
  const fileInputRef = useRef(null)
  // Per-image transform: { x: percentage, y: percentage, scale }
  const defaultTransform = { x: 50, y: 50, scale: 1 }
  const [imageTransforms, setImageTransforms] = useState(
    Array(totalSlots).fill(defaultTransform)
  )
  const [imageOrientations, setImageOrientations] = useState(
    Array(totalSlots).fill('unknown') // 'portrait' | 'landscape'
  )

  const handleBack = () => {
    navigate('/film-strip', {
      state: { brand, model, color, template }
    })
  }

  const openFilePicker = () => {
    fileInputRef.current?.click()
  }

  const handleFilesSelected = (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    console.log(`Uploading image for slot ${currentIdx}:`, file.name)
    
    const reader = new FileReader()
    reader.onload = (ev) => {
      console.log(`Image loaded for slot ${currentIdx}, data length:`, ev.target.result.length)
      
      setUploadedImages((prev) => {
        const next = [...prev]
        next[currentIdx] = ev.target.result
        console.log(`Updated images array:`, next.map((img, idx) => img ? `Slot ${idx}: Image loaded` : `Slot ${idx}: Empty`))
        return next
      })
      
      // Auto-advance to next empty slot if available
      const nextEmptySlot = uploadedImages.findIndex((img, idx) => !img && idx > currentIdx)
      if (nextEmptySlot !== -1) {
        setCurrentIdx(nextEmptySlot)
      }
      
      // Reset transform for this slot
      setImageTransforms((prev) => {
        const next = [...prev]
        next[currentIdx] = { ...defaultTransform }
        return next
      })

      // Determine orientation for this image
      const probe = new Image()
      probe.onload = () => {
        setImageOrientations((prev) => {
          const next = [...prev]
          next[currentIdx] = probe.width >= probe.height ? 'landscape' : 'portrait'
          return next
        })
      }
      probe.src = ev.target.result
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  const goPrev = () => setCurrentIdx((prev) => Math.max(0, prev - 1))
  const goNext = () => setCurrentIdx((prev) => Math.min(totalSlots - 1, prev + 1))

  const handleNext = () => {
    navigate('/text-input', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImages,
        imageTransforms,
        stripCount
      }
    })
  }

  const resetImages = () => setUploadedImages(Array(totalSlots).fill(null))

  const filledCount = uploadedImages.filter((img) => img).length
  const canSubmit = filledCount === totalSlots

  // ----- Crop / Move helpers -----
  const clamp = (val, min, max) => Math.max(min, Math.min(max, val))

  const updateTransform = (idx, updater) => {
    setImageTransforms((prev) => {
      const next = [...prev]
      const current = next[idx]
      const changes = typeof updater === 'function' ? updater(current) : updater
      const updated = { ...current, ...changes }
      // Clamp values to keep image inside padding
      updated.x = clamp(updated.x, 0, 100)
      updated.y = clamp(updated.y, 0, 100)
      updated.scale = clamp(updated.scale, 1, 3)
      next[idx] = updated
      return next
    })
  }

  const moveUp = () => updateTransform(currentIdx, (t) => ({ y: t.y - 5 }))
  const moveDown = () => updateTransform(currentIdx, (t) => ({ y: t.y + 5 }))
  const moveLeft = () => {
    const orient = imageOrientations[currentIdx]
    if (orient === 'landscape') {
      updateTransform(currentIdx, (t) => ({ x: t.x - 10 }))
    } else {
      updateTransform(currentIdx, (t) => ({ y: t.y - 10 }))
    }
  }
  const moveRight = () => {
    const orient = imageOrientations[currentIdx]
    if (orient === 'landscape') {
      updateTransform(currentIdx, (t) => ({ x: t.x + 10 }))
    } else {
      updateTransform(currentIdx, (t) => ({ y: t.y + 10 }))
    }
  }
  const zoomIn = () => updateTransform(currentIdx, (t) => ({ scale: t.scale + 0.1 }))
  const zoomOut = () => updateTransform(currentIdx, (t) => ({ scale: t.scale - 0.1 }))
  const resetTransform = () => updateTransform(currentIdx, defaultTransform)

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
        {/* Spacer for symmetry */}
        <div className="flex-1"></div>
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-start px-6 mt-4">
        <div className="relative mb-6">
          <div className="relative w-[525px] h-[525px] overflow-hidden">
            {/* Images container - middle z-index */}
            <div className="absolute inset-0 flex flex-col justify-center items-center z-10"style={{
  paddingTop: '0px',
  paddingBottom: '0px', 
  paddingLeft: '180px',
  paddingRight: '179px'
}}>
              {Array.from({ length: totalSlots }).map((_, idx) => (
                <div 
                  key={idx}
                  className="w-full overflow-hidden rounded-sm transition-all duration-300 border-t-[8px] border-b-[8px] border-black"
                  style={{
                    height: `${100 / totalSlots - 2}%`,
                  }}
                >
                  {uploadedImages[idx] ? (
                    <img
                      src={uploadedImages[idx]}
                      alt={`Photo ${idx + 1}`}
                      className="w-full h-full object-cover"
                      style={{
                        objectPosition: `${imageTransforms[idx].x}% ${imageTransforms[idx].y}%`,
                        transform: `scale(${imageTransforms[idx].scale})`
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <div className="flex flex-col items-center text-center">
                        <Upload size={20} className={currentIdx === idx ? 'text-blue-500' : 'text-gray-400'} />
                        {currentIdx === idx && (
                          <p className="text-xs mt-1 text-blue-600 font-medium">Current</p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Current selection indicator removed per design update */}
                </div>
              ))}
            </div>

            {/* Phone case overlay - highest z-index with transparent areas */}
            <div className="absolute inset-0 z-20 pointer-events-none">
              <img
                src="/filmstrip-case.png"
                alt="Film strip phone case"
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        </div>

        {/* Control Buttons Row (optional placeholders) */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          <button onClick={zoomOut} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ZoomOut size={20} className="text-gray-700" />
          </button>
          <button onClick={zoomIn} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ZoomIn size={20} className="text-gray-700" />
          </button>
          <button onClick={resetTransform} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <RefreshCw size={20} className="text-gray-700" />
          </button>
          <button onClick={moveLeft} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ArrowLeft size={20} className="text-gray-700" />
          </button>
          <button onClick={moveRight} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ArrowRight size={20} className="text-gray-700" />
          </button>
          <button onClick={moveDown} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ArrowDown size={20} className="text-gray-700" />
          </button>
          <button onClick={moveUp} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ArrowUp size={20} className="text-gray-700" />
          </button>
        </div>

        {/* Navigation Arrows */}
        <div className="flex items-center justify-between w-full max-w-xs mb-4 px-2">
          <button onClick={goPrev} disabled={currentIdx === 0} className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform disabled:opacity-40">
            <ArrowLeft size={24} className="text-gray-600" />
          </button>
          <button onClick={goNext} disabled={currentIdx === totalSlots - 1} className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md active:scale-95 transition-transform disabled:opacity-40">
            <ArrowRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Upload button */}
        <div className="w-full max-w-xs mb-4">
          <button onClick={openFilePicker} className="w-full bg-blue-100 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <Upload size={20} />
              <span>Upload Image {currentIdx + 1} of {totalSlots}{uploadedImages[currentIdx] ? ' (Replace)' : ''}</span>
            </div>
          </button>
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            className="hidden"
            onChange={handleFilesSelected}
          />
        </div>

        {/* Show current selection info */}
        <div className="text-center text-sm text-gray-600 mb-2">
          Selected: Image {currentIdx + 1} of {totalSlots}
          {uploadedImages[currentIdx] && <span className="text-green-600"> ✓</span>}
        </div>

        {/* Progress indicator */}
        <div className="w-full max-w-xs mb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Progress</span>
            <span>{filledCount}/{totalSlots}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(filledCount / totalSlots) * 100}%` }}
            ></div>
          </div>
        </div>

        {filledCount > 0 && (
          <button onClick={resetImages} className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4">
            Reset Images
          </button>
        )}
      </div>

      {/* Submit */}
      <div className="relative z-10 p-6 flex justify-center">
        {canSubmit ? (
          <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
            <div className="rounded-full bg-white p-[6px]">
              <button onClick={handleNext} className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold">
                <span className="text-sm">Submit</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="rounded-full bg-pink-400/50 p-[6px] shadow-xl">
            <div className="rounded-full bg-white p-[6px]">
              <button disabled className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-300 text-white font-semibold cursor-not-allowed">
                <span className="text-sm">Submit</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FilmStripUploadScreen 