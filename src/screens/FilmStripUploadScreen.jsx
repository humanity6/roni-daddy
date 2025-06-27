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

const FilmStripUploadScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, template, stripCount } = location.state || {}

  const [uploadedImages, setUploadedImages] = useState([])
  const fileInputRef = useRef(null)

  const handleBack = () => {
    navigate('/film-strip', {
      state: { brand, model, color, template }
    })
  }

  const openFilePicker = () => {
    if (fileInputRef.current) fileInputRef.current.click()
  }

  const handleFilesSelected = (e) => {
    const files = Array.from(e.target.files).slice(0, stripCount)
    const promises = files.map(
      (file) =>
        new Promise((resolve) => {
          const reader = new FileReader()
          reader.onload = (ev) => resolve(ev.target.result)
          reader.readAsDataURL(file)
        })
    )
    Promise.all(promises).then((imgs) => setUploadedImages(imgs))
  }

  const handleNext = () => {
    navigate('/text-input', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImages
      }
    })
  }

  const resetImages = () => setUploadedImages([])

  const canSubmit = uploadedImages.length === stripCount

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
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content relative flex flex-col justify-between p-1">
              {/* Internal film strip edges */}
              <div className="absolute inset-y-0 left-0 w-3 bg-black flex flex-col justify-between py-2">
                {Array.from({ length: 11 }).map((_, i) => (
                  <div key={i} className="w-2 h-2 bg-white mx-auto my-1 rounded-sm"></div>
                ))}
              </div>
              <div className="absolute inset-y-0 right-0 w-3 bg-black flex flex-col justify-between py-2">
                {Array.from({ length: 11 }).map((_, i) => (
                  <div key={i} className="w-2 h-2 bg-white mx-auto my-1 rounded-sm"></div>
                ))}
              </div>
              {Array.from({ length: stripCount }).map((_, idx) => (
                <div
                  key={idx}
                  className="flex-1 mb-1 last:mb-0 overflow-hidden bg-gray-50 flex items-center justify-center"
                >
                  {uploadedImages[idx] ? (
                    <img src={uploadedImages[idx]} className="w-full h-full object-cover" alt={`uploaded ${idx+1}`} />
                  ) : (
                    <Upload size={24} className="text-gray-300" />
                  )}
                </div>
              ))}
            </div>
            <div className="absolute inset-0 pointer-events-none">
              <img src="/phone-template.png" alt="phone template" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>

        {/* Control Buttons Row (optional placeholders) */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[ZoomOut, ZoomIn, RefreshCw, ArrowRight, ArrowLeft, ArrowDown, ArrowUp].map((Icon, idx) => (
            <button key={idx} className="w-12 h-12 rounded-md bg-green-100 flex items-center justify-center shadow-md active:scale-95 transition-transform">
              <Icon size={20} className="text-gray-700" />
            </button>
          ))}
        </div>

        {/* Upload button */}
        <div className="w-full max-w-xs mb-4">
          <button onClick={openFilePicker} className="w-full bg-blue-100 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <Upload size={20} />
              <span>{uploadedImages.length ? 'Re-upload Images' : 'Upload Images'}</span>
            </div>
          </button>
          <input
            type="file"
            accept="image/*"
            multiple
            ref={fileInputRef}
            className="hidden"
            onChange={handleFilesSelected}
          />
        </div>

        {uploadedImages.length > 0 && (
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