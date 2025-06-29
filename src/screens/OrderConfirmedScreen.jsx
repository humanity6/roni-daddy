const OrderConfirmedScreen = () => {
  return (
    <div className="screen-container" style={{ background: '#FFFFFF' }}>
      {/* Bottom left small blue blob */}
      <div className="absolute bottom-[-140px] left-[-100px] w-[220px] h-[320px] bg-[#DFF4FF] rounded-[70%_30%_65%_35%/55%_45%_60%_40%] opacity-70"></div>
      {/* Bottom right small pink blob */}
      <div className="absolute bottom-[-140px] right-[-100px] w-[220px] h-[320px] bg-[#F8D9DE] rounded-[35%_65%_40%_60%/60%_40%_55%_45%] opacity-70"></div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-between px-6 py-12">
        {/* MOBILE LAYOUT (below 768px) */}
        <div className="md:hidden w-full flex flex-col items-center pt-8 space-y-8">
          {/* Blue cloud with confirmation text */}
          <div className="px-6 py-4" style={{ background:'#DFF4FF', borderRadius:'60% 40% 60% 40% / 45% 55% 45% 55%' }}>
            <h1 className="text-3xl font-black text-[#2F3842] leading-snug text-center" style={{ fontFamily:'Cubano, Arial Black, sans-serif' }}>
              ORDER<br/>CONFIRMED!
            </h1>
          </div>

          {/* Green order number pill */}
          <div className="px-10 py-2 bg-[#D4EFC1] rounded-full">
            <p className="text-4xl font-black text-[#2F3842]" style={{ fontFamily:'Redminer, Cubano, Arial Black, sans-serif' }}>9630</p>
          </div>

          {/* Phone-style rectangle card */}
          <div className="relative border-[24px] border-[#F8D9DE] rounded-[40px] flex flex-col items-start pt-10 pb-6 px-2 space-y-4 w-48">
            {/* Vertical oval inside top left */}
            <div className="absolute top-4 left-4 bg-[#F8D9DE] rounded-full flex items-center justify-center w-14 h-[88px]">
              <div className="bg-white rounded-full w-3 h-[40px]"></div>
            </div>

            {/* Camera/slot */}
            <div className="w-10 h-16 bg-white rounded-3xl"></div>

            {/* Text */}
            <div className="w-full leading-snug text-left pl-0">
              <p className="text-xl font-black text-[#2F3842] whitespace-nowrap" style={{ fontFamily:'Cubano, Arial Black, sans-serif', marginTop:'-2px' }}>HANG TIGHT!</p>
              <p className="text-[#374151] text-xl font-light" style={{ fontFamily:'PoppinsLight, Poppins, sans-serif', letterSpacing:'1.5px' }}>
                Your <span className="font-bold">case</span><br/>is being printed!
              </p>
            </div>
          </div>
        </div>

        {/* DESKTOP ORIGINAL LAYOUT (md+) */}
        <div className="hidden md:block w-full">
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
            <div className="flex flex-col items-center justify-center gap-8 w-full bg-white rounded-[80px] border-[60px] border-[#D4EFC1] p-7 relative">
              {/* Main message */}
              <div className="w-full">
                <h2 className="text-left text-4xl md:text-5xl font-black text-[#2F3842] mb-4" style={{ fontFamily:'Cubano, Arial Black, sans-serif' }}>HANG TIGHT!</h2>
                <p className="text-left text-[#374151] text-xl md:text-2xl font-light" style={{ fontFamily:'Poppins, sans-serif' }}>
                  YOUR CASE IS BEING <span className="font-black">PRINTED</span>
                </p>
              </div>

              {/* Progress indicator and order number */}
              <div className="flex items-center justify-between w-full">
                <div className="w-40 h-28 bg-[#D4EFC1] rounded-full flex items-center justify-center">
                  <div className="w-16 h-5 bg-white rounded-full"></div>
                </div>
                <div className="text-center">
                  <p className="text-[#2F3842] text-6xl md:text-7xl font-black" style={{ fontFamily:'Redminer, Cubano, Arial Black, sans-serif' }}>9630</p>
                </div>
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