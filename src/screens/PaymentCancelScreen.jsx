import { ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const PaymentCancelScreen = () => {
  const navigate = useNavigate()

  const handleBack = () => {
    navigate(-1) // Go back to previous screen (payment screen)
  }

  const handleHome = () => {
    navigate('/')
  }

  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Pastel blobs background */}
      <div className="absolute bottom-[-140px] left-[-100px] w-[220px] h-[320px] bg-[#DFF4FF] rounded-[70%_30%_65%_35%/55%_45%_60%_40%] opacity-70"></div>
      <div className="absolute bottom-[-140px] right-[-100px] w-[220px] h-[320px] bg-[#F8D9DE] rounded-[35%_65%_40%_60%/60%_40%_55%_45%] opacity-70"></div>

      <div className="relative z-10 flex flex-col items-center justify-between px-6 py-12 min-h-screen">
        {/* Back Arrow */}
        <div className="w-full flex justify-start mb-4">
          <button
            onClick={handleBack}
            className="w-12 h-12 rounded-full bg-white border-4 border-blue-300 flex items-center justify-center active:scale-95 transition-transform shadow-lg"
          >
            <ArrowLeft size={20} className="text-blue-500" />
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          {/* Cancel Icon */}
          <div className="w-20 h-20 rounded-full bg-orange-100 flex items-center justify-center mb-6">
            <span className="text-orange-500 text-3xl">⚠</span>
          </div>

          {/* Title */}
          <h1 
            className="text-4xl font-black text-[#2F3842] mb-4"
            style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}
          >
            PAYMENT CANCELLED
          </h1>

          {/* Description */}
          <p 
            className="text-gray-600 text-lg mb-8 max-w-md"
            style={{ fontFamily: 'PoppinsLight, Poppins, sans-serif' }}
          >
            Your payment was cancelled. Don't worry - no charges were made to your card.
          </p>

          {/* Action Buttons */}
          <div className="space-y-4">
            <button
              onClick={handleBack}
              className="w-full px-8 py-4 bg-pink-400 text-white rounded-full font-semibold text-lg shadow-lg transition-transform active:scale-95"
            >
              Try Payment Again
            </button>
            
            <button
              onClick={handleHome}
              className="w-full px-8 py-4 bg-gray-200 text-gray-700 rounded-full font-semibold text-lg transition-transform active:scale-95"
            >
              Start Over
            </button>
          </div>
        </div>

        {/* Bottom spacer */}
        <div></div>
      </div>
    </div>
  )
}

export default PaymentCancelScreen