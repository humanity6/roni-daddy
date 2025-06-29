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

const FunnyToonGenerateScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    brand,
    model,
    color,
    template,
    uploadedImage,
    toonStyle,
    aiCredits: initialCredits = 4,
    transform: initialTransform
  } = location.state || {}

  const [aiCredits, setAiCredits] = useState(initialCredits)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null) // Start with no generated image
  const [originalImageFile, setOriginalImageFile] = useState(null)
  const [error, setError] = useState(null)
  const [debugInfo, setDebugInfo] = useState('')
  const [firstGenerateTriggered, setFirstGenerateTriggered] = useState(false)

  // Transform state for adjusting image inside case
  const [transform, setTransform] = useState(initialTransform || { x: 0, y: 0, scale: 2 })

  /* Transform helpers */
  const moveLeft = () => setTransform((p) => ({ ...p, x: Math.max(p.x - 5, -50) }))
  const moveRight = () => setTransform((p) => ({ ...p, x: Math.min(p.x + 5, 50) }))
  const moveUp = () => setTransform((p) => ({ ...p, y: Math.max(p.y - 5, -50) }))
  const moveDown = () => setTransform((p) => ({ ...p, y: Math.min(p.y + 5, 50) }))
  const zoomIn = () => setTransform((p) => ({ ...p, scale: Math.min(p.scale + 0.1, 5) }))
  const zoomOut = () => setTransform((p) => ({ ...p, scale: Math.max(p.scale - 0.1, 0.5) }))
  const resetTransform = () => setTransform({ x: 0, y: 0, scale: 2 })

  // Convert data URL back to File for API calls
  useEffect(() => {
    console.log('🔍 Debug - uploadedImage:', uploadedImage ? 'exists' : 'null')
    
    if (uploadedImage && uploadedImage.startsWith('data:')) {
      setDebugInfo('Converting image to file...')
      // Convert data URL to File object for API calls
      fetch(uploadedImage)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'uploaded-image.png', { type: 'image/png' })
          setOriginalImageFile(file)
          setDebugInfo(`Image file ready: ${file.size} bytes`)
          console.log('🔍 Debug - Original file created:', file.size, 'bytes')
        })
        .catch(err => {
          console.error('Error converting image:', err)
          setError('Failed to process uploaded image')
          setDebugInfo('Error converting image')
        })
    } else {
      setDebugInfo('No uploaded image found')
    }
  }, [uploadedImage])

  // Automatically trigger first generation once image file is ready
  useEffect(() => {
    if (originalImageFile && !firstGenerateTriggered && aiCredits > 0 && !generatedImage && !isGenerating) {
      handleRegenerate()
      setFirstGenerateTriggered(true)
    }
  }, [originalImageFile, firstGenerateTriggered, aiCredits, generatedImage, isGenerating])

  const handleBack = () => {
    navigate('/funny-toon', {
      state: {
        brand,
        model,
        color,
        template,
        uploadedImage,
        toonStyle,
        aiCredits,
        transform
      }
    })
  }

  const handleRegenerate = async () => {
    console.log('🔍 Debug - Regenerate clicked')
    console.log('🔍 Debug - aiCredits:', aiCredits)
    console.log('🔍 Debug - originalImageFile:', originalImageFile ? `exists (${originalImageFile.size} bytes)` : 'null')
    console.log('🔍 Debug - toonStyle:', toonStyle)
    console.log('🔍 Debug - uploadedImage:', uploadedImage ? 'exists' : 'null')
    
    if (aiCredits <= 0) {
      setError('No AI credits remaining')
      return
    }
    
    if (!originalImageFile) {
      setError('No image file available for processing')
      return
    }
    
    setIsGenerating(true)
    setError(null)
    setDebugInfo('Starting AI generation...')
    
    try {
      console.log('🔍 Debug - Making API call...')
      
      // First check if API is running
      const healthCheck = await aiImageService.checkHealth()
      console.log('🔍 Debug - API Health:', healthCheck)
      setDebugInfo(`API Status: ${healthCheck.status}`)
      
      // Generate new image using AI service
      const result = await aiImageService.generateFunnyToon(
        toonStyle || 'Classic Cartoon',
        originalImageFile,
        'medium' // quality
      )
      
      console.log('🔍 Debug - AI Result:', result)
      
      if (result.success) {
        // Get the generated image URL
        const generatedImageUrl = aiImageService.getImageUrl(result.filename)
        console.log('🔍 Debug - Generated image URL:', generatedImageUrl)
        setGeneratedImage(generatedImageUrl)
        setAiCredits((prev) => Math.max(0, prev - 1))
        setDebugInfo('AI generation successful!')
      } else {
        throw new Error('Generation failed - no success flag')
      }
    } catch (err) {
      console.error('🔍 Debug - AI Generation Error:', err)
      const errorMessage = err.message || 'Failed to generate image. Please try again.'
      setError(errorMessage)
      setDebugInfo(`Error: ${errorMessage}`)
      
      // Check if it's a network error
      if (err.message.includes('fetch')) {
        setError('Cannot connect to AI server. Make sure the API server is running on port 8000.')
      }
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
        uploadedImage: generatedImage || uploadedImage, // Use generated image if available
        toonStyle,
        transform
      }
    })
  }

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
        <h1 className="text-lg font-semibold text-gray-800">Funny Toon</h1>
        <div className="w-12 h-12" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Error message */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm text-center max-w-xs">
            {error}
          </div>
        )}

        {/* Phone preview */}
        <div className="relative mb-6">
          <div className="relative w-72 h-[480px]">
            <div className="phone-case-content">
              {/* Show generated image if available, otherwise show uploaded image */}
              {generatedImage ? (
                <img 
                  src={generatedImage} 
                  alt="AI Generated design" 
                  className="phone-case-image"
                  style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
                  onError={(e) => {
                    console.error('Image load error:', e)
                    setError('Failed to load generated image')
                  }}
                />
              ) : uploadedImage ? (
                <img 
                  src={uploadedImage} 
                  alt="Original uploaded design" 
                  className="phone-case-image"
                  style={{ transform: `translate(${transform.x}%, ${transform.y}%) scale(${transform.scale})`, transformOrigin: 'center center' }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <Upload size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Your design here</p>
                  </div>
                </div>
              )}
              
              {/* Loading overlay */}
              {isGenerating && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
                  <div className="text-white text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                    <p className="text-sm">Generating...</p>
                  </div>
                </div>
              )}
            </div>

            {/* Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <img src="/phone-template.png" alt="Phone template" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>

        {/* Controls row */}
        <div className="flex items-center justify-center space-x-3 mb-6">
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
              disabled={isGenerating || (!generatedImage && !uploadedImage)}
              className={`w-12 h-12 rounded-md flex items-center justify-center shadow-md active:scale-95 transition-transform ${isGenerating ? 'bg-gray-100 cursor-not-allowed' : 'bg-green-100 hover:bg-green-200'}`}
            >
              <Icon size={20} className={isGenerating ? 'text-gray-400' : 'text-gray-700'} />
            </button>
          ))}
        </div>

        {/* Arrow row with credits & regenerate */}
        <div className="flex items-center w-full max-w-xs mb-6 px-2">
          {/* Left Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>

          {/* Info & regenerate buttons */}
          <div className="flex flex-col flex-grow mx-2 space-y-2">
            <div className="w-full py-2 rounded-full text-sm font-semibold font-display bg-white border border-gray-300 text-gray-800 text-center">
              AI CREDITS REMAINING: {aiCredits}
            </div>
            <button
              onClick={handleRegenerate}
              disabled={aiCredits === 0 || isGenerating}
              className={`w-full py-2 rounded-full text-sm font-semibold font-display text-white shadow-md transition-all active:scale-95 ${
                aiCredits === 0 ? 'bg-gray-300 cursor-not-allowed' : 'bg-gradient-to-r from-blue-400 to-blue-600'
              }`}
            >
              {isGenerating ? 'Generating...' : 'RE-GENERATE IMAGE'}
            </button>
          </div>

          {/* Right Arrow */}
          <button className="w-12 h-12 rounded-md bg-white border border-gray-300 flex-shrink-0 flex items-center justify-center shadow-md active:scale-95 transition-transform">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Reset Inputs (reusing functionality) */}
        <button
          onClick={handleBack}
          className="w-full max-w-xs bg-green-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform shadow-lg mb-4"
        >
          Back to Styles
        </button>
      </div>

      {/* Generate button - always pink */}
      <div className="relative z-10 p-6 flex justify-center">
        <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
          <div className="rounded-full bg-white p-[6px]">
            <button
              onClick={handleGenerate}
              className="w-16 h-16 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold font-display"
            >
              <span className="text-sm">Generate</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FunnyToonGenerateScreen 