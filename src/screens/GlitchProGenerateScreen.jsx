import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  Upload,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'
import aiImageService from '../services/aiImageService'

const GlitchProGenerateScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    brand,
    model,
    color,
    template,
    uploadedImage,
    mode = 'retro',
    aiCredits: initialCredits = 4,
    transform: initialTransform
  } = location.state || {}

  const [aiCredits, setAiCredits] = useState(initialCredits)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [originalImageFile, setOriginalImageFile] = useState(null)
  const [error, setError] = useState(null)
  const [firstGenerateTriggered, setFirstGenerateTriggered] = useState(false)
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })

  /* ---------------- helpers ---------------- */
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

  /* Convert uploaded dataUrl to File once */
  useEffect(() => {
    if (uploadedImage && uploadedImage.startsWith('data:')) {
      fetch(uploadedImage)
        .then((res) => res.blob())
        .then((blob) => setOriginalImageFile(new File([blob], 'upload.png', { type: 'image/png' })))
        .catch(() => setError('Failed to process image'))
    }
  }, [uploadedImage])

  /* Auto first generation */
  useEffect(() => {
    if (originalImageFile && !firstGenerateTriggered && aiCredits > 0 && !generatedImage && !isGenerating) {
      handleRegenerate()
      setFirstGenerateTriggered(true)
    }
  }, [originalImageFile, firstGenerateTriggered, aiCredits, generatedImage, isGenerating])

  /* navigation */
  const handleBack = () => {
    navigate('/glitch', {
      state: { brand, model, color, template, uploadedImage, transform, mode, aiCredits }
    })
  }

  /* regenerate */
  const handleRegenerate = async () => {
    if (aiCredits <= 0 || !originalImageFile) return
    setIsGenerating(true)
    setError(null)
    try {
      await aiImageService.checkHealth()
      const result = await aiImageService.generateGlitchPro(mode, originalImageFile, 'medium')
      if (result.success) {
        setGeneratedImage(aiImageService.getImageUrl(result.filename))
        setAiCredits((prev) => Math.max(0, prev - 1))
      } else {
        throw new Error('Generation failed')
      }
    } catch (err) {
      setError(err.message || 'Failed to generate image')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleGenerate = () => {
    navigate('/text-input', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage: generatedImage || uploadedImage,
        mode,
        transform
      }
    })
  }

  return (
    <div className="screen-container">
      <PastelBlobs />
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button onClick={handleBack} className="w-12 h-12 rounded-full bg-white/90 border-4 border-pink-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"><ArrowLeft size={20} className="text-pink-400"/></button>
        <h1 className="text-lg font-semibold text-gray-800">Glitch Pro X</h1>
        <div className="w-12 h-12"/>
      </div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {error && <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm text-center max-w-xs">{error}</div>}

        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-border"></div>
            <div className="phone-case-content">
              {generatedImage ? (
                <img src={generatedImage} alt="AI" className="phone-case-image-contain" style={{ transform:`translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin:'center center' }}/>
              ) : uploadedImage ? (
                <img src={uploadedImage} alt="Upload" className="phone-case-image-contain" style={{ transform:`translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin:'center center' }}/>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50"><Upload size={48} className="text-gray-400"/></div>
              )}
              {isGenerating && <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10"><div className="text-white text-sm">Generating…</div></div>}
            </div>
            <div className="absolute inset-0 pointer-events-none"><img src="/phone-template.png" className="w-full h-full object-contain"/></div>
          </div>
        </div>

        {/* controls */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          {[{Icon:ZoomOut,action:zoomOut},{Icon:ZoomIn,action:zoomIn},{Icon:RefreshCw,action:resetTransform},{Icon:ArrowRight,action:moveRight},{Icon:ArrowLeft,action:moveLeft},{Icon:ArrowDown,action:moveDown},{Icon:ArrowUp,action:moveUp}].map(({Icon,action},idx)=>(<button key={idx} onClick={action} disabled={isGenerating||(!generatedImage&&!uploadedImage)} className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-transform ${isGenerating?'bg-gray-100':'bg-green-100 hover:bg-green-200'}`}><Icon size={20} className="text-gray-700"/></button>))}
        </div>

        {/* credits */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          <button 
            onClick={handleBack}
            className="w-12 h-12 rounded-md bg-white border border-gray-300 flex items-center justify-center shadow-md"
          >
            <ChevronLeft size={24} className="text-gray-600"/>
          </button>
          <div className="flex flex-col flex-grow mx-2 space-y-2">
            <div className="w-full py-2 rounded-full text-sm font-semibold bg-white border border-gray-300 text-gray-800 text-center">AI CREDITS REMAINING: {aiCredits}</div>
            <button onClick={handleRegenerate} disabled={aiCredits===0||isGenerating} className={`w-full py-2 rounded-full text-sm font-semibold text-white shadow-md active:scale-95 ${aiCredits===0?'bg-gray-300':'bg-gradient-to-r from-blue-400 to-blue-600'}`}>{isGenerating?'Generating...':'RE-GENERATE IMAGE'}</button>
          </div>
          <button 
            onClick={handleGenerate}
            disabled={!generatedImage}
            className={`w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center shadow-md ${
              generatedImage ? 'bg-white cursor-pointer' : 'bg-gray-100 cursor-not-allowed'
            }`}
          >
            <ChevronRight size={24} className={`${generatedImage ? 'text-gray-600' : 'text-gray-400'}`}/>
          </button>
        </div>
      </div>

      {/* Generate button - styled like Submit button */}
      <div className="relative z-10 p-6 flex justify-center">
        {/* Outer Pink Ring */}
        <div className="w-24 h-24 rounded-full border-8 border-pink-400 flex items-center justify-center shadow-xl">
          {/* Minimal gap between circles */}
          <div className="w-17 h-17 rounded-full border-0.5 border-white bg-white flex items-center justify-center">
            {/* Inner Pink Circle */}
            <button 
              onClick={handleGenerate}
              className="w-16 h-16 rounded-full bg-pink-400 text-white flex items-center justify-center active:scale-95 transition-transform"
            >
              <span className="font-semibold text-[10px]">Generate</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlitchProGenerateScreen 