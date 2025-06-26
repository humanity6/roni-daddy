const OrderConfirmedScreen = () => {
  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Pink blob – top-left (smaller, tight in corner) */}
      <div className="absolute top-[-160px] left-[-220px] w-[520px] h-[360px] bg-[#FCDDE7] rounded-[75%_45%_60%_25%/60%_80%_35%_55%] opacity-70"></div>
      {/* Blue blob – bottom-right (smaller, tight in corner) */}
      <div className="absolute bottom-[-160px] right-[-240px] w-[520px] h-[360px] bg-[#CBE8F4] rounded-[60%_55%_70%_40%/40%_35%_55%_70%] opacity-70"></div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-between px-6 py-12">
        {/* Header */}
        <div className="text-center mt-8">
          <h1 
            className="text-5xl md:text-6xl font-black text-[#2F3842] mb-8 outline-none"
            style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}
          >
            ORDER CONFIRMED!
          </h1>
        </div>

        {/* Main Content Area */}
        <div className="flex w-full max-w-2xl mx-auto items-center justify-center">
          {/* Outer card with thick green border */}
          <div className="flex flex-col items-center justify-center gap-8 w-full bg-white rounded-[80px] border-[48px] border-[#D4EFC1] p-8 relative">
            
            {/* Main message – left-aligned */}
            <div className="w-full">
              <h2 
                className="text-left text-4xl md:text-5xl font-black text-[#2F3842] mb-4"
                style={{ fontFamily: 'Cubano, Arial Black, sans-serif' }}
              >
                HANG TIGHT!
              </h2>
              <p 
                className="text-left text-[#374151] text-xl md:text-2xl font-light"
                style={{ fontFamily: 'Poppins, sans-serif' }}
              >
                YOUR CASE IS BEING <span className="font-black">PRINTED</span>
              </p>
            </div>

            {/* Progress indicator and order number */}
            <div className="flex items-center justify-between w-full">
              {/* Green oval – resized with slightly larger dash */}
              <div className="w-40 h-20 bg-[#D4EFC1] rounded-full flex items-center justify-center">
                <div className="w-20 h-4 bg-white rounded-full"></div>
              </div>

              {/* Order number */}
              <div className="text-center">
                <p className="text-[#2F3842] text-6xl md:text-7xl font-black" style={{ fontFamily: 'Redminer, Cubano, Arial Black, sans-serif' }}>
                  9630
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom spacer */}
        <div></div>
      </div>
    </div>
  )
}

export default OrderConfirmedScreen 