import { ArrowLeft } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { fonts as availableFonts } from '../utils/fontManager'
import { getTemplatePrice } from '../config/templatePricing'
import { useState } from 'react'

const PaymentScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)
  const [paymentError, setPaymentError] = useState(null)

  // Expecting these values from previous step, otherwise use sensible defaults
  const {
    designImage,
    uploadedImages,
    imageTransforms,
    inputText,
    selectedFont = 'Arial',
    fontSize = 30,
    selectedTextColor = '#ffffff',
    selectedBackgroundColor = '#ffffff',
    textPosition,
    transform: initialTransform,
    template,
    stripCount,
    price,
  } = location.state || {}

  // Fixed smaller blobs that match the mock-up design
  const cornerBlobs = [
    {
      top: '-80px',
      left: '-100px',
      width: '180px',
      height: '140px',
      background: '#F8D9DE', // soft pink
      borderRadius: '65% 35% 55% 45% / 50% 60% 40% 50%'
    },
    {
      top: '-90px',
      right: '-90px',
      width: '150px',
      height: '130px',
      background: '#CBE8F4', // pale blue
      borderRadius: '35% 65% 45% 55% / 60% 40% 60% 40%'
    },
    {
      bottom: '-90px',
      left: '-100px',
      width: '170px',
      height: '140px',
      background: '#CBE8F4', // pale blue duplicate bottom-left
      borderRadius: '55% 45% 60% 40% / 45% 55% 35% 65%'
    },
    {
      bottom: '-100px',
      right: '-100px',
      width: '210px',
      height: '160px',
      background: '#D4EFC1', // light green
      borderRadius: '45% 55% 65% 35% / 50% 60% 40% 50%'
    }
  ]

  // Get the effective price from template pricing config
  const effectivePrice = 
    typeof price === 'number' && !isNaN(price)
      ? price
      : template?.id 
        ? getTemplatePrice(template.id)
        : 19.99

  // Compute style helpers reused from previous screens
  const getPreviewStyle = () => ({
    fontFamily: availableFonts.find(f => f.name === selectedFont)?.style || 'Arial, sans-serif',
    fontSize: `${fontSize}px`,
    color: selectedTextColor,
    whiteSpace: 'nowrap',
    fontWeight: '500',
    lineHeight: '1.2'
  })

  const getTextStyle = () => ({
    position: 'absolute',
    left: `${textPosition?.x || 50}%`,
    top: `${textPosition?.y || 50}%`,
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none'
  })

  const handleBack = () => {
    navigate(-1)
  }

  const handlePay = async () => {
    if (isProcessingPayment) return
    
    setIsProcessingPayment(true)
    setPaymentError(null)
    
    try {
      // Get all the order data we need
      const { brand, model, color } = location.state || {}
      
      // Create payment intent
      const paymentResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/create-payment-intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: effectivePrice,
          template_id: template?.id || 'classic',
          brand: brand || 'iPhone',
          model: model || 'iPhone 15 Pro',
          color: color || 'Natural Titanium'
        }),
      })
      
      if (!paymentResponse.ok) {
        throw new Error('Payment setup failed')
      }
      
      const { payment_intent_id } = await paymentResponse.json()
      
      // For now, simulate successful payment (in production, this would use Stripe Elements)
      // Confirm payment
      const confirmResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/confirm-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_intent_id,
          order_data: {
            mobile_model_id: `MM${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}000001`,
            pic: designImage
          }
        }),
      })
      
      if (!confirmResponse.ok) {
        throw new Error('Payment confirmation failed')
      }
      
      const orderResult = await confirmResponse.json()
      
      // Navigate to order confirmed with real data
      navigate('/order-confirmed', { 
        state: { 
          designImage, 
          uploadedImages,
          imageTransforms,
          price: effectivePrice,
          orderData: orderResult,
          brand,
          model,
          color,
          template
        } 
      })
      
    } catch (error) {
      console.error('Payment error:', error)
      setPaymentError('Payment failed. Please try again.')
    } finally {
      setIsProcessingPayment(false)
    }
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Pastel blobs background – fixed smaller shapes in each corner */}
      {cornerBlobs.map((blob, i) => (
        <div
          key={i}
          className="absolute opacity-70"
          style={{
            ...blob,
          }}
        />
      ))}

      {/* Content wrapper */}
      <div className="relative z-10 flex flex-col items-center px-6 py-8 min-h-screen">
        {/* Back Arrow */}
        <div className="w-full flex justify-start mb-4">
          <button
            onClick={handleBack}
            className="w-12 h-12 rounded-full bg-white border-4 border-blue-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
          >
            <ArrowLeft size={20} className="text-blue-500" />
          </button>
        </div>

        {/* Phone render */}
        <div className="flex-1 flex flex-col items-center justify-start pt-2">
          {template?.id?.startsWith('film-strip') ? (
            <div className="relative w-[525px] h-[525px] overflow-hidden pointer-events-none">
              {/* Background color layer for film strip */}
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
              
              <div
                className="absolute inset-0 flex flex-col justify-center items-center z-10"
                style={{ paddingTop:'0px', paddingBottom:'0px', paddingLeft:'180px', paddingRight:'179px'}}
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
            <div className="relative w-64 h-[420px] mx-auto">
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
                ) : designImage ? (
                  <img 
                    src={designImage} 
                    alt="Your design" 
                    className="phone-case-image-contain"
                    style={initialTransform ? { transform: `translate(${initialTransform.x}%, ${initialTransform.y}%) scale(${initialTransform.scale})`, transformOrigin: 'center center' } : undefined}
                  />
                ) : (
                  <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 text-sm">No design</div>
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

          {/* Price */}
          <div className="mt-10">
            <div className="px-8 py-3 rounded-full" style={{ background: '#DFF4FF' }}>
              <p
                className="text-4xl font-semibold text-[#2F3842]"
                style={{ fontFamily: 'Cubano, sans-serif' }}
              >
                £{effectivePrice.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Pay button */}
        <div className="my-8">
          <div className="rounded-full bg-pink-400 p-[6px] shadow-xl transition-transform active:scale-95">
            <div className="rounded-full bg-white p-[6px]">
              <button
                onClick={handlePay}
                disabled={isProcessingPayment}
                className="w-20 h-20 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessingPayment ? '...' : 'Pay'}
              </button>
            </div>
          </div>
        </div>

        {/* Error message */}
        {paymentError && (
          <div className="mb-4 px-4 py-2 bg-red-100 border border-red-400 text-red-700 rounded">
            {paymentError}
          </div>
        )}

        {/* Bottom helper text */}
        <div className="mb-8 text-center">
          <p
            className="text-gray-500 text-lg"
            style={{ fontFamily: 'PoppinsLight, Poppins, sans-serif' }}
          >
            Please <span className="font-semibold">Scan</span> Your
            <br /> Card on the Card Reader.
          </p>
        </div>
      </div>
    </div>
  )
}

export default PaymentScreen 