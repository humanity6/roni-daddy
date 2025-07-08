import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import PastelBlobs from '../components/PastelBlobs'

const TemplateSelectionScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { brand, model, color, uploadedImage } = location.state || {}
  
  // State kept only for quick visual selection feedback (optional)
  const [selectedTemplate, setSelectedTemplate] = useState('')

  const templates = [
    // Basic Templates
    {
      id: 'classic',
      name: 'Classic',
      price: '£19.99',
      category: 'basic',
      description: 'Single image with background',
      imageCount: 1,
      features: ['Background colors', 'Text overlay', 'Border options'],
      preview: 'classic-preview',
      imagePath: '/ui-mockups/pickadesignmode_classic.png'
    },
    {
      id: '2-in-1',
      name: '2 in 1',
      price: '£19.99',
      category: 'basic',
      description: '2 images with layouts',
      imageCount: 2,
      features: ['Dual layouts', 'Custom backgrounds', 'Text options'],
      preview: '2in1-preview',
      imagePath: '/ui-mockups/pickadesignmode_2in1.png'
    },
    {
      id: '3-in-1',
      name: '3 in 1',
      price: '£19.99',
      category: 'basic',
      description: '3 images with layouts',
      imageCount: 3,
      features: ['Triple layouts', 'Backgrounds', 'Text styling'],
      preview: '3in1-preview',
      imagePath: '/ui-mockups/pickadesignmode_3in1.png'
    },
    {
      id: '4-in-1',
      name: '4 in 1',
      price: '£19.99',
      category: 'basic',
      description: '4 images with layouts',
      imageCount: 4,
      features: ['Quad layouts', 'Custom backgrounds', 'Typography'],
      preview: '4in1-preview',
      imagePath: '/ui-mockups/pickadesignmode_4in1.png'
    },
    
    // AI-Enhanced Templates
    {
      id: 'retro-remix',
      name: 'Retro Remix',
      price: '£21.99',
      category: 'ai',
      description: 'AI retro style',
      imageCount: 1,
      features: ['AI enhancement', 'Retro filters', 'Keyword prompts'],
      preview: 'retro-preview',
      imagePath: '/ui-mockups/pickadesignmode_retroremix.png'
    },
    // Film Strip Template (order swapped to appear after Retro Remix)
    {
      id: 'film-strip-3',
      name: 'Film Strip',
      price: '£19.99',
      category: 'film',
      description: '3 in 1 Film Strip',
      imageCount: 3,
      features: ['Vintage film look', 'Sequential layout', 'Film grain effect'],
      preview: 'filmstrip-preview',
      imagePath: '/ui-mockups/pickadesignmode_filmstrip.png'
    },
    {
      id: 'cover-shoot',
      name: 'Cover Shoot',
      price: '£21.99',
      category: 'ai',
      description: 'Model-style AI enhancement',
      imageCount: 1,
      features: ['AI styling', 'Professional look', 'Magazine cover'],
      preview: 'cover-preview',
      imagePath: '/ui-mockups/pickadesignmode_covershoot.png'
    },
    {
      id: 'funny-toon',
      name: 'Funny Toon',
      price: '£21.99',
      category: 'ai',
      description: 'Cartoon conversion',
      imageCount: 1,
      features: ['AI cartoon', 'Style options', 'Fun effects'],
      preview: 'toon-preview',
      imagePath: '/ui-mockups/pickadesignmode_funnytoon.png'
    },
    {
      id: 'glitch-pro',
      name: 'Glitch Pro X',
      price: '£21.99',
      category: 'ai',
      description: 'Digital glitch effects',
      imageCount: 1,
      features: ['Glitch effects', 'Retro/Chaos modes', 'Digital art'],
      preview: 'glitch-preview',
      imagePath: '/ui-mockups/pickadesignmode_glitchproX.png'
    },
    {
      id: 'footy-fan',
      name: 'Footy Fan',
      price: '£23.99',
      category: 'ai',
      description: 'Football team themes',
      imageCount: 1,
      features: ['Team colors', 'Football graphics', 'Fan style'],
      preview: 'footy-preview',
      imagePath: '/ui-mockups/pickadesignmode_footyfan.png'
    }
  ]

  const handleTemplateSelect = (templateId) => {
    const template = templates.find(t => t.id === templateId)
    // Provide quick visual feedback before navigation
    setSelectedTemplate(templateId)
    
    // Route film-strip template to film-strip screen
    if (template.id?.startsWith('film-strip')) {
      navigate('/film-strip', {
        state: {
          brand,
          model,
          color,
          template
        }
      })
    }
    // Route multi-image templates directly to upload screen
    else if (template?.imageCount && template.imageCount > 1) {
      navigate('/multi-image-upload', {
        state: {
          brand,
          model,
          color,
          template
        }
      })
    } else {
      navigate('/phone-preview', {
        state: {
          brand,
          model,
          color,
          template
        }
      })
    }
  }

  const handleBack = () => {
    navigate('/phone-brand', { 
      state: { 
        brand 
      } 
    })
  }

  const getPreviewGradient = (templateId) => {
    const gradients = {
      'classic': 'from-blue-400 to-purple-500',
      '2-in-1': 'from-green-400 to-blue-500',
      '3-in-1': 'from-pink-400 to-red-500',
      '4-in-1': 'from-yellow-400 to-orange-500',
      'film-strip-3': 'from-gray-700 to-gray-900',
      'retro-remix': 'from-orange-400 to-pink-500',
      'cover-shoot': 'from-purple-600 to-blue-600',
      'funny-toon': 'from-green-400 to-yellow-400',
      'glitch-pro': 'from-red-500 to-purple-600',
      'footy-fan': 'from-green-500 to-green-700'
    }
    return gradients[templateId] || 'from-gray-400 to-gray-600'
  }

  // Helper to render template preview with fixed size
  const renderTemplatePreview = (template) => {
    /*
      Enlarged preview wrapper to better match the dimensions shown
      in the UI mock-up (roughly 700×1350 → aspect ≈ 1 : 1.93).
      We keep a fixed width so four cases fit a single row on most
      mobile screens and calculate the height accordingly.
    */
    return (
      <div className="aspect-[7/13.5] w-full max-w-[90px] mx-auto rounded-xl flex items-center justify-center bg-white">
        {/* Template preview image */}
        <img 
          src={template.imagePath} 
          alt={`${template.name} template preview`}
          className="w-full h-full object-contain rounded-xl shadow-md"
          onError={(e) => {
            e.target.style.display = 'none'
            e.target.nextSibling.style.display = 'flex'
          }}
        />
        {/* Fallback gradient background */}
        <div 
          className={`w-full h-full bg-gradient-to-br ${getPreviewGradient(template.id)} rounded-xl`}
          style={{ display: 'none' }}
        >
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-white text-xs font-medium">{template.name}</div>
          </div>
        </div>
      </div>
    )
  }

  // Group templates into rows: first 4, next 3, last 3
  const groupedTemplates = [
    templates.slice(0, 4),
    templates.slice(4, 7),
    templates.slice(7, 10)
  ]

  return (
    <div className="screen-container">
      <PastelBlobs />
      
      {/* Header */}
      <div className="relative z-10 flex items-center p-4">
        <button 
          onClick={handleBack}
          className="w-10 h-10 rounded-full bg-white border-2 border-pink-500 flex items-center justify-center active:scale-95 transition-transform absolute left-4"
        >
          <ArrowLeft size={20} className="text-pink-500" />
        </button>
        <h1 className="text-2xl md:text-4xl font-cubano text-[#424242] tracking-normal text-center w-full px-16 whitespace-nowrap">PICK A DESIGN MODE</h1>
      </div>

      {/* Content */}
      <div className="relative z-10 flex-1 pt-2 pb-2 px-2 overflow-visible flex justify-center">
        {/* Centered grid container with fixed width */}
        <div className="max-w-[420px] w-full mx-auto space-y-4">
          {groupedTemplates.map((row, idx) => (
            <div
              key={idx}
              className={`grid ${idx === 0 ? 'grid-cols-4' : 'grid-cols-3'} gap-x-2 gap-y-4`}
              style={{ alignItems: 'start' }}
            >
              {row.map((template) => (
                <button
                  key={template.id}
                  onClick={() => handleTemplateSelect(template.id)}
                  className={`flex flex-col items-center transition-transform duration-200 relative ${selectedTemplate === template.id ? 'scale-105' : ''} active:scale-95 w-full`}
                  style={{ minWidth: 0 }}
                >
                  <div className="mb-1 w-full">
                    {renderTemplatePreview(template)}
                  </div>
                  <div className="flex flex-col items-center justify-center text-center w-full px-0 mt-0">
                    {/* Template name on its own line */}
                    <span
                      className="text-[13px] font-normal text-gray-900 font-poppins-light leading-tight w-full"
                      style={{ wordSpacing: '-2px', maxWidth: '100%' }}
                    >
                      {template.name}
                    </span>
                    {/* Template price on the next line */}
                    <span className="text-[13px] font-bold text-gray-900 font-poppins-light leading-tight w-full">
                      {template.price}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Next button removed for mobile-first instantaneous navigation */}
    </div>
  )
}

export default TemplateSelectionScreen 