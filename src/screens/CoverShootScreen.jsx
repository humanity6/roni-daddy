import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  Plus,
  Minus,
  RefreshCw
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const CoverShootScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, uploadedImage } = location.state || {}

  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 2 })
  const [image, setImage] = useState(uploadedImage || null)

  // Transform helpers
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 3) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 1) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

  const handleGenerate = () => {
    navigate('/ai-regenerate', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage: image,
        transform
      }
    })
  }

  const handleBack = () => navigate(-1)

  return (
    <div className="screen-container">
      <PastelBlobs />

      {/* Back Arrow */}
      <button
        onClick={handleBack}
        className="absolute top-4 left-4 w-12 h-12 rounded-full bg-white border-4 border-pink-400 flex items-center justify-center shadow-lg active:scale-95 transition-transform z-20"
      >
        <ArrowLeft size={20} className="text-pink-400" />
      </button>

      <div className="relative z-10 flex flex-col items-center px-6 mt-2">
        {/* Phone preview */}
        <div className="relative w-72 h-[480px] mb-4">
          <div className="phone-case-content">
            {image && (
              <img
                src={image}
                alt="Uploaded"
                className="phone-case-image"
                style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
              />
            )}
          </div>
          <div className="absolute inset-0 pointer-events-none">
            <img src="/phone-template.png" alt="template" className="w-full h-full object-contain" />
          </div>
        </div>

        {/* Control row */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[
            { icon: Minus, action: zoomOut },
            { icon: Plus, action: zoomIn },
            { icon: RefreshCw, action: resetTransform },
            { icon: ArrowRight, action: moveRight },
            { icon: ArrowLeft, action: moveLeft },
            { icon: ArrowDown, action: moveDown },
            { icon: ArrowUp, action: moveUp }
          ].map(({ icon: Icon, action }, idx) => (
            <button
              key={idx}
              onClick={action}
              disabled={!image}
              className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-all ${image ? 'bg-green-100 hover:bg-green-200' : 'bg-gray-100 cursor-not-allowed'}`}
            >
              <Icon size={20} className={image ? 'text-gray-700' : 'text-gray-400'} />
            </button>
          ))}
        </div>

        {/* Generate Cover Shot row */}
        <div className="flex items-center w-full max-w-xs mb-3">
          <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow active:scale-95 transition-transform">
            <ArrowLeft size={20} className="text-gray-600" />
          </button>
          <button
            onClick={handleGenerate}
            disabled={!image}
            className={`flex-1 mx-2 rounded-full py-2 text-sm font-bold shadow active:scale-95 transition-all bg-blue-100 border-2 border-black text-black ${image ? '' : 'opacity-40 cursor-not-allowed'}`}
          >
            Generate Cover Shot
          </button>
          <button className="flex-shrink-0 w-10 h-10 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow active:scale-95 transition-transform">
            <ArrowRight size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Reset Inputs */}
        <button
          onClick={() => {
            setImage(null)
            resetTransform()
          }}
          disabled={!image}
          className={`mb-6 bg-green-200 text-gray-800 font-medium py-2 px-10 rounded-full active:scale-95 transition-transform shadow ${image ? '' : 'opacity-40 cursor-not-allowed'}`}
        >
          Reset Inputs
        </button>
      </div>

      {/* Bottom Generate ring */}
      <div className="relative z-10 pb-8 flex justify-center">
        <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
          <div className="rounded-full bg-white p-[6px]">
            <button
              onClick={handleGenerate}
              disabled={!image}
              className={`w-20 h-20 rounded-full flex items-center justify-center font-semibold transition-all bg-pink-400 text-white ${image ? '' : 'opacity-40 cursor-not-allowed'}`}
            >
              Generate
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CoverShootScreen 