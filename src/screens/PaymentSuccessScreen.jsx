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
        const urlParams = new URLSearchParams(location.search)
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
        
        if (pendingOrderData.chinesePaymentData?.third_id) {
          orderData.third_id = pendingOrderData.chinesePaymentData.third_id
        }
        
        if (pendingOrderData.chinesePaymentData?.chinese_payment_id) {
          orderData.chinese_payment_id = pendingOrderData.chinesePaymentData.chinese_payment_id
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
          
          // If payment was successful but backend had issues, still show success to user
          // The payment went through Stripe successfully, so don't confuse the user
          result = {
            success: true,
            message: 'Payment successful - order may be delayed due to processing issues',
            queue_number: 'TMP001',
            warning: true
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