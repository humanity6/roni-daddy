import { ArrowLeft } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'

const PaymentScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()

  // Expecting these values from previous step, otherwise use sensible defaults
  const {
    designImage,
    price = 18.99,
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

  const handleBack = () => {
    navigate(-1)
  }

  const handlePay = () => {
    navigate('/order-confirmed', { state: { designImage, price } })
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
          <div className="relative w-64 h-[420px] mx-auto">
            {/* Dynamic design image */}
            <div className="phone-case-content">
              {designImage ? (
                <img src={designImage} alt="Your design" className="phone-case-image" />
              ) : (
                <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 text-sm">No design</div>
              )}
            </div>
            {/* Template overlay */}
            <img
              src="/phone-template.png"
              alt="Phone template"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />
          </div>

          {/* Price */}
          <div className="mt-10">
            <div className="px-8 py-3 rounded-full" style={{ background: '#DFF4FF' }}>
              <p
                className="text-4xl font-semibold text-[#2F3842]"
                style={{ fontFamily: 'Cubano, sans-serif' }}
              >
                £{price.toFixed(2)}
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
                className="w-20 h-20 rounded-full flex items-center justify-center bg-pink-400 text-white font-semibold"
              >
                Pay
              </button>
            </div>
          </div>
        </div>

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