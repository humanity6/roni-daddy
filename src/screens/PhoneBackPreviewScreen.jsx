import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  ArrowLeft, 
  ArrowRight, 
  Upload, 
  Sparkles, 
  Film, 
  Palette,
  Camera,
  Image as ImageIcon,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const PhoneBackPreviewScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, uploadedImage, template } = location.state || {}
  
  const [additionalImages, setAdditionalImages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleImageUpload = (event, index) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const newImages = [...additionalImages]
        newImages[index] = e.target.result
        setAdditionalImages(newImages)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleBack = () => {
    navigate('/template-selection')
  }

  const handleNext = () => {
    setIsLoading(true)
    // Simulate processing time for AI templates
    setTimeout(() => {
      setIsLoading(false)
      // Navigate to retry screen for potential modifications
      navigate('/retry')
    }, 2000)
  }

  const getCategoryIcon = (category) => {
    switch(category) {
      case 'ai': return <Sparkles size={16} className="text-purple-500" />
      case 'film': return <Film size={16} className="text-orange-500" />
      default: return <Palette size={16} className="text-blue-500" />
    }
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

  const renderTemplateLayout = () => {
    if (!template || !uploadedImage) return null

    const images = [uploadedImage, ...additionalImages].filter(Boolean)
    
    switch(template.id) {
      case 'classic':
        return (
          <div className="w-full h-full relative">
            <img 
              src={images[0]} 
              alt="Classic design" 
              className="phone-case-image"
            />
            {template.category === 'ai' && (
              <div className="absolute top-2 right-2 bg-purple-500 text-white px-2 py-1 rounded text-xs font-medium">
                AI Enhanced
              </div>
            )}
          </div>
        )
      
      case '2-in-1':
        return (
          <div className="w-full h-full grid grid-cols-2 gap-1">
            <img 
              src={images[0]} 
              alt="Image 1" 
              className="phone-case-image"
            />
            {images[1] ? (
              <img 
                src={images[1]} 
                alt="Image 2" 
                className="phone-case-image"
              />
            ) : (
              <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                <Camera size={24} className="text-gray-400" />
              </div>
            )}
          </div>
        )
      
      case '3-in-1':
        return (
          <div className="w-full h-full grid grid-rows-2 gap-1">
            <img 
              src={images[0]} 
              alt="Image 1" 
              className="phone-case-image"
            />
            <div className="grid grid-cols-2 gap-1">
              {images[1] ? (
                <img 
                  src={images[1]} 
                  alt="Image 2" 
                  className="phone-case-image"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <Camera size={16} className="text-gray-400" />
                </div>
              )}
              {images[2] ? (
                <img 
                  src={images[2]} 
                  alt="Image 3" 
                  className="phone-case-image"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <Camera size={16} className="text-gray-400" />
                </div>
              )}
            </div>
          </div>
        )
      
      case '4-in-1':
        return (
          <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-1">
            {[0, 1, 2, 3].map((index) => (
              images[index] ? (
                <img 
                  key={index}
                  src={images[index]} 
                  alt={`Image ${index + 1}`} 
                  className="phone-case-image"
                />
              ) : (
                <div key={index} className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <Camera size={16} className="text-gray-400" />
                </div>
              )
            ))}
          </div>
        )
      
      case 'film-strip-3':
        return (
          <div className="w-full h-full bg-gray-900 p-4">
            <div className="flex flex-col h-full space-y-2">
              {[0, 1, 2].map((index) => (
                <div key={index} className="flex-1 bg-white rounded border-2 border-gray-800">
                  {images[index] ? (
                    <img 
                      src={images[index]} 
                      alt={`Film frame ${index + 1}`} 
                      className="phone-case-image rounded"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <Film size={16} className="text-gray-400" />
                    </div>
                  )}
                </div>
              ))}
            </div>
            {/* Film strip holes */}
            <div className="absolute left-2 top-0 bottom-0 w-4 flex flex-col justify-center space-y-3">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="w-2 h-2 bg-gray-700 rounded-full mx-auto"></div>
              ))}
            </div>
          </div>
        )
      
      default:
        return (
          <div className="w-full h-full relative">
            <img 
              src={images[0]} 
              alt="Template design" 
              className="phone-case-image"
            />
            {template.category === 'ai' && (
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                <div className="absolute top-2 right-2 bg-purple-500 text-white px-2 py-1 rounded text-xs font-medium flex items-center space-x-1">
                  <Sparkles size={12} />
                  <span>AI</span>
                </div>
              </div>
            )}
          </div>
        )
    }
  }

  const imagesNeeded = template?.imageCount || 1
  const imagesUploaded = [uploadedImage, ...additionalImages].filter(Boolean).length

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 flex items-center justify-between p-4">
        <button 
          onClick={handleBack}
          className="w-12 h-12 rounded-full bg-cyan-400 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
        >
          <ArrowLeft size={20} className="text-white" />
        </button>
        <div className="w-12 h-12"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
        {/* Phone Case Preview */}
        <div className="relative mb-8">
          {/* Phone Case Container */}
          <div className="relative w-72 h-[480px]">
            {/* Template layout - positioned to fit exactly within phone template boundaries */}
            <div className="phone-case-content">
              {uploadedImage && template ? (
                renderTemplateLayout()
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-400">
                    <ImageIcon size={48} className="mx-auto mb-3" />
                    <p className="text-sm">Template preview</p>
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
          </div>
        </div>

                 {/* Navigation Arrows */}
         <div className="flex items-center justify-between w-full max-w-xs mb-6">
           <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
             <ChevronLeft size={24} className="text-gray-600" />
           </button>
           <button className="w-12 h-12 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg active:scale-95 transition-transform">
             <ChevronRight size={24} className="text-gray-600" />
           </button>
         </div>

         {/* Upload Additional Images */}
         {template && imagesNeeded > 1 && (
           <div className="w-full max-w-xs mb-4">
             <div className="space-y-3">
               {[...Array(imagesNeeded - 1)].map((_, index) => (
                 <label key={index} className="block">
                   <input
                     type="file"
                     accept="image/*"
                     onChange={(e) => handleImageUpload(e, index)}
                     className="hidden"
                   />
                   <div className="w-full bg-blue-200 text-gray-800 font-medium py-3 px-6 rounded-full text-center active:scale-95 transition-transform cursor-pointer shadow-lg">
                     <div className="flex items-center justify-center space-x-2">
                       <Upload size={20} />
                       <span>Upload Image {index + 2}</span>
                     </div>
                   </div>
                 </label>
               ))}
             </div>
           </div>
         )}

         {/* Template Info */}
         {template && (
           <div className="w-full max-w-xs mb-4">
             <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
               <div className="flex items-center justify-center space-x-2 mb-2">
                 {getCategoryIcon(template.category)}
                 <h3 className="font-bold text-gray-800">{template.name}</h3>
                 <span className="font-bold text-pink-600">{template.price}</span>
               </div>
               <p className="text-sm text-gray-600 text-center">{template.description}</p>
               {template.category === 'ai' && (
                 <div className="mt-3 flex items-center justify-center space-x-2">
                   <Sparkles className="text-purple-500 animate-pulse" size={16} />
                   <span className="text-xs text-purple-600">AI Enhanced</span>
                 </div>
               )}
             </div>
           </div>
         )}
       </div>

       {/* Submit Button */}
       <div className="relative z-10 p-6">
         {isLoading ? (
           <div className="w-16 h-16 rounded-full bg-gray-400 mx-auto flex items-center justify-center shadow-xl">
             <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
           </div>
         ) : (
           <button 
             onClick={handleNext}
             disabled={imagesUploaded < imagesNeeded}
             className={`
               w-16 h-16 rounded-full mx-auto flex items-center justify-center shadow-xl transition-all duration-200
               ${imagesUploaded >= imagesNeeded 
                 ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white active:scale-95' 
                 : 'bg-gray-300 text-gray-500 cursor-not-allowed'
               }
             `}
           >
             <span className="font-bold text-sm">Submit</span>
           </button>
         )}
       </div>
    </div>
  )
}

export default PhoneBackPreviewScreen 