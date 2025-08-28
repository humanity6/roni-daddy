import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useAppState } from '../contexts/AppStateContext'

const PaymentSuccessScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { state, actions } = useAppState()
  const [isProcessing, setIsProcessing] = useState(true)
  const [orderData, setOrderData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const processPayment = async () => {
      try {
        // Get session ID from URL params
        const urlParams = new URLSearchParams(location.search)
        const sessionId = urlParams.get('session_id')
        
        if (!sessionId) {
          throw new Error('No session ID found')
        }

        // Get pending order data from localStorage
        const pendingOrderData = JSON.parse(localStorage.getItem('pendingOrder') || '{}')
        console.log('PaymentSuccessScreen - pendingOrderData from localStorage:', pendingOrderData)
        console.log('PaymentSuccessScreen - selectedModelData:', pendingOrderData.selectedModelData)
        console.log('PaymentSuccessScreen - mobile_shell_id direct:', pendingOrderData.mobile_shell_id)
        console.log('PaymentSuccessScreen - mobile_shell_id in selectedModelData:', pendingOrderData.selectedModelData?.mobile_shell_id)
        
        // Extract device_id from multiple sources
        const deviceIdFromUrl = urlParams.get('device_id') || urlParams.get('machine_id')
        const deviceIdFromState = state.vendingMachineSession?.deviceId
        const deviceIdFromStorage = localStorage.getItem('pimpMyCase_deviceId')
        const deviceIdFromPending = pendingOrderData.deviceId
        
        // Priority order: URL params > App state > localStorage > pendingOrderData
        const deviceId = deviceIdFromUrl || deviceIdFromState || deviceIdFromStorage || deviceIdFromPending
        console.log('PaymentSuccessScreen - Device ID resolution:', {
          fromUrl: deviceIdFromUrl,
          fromState: deviceIdFromState, 
          fromStorage: deviceIdFromStorage,
          fromPending: deviceIdFromPending,
          final: deviceId
        })
        
        // Prepare order data with Chinese API information
        const orderData = {
          pic: pendingOrderData.designImage
        }
        
        // Include Chinese API data if available (from app payment flow)
        if (pendingOrderData.selectedModelData?.chinese_model_id) {
          orderData.chinese_model_id = pendingOrderData.selectedModelData.chinese_model_id
          orderData.mobile_model_id = pendingOrderData.selectedModelData.chinese_model_id
        }
        
        // Get mobile_shell_id from direct property or from selectedModelData as fallback
        const mobileShellId = pendingOrderData.mobile_shell_id || pendingOrderData.selectedModelData?.mobile_shell_id
        if (mobileShellId) {
          orderData.mobile_shell_id = mobileShellId
          console.log('PaymentSuccessScreen - Using mobile_shell_id:', mobileShellId)
        } else {
          console.warn('PaymentSuccessScreen - No mobile_shell_id found in pendingOrderData')
        }
        
        // Always include device_id if available from any source
        if (deviceId) {
          orderData.device_id = deviceId
          console.log('PaymentSuccessScreen - Using device_id:', deviceId)
        } else {
          console.warn('PaymentSuccessScreen - No device_id found from any source')
        }
        
        // CRITICAL FIX: Read stored payment data correctly (PaymentScreen stores directly, not nested)
        if (pendingOrderData.paymentThirdId) {
          orderData.third_id = pendingOrderData.paymentThirdId
          console.log('PaymentSuccessScreen - Using stored paymentThirdId:', pendingOrderData.paymentThirdId)
        } else if (deviceId) {
          // Warn if device_id exists but no payment data - this will cause duplicate payData
          console.warn('PaymentSuccessScreen - CRITICAL: device_id exists but no stored paymentThirdId - backend will create duplicate payData call')
        }
        
        if (pendingOrderData.chinesePaymentId) {
          orderData.chinese_payment_id = pendingOrderData.chinesePaymentId
          console.log('PaymentSuccessScreen - Using stored chinesePaymentId:', pendingOrderData.chinesePaymentId)
        } else if (deviceId) {
          console.warn('PaymentSuccessScreen - WARNING: device_id exists but no stored chinesePaymentId')
        }
        
        console.log('Sending order data to backend:', orderData)
        console.log('mobile_shell_id in order data:', orderData?.mobile_shell_id)
        
        // Process payment success with backend
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/process-payment-success`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            order_data: orderData
          }),
        })

        let result
        if (!response.ok) {
          const errorText = await response.text()
          console.error('Backend payment processing had issues:', response.status, errorText)
          
          // CRITICAL FIX: For 503 errors (Chinese API failures), don't show fake success
          // These are order fulfillment failures that need user attention
          if (response.status === 503) {
            console.error('PaymentSuccessScreen - Chinese API integration failed - order not queued for printing')
            throw new Error(`Order processing failed: ${errorText}. Your payment was successful but the order could not be queued for printing. Please contact support with session ID: ${sessionId}`)
          } else if (response.status >= 500) {
            // Other server errors - also don't fake success 
            throw new Error(`Server error during order processing: ${errorText}. Please contact support with session ID: ${sessionId}`)
          } else {
            // For 4xx errors, might be recoverable - show generic error
            throw new Error(`Order processing error: ${errorText}. Please try again or contact support.`)
          }
        } else {
          result = await response.json()
          console.log('Payment processing successful:', result)
        }
        
        // Combine order data with payment result
        const completeOrderData = {
          ...pendingOrderData,
          orderData: result
        }
        
        setOrderData(completeOrderData)
        
        // Clear pending order from localStorage
        localStorage.removeItem('pendingOrder')
        
        // Reset AI credits after successful payment
        actions.setAiCredits(4)
        
        // Skip payment success screen and go directly to order confirmed
        navigate('/order-confirmed', { 
          state: completeOrderData
        })
        return
        
      } catch (err) {
        console.error('Payment processing error:', err)
        setError(err.message)
      } finally {
        setIsProcessing(false)
      }
    }

    processPayment()
  }, [location.search])

  const handleContinue = () => {
    if (orderData) {
      navigate('/order-confirmed', { 
        state: orderData
      })
    }
  }

  const handleBack = () => {
    navigate('/')
  }

  if (isProcessing) {
    return (
      <div className="screen-container" style={{ background: '#FFFFFF' }}>
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-400 mx-auto mb-4"></div>
            <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Processing Payment...</h1>
            <p className="text-gray-600">Please wait while we confirm your payment</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="screen-container" style={{ background: '#FFFFFF' }}>
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-red-500 text-2xl">✕</span>
            </div>
            <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Payment Error</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={handleBack}
              className="px-6 py-3 bg-pink-400 text-white rounded-full font-semibold"
            >
              Return Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            <span className="text-green-500 text-2xl">✓</span>
          </div>
          <h1 className="text-2xl font-bold text-[#2F3842] mb-2">Payment Successful!</h1>
          <p className="text-gray-600 mb-6">Your payment has been processed successfully</p>
          
          {orderData?.orderData && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
              <h3 className="font-semibold mb-2">Order Details</h3>
              <p className="text-sm text-gray-600">Order ID: {orderData.orderData.order_id}</p>
              <p className="text-sm text-gray-600">Payment ID: {orderData.orderData.payment_id}</p>
              <p className="text-sm text-gray-600">Amount: £{orderData.price?.toFixed(2)}</p>
            </div>
          )}
          
          <button
            onClick={handleContinue}
            className="px-6 py-3 bg-pink-400 text-white rounded-full font-semibold"
          >
            View Order Status
          </button>
        </div>
      </div>
    </div>
  )
}

export default PaymentSuccessScreen