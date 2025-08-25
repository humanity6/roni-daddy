import { ArrowLeft } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { fonts as availableFonts } from '../utils/fontManager'
import { getTemplatePrice } from '../config/templatePricing'
import { useState } from 'react'
import { useAppState } from '../contexts/AppStateContext'

const PaymentScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: appState } = useAppState()
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)
  const [paymentError, setPaymentError] = useState(null)
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null)
  
  // Get vending machine session info and device_id from multiple sources
  const { vendingMachineSession } = appState
  const isVendingMachine = vendingMachineSession?.isVendingMachine || false
  const isRegisteredVending = isVendingMachine && vendingMachineSession?.sessionStatus === 'registered'
  
  // Extract device_id from multiple sources
  const currentUrl = window.location.href
  const urlParams = new URLSearchParams(window.location.search)
  
  // Also try manual extraction as backup
  const deviceIdMatch = currentUrl.match(/device_id=([^&]+)/)
  const deviceIdFromUrl = urlParams.get('device_id') || (deviceIdMatch ? deviceIdMatch[1] : null)
  
  const deviceIdFromSession = vendingMachineSession?.deviceId
  const deviceIdFromState = location.state?.deviceId
  
  // Use first available device_id
  const deviceId = deviceIdFromSession || deviceIdFromUrl || deviceIdFromState
  
  console.log('PaymentScreen - Current URL:', currentUrl)
  console.log('PaymentScreen - URL search params:', window.location.search)
  console.log('PaymentScreen - Device ID from session:', deviceIdFromSession)
  console.log('PaymentScreen - Device ID from URL:', deviceIdFromUrl)  
  console.log('PaymentScreen - Device ID from state:', deviceIdFromState)
  console.log('PaymentScreen - Final Device ID:', deviceId)
  
  // Get Chinese model data from app state
  const phoneSelection = appState.modelData || {}
  const chineseModelId = phoneSelection.chinese_model_id
  
  console.log('PaymentScreen - Device ID:', deviceId)
  console.log('PaymentScreen - Phone Selection:', phoneSelection)
  console.log('PaymentScreen - Chinese Model ID:', chineseModelId)
  console.log('PaymentScreen - App State:', appState)
  if (isVendingMachine && !isRegisteredVending) {
    console.warn('PaymentScreen - Vending session not registered. sessionStatus:', vendingMachineSession?.sessionStatus)
  }

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

  // Always use template pricing (ignore any external price sources)
  const effectivePrice = template?.id 
    ? getTemplatePrice(template.id)
    : 19.99
  
  console.log('PaymentScreen - Pricing Info:', {
    templateId: template?.id,
    templateBasedPrice: effectivePrice,
    externalPrice: price,
    usingTemplatePrice: true
  })

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

  const handlePayOnApp = async () => {
    if (isProcessingPayment) return
    
    setIsProcessingPayment(true)
    setPaymentError(null)
    
    try {
      // Get all the order data we need from app state and location
      const { brand, model, color } = location.state || {}
      const selectedModelData = location.state?.selectedModelData || phoneSelection
      
      // Extract order data from app state and location state consistently
      const brandFromState = appState.brand || selectedModelData?.brand || brand
      const modelFromState = appState.model || selectedModelData?.model || model
      const colorFromState = appState.color || selectedModelData?.color || color
      
      console.log('PaymentScreen - Order data:', { brandFromState, modelFromState, colorFromState, selectedModelData })
      
      // Get final image data from location state - NO BASE64 FALLBACK
      const finalImagePublicUrl = location.state?.finalImagePublicUrl
      const imageSessionId = location.state?.imageSessionId
      
      console.log('PaymentScreen - Final image data:', { 
        finalImagePublicUrl, 
        imageSessionId,
        hasValidImageUrl: !!finalImagePublicUrl
      })
      
      // CRITICAL: Ensure we have a valid uploaded image URL
      if (!finalImagePublicUrl || finalImagePublicUrl.startsWith('data:')) {
        setPaymentError('Image upload failed. Please try again or go back to upload a new image.')
        setIsProcessingPayment(false)
        return
      }
      
      // Store current order data in localStorage for success page
      const orderData = {
        designImage, 
        finalImagePublicUrl, // Store the permanent URL separately
        imageSessionId, // Store session ID for tracking
        uploadedImages,
        imageTransforms,
        price: effectivePrice,
        brand: brandFromState || 'iPhone',
        model: modelFromState || 'iPhone 15 Pro',
        color: colorFromState || 'Natural Titanium',
        chinese_model_id: selectedModelData?.chinese_model_id,
        device_id: deviceId,
        template,
        inputText,
        selectedFont,
        selectedTextColor,
        selectedBackgroundColor,
        textPosition,
        paymentMethod: 'app'
      }
      localStorage.setItem('pendingOrder', JSON.stringify(orderData))
      
      // Chinese API integration will be handled by the backend after successful payment
      // Store the necessary data for post-payment processing
      orderData.deviceId = deviceId
      orderData.selectedModelData = selectedModelData
      localStorage.setItem('pendingOrder', JSON.stringify(orderData))
      
      // Create Stripe checkout session
      console.log('PaymentScreen - Creating Stripe checkout session...')
      const checkoutResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: effectivePrice,
          template_id: template?.id || 'classic',
          brand: brandFromState || 'iPhone',
          model: modelFromState || 'iPhone 15 Pro',
          color: colorFromState || 'Natural Titanium',
          design_image: designImage
        }),
      })
      
      console.log('PaymentScreen - Checkout response status:', checkoutResponse.status)
      
      if (!checkoutResponse.ok) {
        const errorText = await checkoutResponse.text()
        console.error('PaymentScreen - Checkout session creation failed:', errorText)
        throw new Error(`Checkout session creation failed: ${errorText}`)
      }
      
      const responseData = await checkoutResponse.json()
      console.log('PaymentScreen - Checkout response data:', responseData)
      
      const { checkout_url } = responseData
      
      if (!checkout_url) {
        console.error('PaymentScreen - No checkout_url in response')
        throw new Error('No checkout URL received from server')
      }
      
      console.log('PaymentScreen - Redirecting to Stripe checkout:', checkout_url)
      
      // Add a small delay and fallback for redirect
      setTimeout(() => {
        console.log('PaymentScreen - Redirect timeout, showing fallback message')
        setPaymentError('Redirect taking too long. Click here to continue: ' + checkout_url)
        setIsProcessingPayment(false)
      }, 3000)
      
      // Redirect to Stripe hosted checkout
      window.location.href = checkout_url
      
    } catch (error) {
      console.error('Payment error:', error)
      setPaymentError('Payment setup failed. Please try again.')
      setIsProcessingPayment(false)
    }
  }

  const handlePayViaVendingMachine = async () => {
    if (isProcessingPayment) return
    
    setIsProcessingPayment(true)
    setPaymentError(null)
    
    try {
      // Get all the order data we need from app state and location
      const { brand, model, color } = location.state || {}
      const selectedModelData = location.state?.selectedModelData || phoneSelection
      
      if (!deviceId) {
        throw new Error('Device ID is required for vending machine payment')
      }
      
      if (!selectedModelData?.chinese_model_id) {
        throw new Error('Chinese model ID is required for payment processing')
      }
      
      // Extract order data from app state and location state properly
      const brandFromState = appState.brand || selectedModelData?.brand || brand
      const modelFromState = appState.model || selectedModelData?.model || model
      const colorFromState = appState.color || selectedModelData?.color || color
      
      console.log('PaymentScreen - Vending machine payment data:', { 
        brandFromState, modelFromState, colorFromState, selectedModelData, deviceId 
      })
      
      // Get final image data for vending machine flow - NO BASE64 FALLBACK
      const finalImagePublicUrl = location.state?.finalImagePublicUrl
      const imageSessionId = location.state?.imageSessionId
      
      console.log('PaymentScreen - Vending final image data:', { 
        finalImagePublicUrl, 
        imageSessionId,
        hasValidImageUrl: !!finalImagePublicUrl
      })
      
      // CRITICAL: Ensure we have a valid uploaded image URL
      if (!finalImagePublicUrl || finalImagePublicUrl.startsWith('data:')) {
        setPaymentError('Image upload failed. Please try again or go back to upload a new image.')
        setIsProcessingPayment(false)
        return
      }
      
      // Store current order data in localStorage
      const orderData = {
        designImage, 
        uploadedImages,
        imageTransforms,
        price: effectivePrice,
        brand: brandFromState || 'iPhone',
        model: modelFromState || 'iPhone 15 Pro',
        color: colorFromState || 'Natural Titanium',
        chinese_model_id: selectedModelData?.chinese_model_id,
        device_id: deviceId,
        template,
        inputText,
        selectedFont,
        selectedTextColor,
        selectedBackgroundColor,
        textPosition,
        paymentMethod: 'vending_machine'
      }
      localStorage.setItem('pendingOrder', JSON.stringify(orderData))

      // Chinese API activation will be handled by the vending session for proper device_id management
      
      // If in vending machine mode, send order summary to vending machine
  if (isRegisteredVending && vendingMachineSession?.sessionId) {
        // Prepare order data in the format expected by the backend API
        const backendOrderData = {
          brand: brandFromState || 'iPhone',
          brand_id: (brandFromState || 'iPhone').toLowerCase(),
          model: modelFromState || 'iPhone 15 Pro',
          template: template ? {
            id: template.id,
            name: template.name || template.id
          } : null,
          color: colorFromState || 'Natural Titanium',
          inputText: inputText || '',
          selectedFont: selectedFont || 'Arial',
          selectedTextColor: selectedTextColor || '#ffffff',
          image_count: uploadedImages ? uploadedImages.length : 0,
          colors: {
            background: selectedBackgroundColor || '#ffffff',
            text: selectedTextColor || '#ffffff'
          },
          price: effectivePrice,
          chinese_model_id: selectedModelData?.chinese_model_id,
          device_id: deviceId
        }

        console.log('Sending order summary to vending machine:', {
          session_id: vendingMachineSession.sessionId,
          payment_amount: effectivePrice,
          currency: 'GBP',
          order_data: backendOrderData
        })

        const orderSummaryResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${vendingMachineSession.sessionId}/order-summary`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: vendingMachineSession.sessionId,
            order_data: backendOrderData,
            payment_amount: effectivePrice,
            currency: 'GBP'
          })
        })
        
        if (!orderSummaryResponse.ok) {
          let errorMessage = 'Failed to send order to vending machine'
          try {
            const errorData = await orderSummaryResponse.json()
            if (orderSummaryResponse.status === 400 && errorData.detail?.includes('Order data too large')) {
              errorMessage = 'Order details are too large for vending machine processing. Please try with fewer images or simpler design.'
            } else if (orderSummaryResponse.status === 400) {
              errorMessage = `Order validation failed: ${errorData.detail || 'Invalid order data'}`
            } else if (orderSummaryResponse.status === 404) {
              errorMessage = 'Vending machine session not found. Please scan the QR code again.'
            } else if (orderSummaryResponse.status === 410) {
              errorMessage = 'Vending machine session has expired. Please scan the QR code again.'
            } else {
              errorMessage = `Vending machine error (${orderSummaryResponse.status}): ${errorData.detail || 'Unknown error'}`
            }
          } catch (e) {
            errorMessage = `Network error: Unable to communicate with vending machine (${orderSummaryResponse.status})`
          }
          throw new Error(errorMessage)
        }
        
        const summaryResult = await orderSummaryResponse.json()
        console.log('Order summary sent to vending machine:', summaryResult)
        
        // Chinese API integration will be handled after payment confirmation
        // Store the necessary data for post-payment processing
        orderData.deviceId = deviceId
        orderData.selectedModelData = selectedModelData
        orderData.finalImagePublicUrl = finalImagePublicUrl
        localStorage.setItem('pendingOrder', JSON.stringify(orderData))
        
        // Show message to return to vending machine for payment
        alert(`Order ready! Please return to the vending machine to pay £${effectivePrice.toFixed(2)}`)
        
        // Navigate to waiting screen with vending machine context
        navigate('/vending-payment-waiting', { 
          state: { 
            orderData,
            price: effectivePrice,
            vendingMachineSession,
            isVendingMachine: true
          } 
        })
      } else if (isVendingMachine && !isRegisteredVending) {
        // Degraded mode: vending detected but not registered; inform user and fallback to app payment flow
        alert('Machine connection not established (machine busy). You can pay in-app instead.')
        navigate('/vending-payment-waiting', { 
          state: { 
            orderData,
            price: effectivePrice,
            vendingMachineSession: { ...vendingMachineSession, sessionStatus: 'registration_failed' },
            isVendingMachine: false
          } 
        })
      } else {
        // Regular flow for non-vending machine users
        navigate('/vending-payment-waiting', { 
          state: { 
            orderData,
            price: effectivePrice 
          } 
        })
      }
      
    } catch (error) {
      console.error('Vending machine payment error:', error)
      setPaymentError('Vending machine payment setup failed. Please try again.')
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
                      className="w-full h-full object-contain"
                      style={{
                        // RESTORE USER TRANSFORMS for film strip preview
                        ...(imageTransforms && imageTransforms[idx] 
                          ? { 
                              transform: `scale(${imageTransforms[idx].scale})`,
                              transformOrigin: 'center center',
                              objectPosition: `${imageTransforms[idx].x || 50}% ${imageTransforms[idx].y || 50}%`
                            }
                          : {}),
                        objectFit: 'contain'
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
                              className="w-full h-full object-contain"
                              style={{
                                // RESTORE USER TRANSFORMS for 4-image grid preview
                                ...(imageTransforms && imageTransforms[idx] 
                                  ? { 
                                      transform: `translate(${imageTransforms[idx].x}%, ${imageTransforms[idx].y}%) scale(${imageTransforms[idx].scale})`,
                                      transformOrigin: 'center center'
                                    }
                                  : {}),
                                objectFit: 'contain',
                                objectPosition: 'center'
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
                              className="w-full h-full object-contain"
                              style={{
                                // RESTORE USER TRANSFORMS for vertical multi-image preview
                                ...(imageTransforms && imageTransforms[idx] 
                                  ? { 
                                      transform: `translate(${imageTransforms[idx].x}%, ${imageTransforms[idx].y}%) scale(${imageTransforms[idx].scale})`,
                                      transformOrigin: 'center center'
                                    }
                                  : {}),
                                objectFit: 'contain',
                                objectPosition: 'center'
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
                    style={{
                      // RESTORE USER TRANSFORMS - show exactly what user finalized during cropping
                      ...(imageTransforms && imageTransforms[0] 
                        ? { 
                            transform: `translate(${imageTransforms[0].x}%, ${imageTransforms[0].y}%) scale(${imageTransforms[0].scale})`,
                            transformOrigin: 'center center'
                          }
                        : initialTransform 
                        ? { 
                            transform: `translate(${initialTransform.x}%, ${initialTransform.y}%) scale(${initialTransform.scale})`,
                            transformOrigin: 'center center'
                          }
                        : {}),
                      objectFit: 'contain',
                      objectPosition: 'center'
                    }}
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
          
          {/* Vending Machine Indicator */}
          {isVendingMachine && (
            <div className="mt-4 px-6 py-3 bg-green-100 border-2 border-green-300 rounded-xl">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <p className="text-green-800 font-semibold">
                  Connected to {vendingMachineSession?.machineInfo?.name || 'Vending Machine'}
                </p>
              </div>
              {vendingMachineSession?.location && (
                <p className="text-green-700 text-sm text-center mt-1">
                  Location: {vendingMachineSession.location}
                </p>
              )}
              {deviceId && (
                <p className="text-green-700 text-xs text-center mt-1">
                  Device: {deviceId}
                </p>
              )}
            </div>
          )}
          
          {/* Chinese API Status Indicators */}
          {!deviceId && (
            <div className="mt-4 px-6 py-3 bg-yellow-100 border-2 border-yellow-300 rounded-xl">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <p className="text-yellow-800 font-semibold text-sm">
                  Warning: No device ID - scan QR code from vending machine
                </p>
              </div>
            </div>
          )}
          
          {(!phoneSelection?.chinese_model_id && !location.state?.selectedModelData?.chinese_model_id) && (
            <div className="mt-4 px-6 py-3 bg-red-100 border-2 border-red-300 rounded-xl">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <p className="text-red-800 font-semibold text-sm">
                  Error: No Chinese model ID - please select model again
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Payment Method Selection */}
        <div className="my-8 space-y-4">
          <h3 className="text-xl font-semibold text-center text-gray-800 mb-6">
            Choose Payment Method
          </h3>
          
          {/* Pay on App Button */}
          <div className="flex justify-center">
            <div className="rounded-full bg-blue-400 p-[6px] shadow-xl transition-transform active:scale-95">
              <div className="rounded-full bg-white p-[6px]">
                <button
                  onClick={handlePayOnApp}
                  disabled={isProcessingPayment}
                  className="px-8 py-4 rounded-full flex items-center justify-center bg-blue-400 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed min-w-[160px]"
                >
                  {isProcessingPayment ? '...' : 'Pay on App'}
                </button>
              </div>
            </div>
          </div>

          {/* Or Separator */}
          <div className="flex items-center justify-center py-2">
            <div className="border-t border-gray-300 w-16"></div>
            <span className="mx-4 text-gray-500 font-medium">OR</span>
            <div className="border-t border-gray-300 w-16"></div>
          </div>

          {/* Pay via Vending Machine Button */}
          <div className="flex justify-center">
            <div className="rounded-full bg-green-400 p-[6px] shadow-xl transition-transform active:scale-95">
              <div className="rounded-full bg-white p-[6px]">
                <button
                  onClick={handlePayViaVendingMachine}
                  disabled={isProcessingPayment || !deviceId || (!phoneSelection?.chinese_model_id && !location.state?.selectedModelData?.chinese_model_id)}
                  className="px-8 py-4 rounded-full flex items-center justify-center bg-green-400 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed min-w-[160px]"
                >
                  {isProcessingPayment ? '...' : 'Pay via Machine'}
                </button>
              </div>
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
            {isVendingMachine ? (
              <>
                You scanned the QR code from a <span className="font-semibold">vending machine</span>.
                <br />Choose <span className="font-semibold">Pay via Machine</span> to pay at the machine, or <span className="font-semibold">Pay on App</span> for card payment.
              </>
            ) : (
              <>
                Choose <span className="font-semibold">Pay on App</span> for card payment
                <br />or <span className="font-semibold">Pay via Machine</span> to use the vending machine.
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}

export default PaymentScreen 