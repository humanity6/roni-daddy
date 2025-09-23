import { Routes, Route, Navigate } from 'react-router-dom'
// Trigger deployment - mobile app please do
import { AppStateProvider } from './contexts/AppStateContext'
import PhoneBrandScreen from './screens/PhoneBrandScreen'
import IPhoneModelScreen from './screens/IPhoneModelScreen'
import GoogleModelScreen from './screens/GoogleModelScreen'
import SamsungModelScreen from './screens/SamsungModelScreen'
import CustomizeImageScreen from './screens/CustomizeImageScreen'
import TemplateSelectionScreen from './screens/TemplateSelectionScreen'
import PhonePreviewScreen from './screens/PhonePreviewScreen'
import TextInputScreen from './screens/TextInputScreen'
import FontSelectionScreen from './screens/FontSelectionScreen'
import TextColorSelectionScreen from './screens/TextColorSelectionScreen'
import BackgroundColorSelectionScreen from './screens/BackgroundColorSelectionScreen'
import QRScreen from './screens/QRScreen'
import ReadyToPayScreen from './screens/ReadyToPayScreen'
import OrderConfirmedScreen from './screens/OrderConfirmedScreen'
import MultiOrderQueueScreen from './screens/MultiOrderQueueScreen'
import FunnyToonScreen from './screens/FunnyToonScreen'
import FunnyToonGenerateScreen from './screens/FunnyToonGenerateScreen'
import PaymentScreen from './screens/PaymentScreen'
import FilmStripScreen from './screens/FilmStripScreen'
import FilmStripUploadScreen from './screens/FilmStripUploadScreen'
import MultiImageUploadScreen from './screens/MultiImageUploadScreen'
import RetroRemixScreen from './screens/RetroRemixScreen'
import GlitchScreen from './screens/GlitchScreen'
import GlitchProGenerateScreen from './screens/GlitchProGenerateScreen'
import CoverShootScreen from './screens/CoverShootScreen'
import CoverShootGenerateScreen from './screens/CoverShootGenerateScreen'
import RetroRemixGenerateScreen from './screens/RetroRemixGenerateScreen'
import PaymentSuccessScreen from './screens/PaymentSuccessScreen'
import PaymentCancelScreen from './screens/PaymentCancelScreen'
import VendingPaymentWaitingScreen from './screens/VendingPaymentWaitingScreen'
import VendingPaymentSuccessScreen from './screens/VendingPaymentSuccessScreen'

function App() {
  return (
    <AppStateProvider>
      <div className="App">
        <Routes>
          <Route path="/" element={<PhoneBrandScreen />} />
          <Route path="/qr" element={<QRScreen />} />
          <Route path="/phone-brand" element={<PhoneBrandScreen />} />
          <Route path="/iphone-model" element={<IPhoneModelScreen />} />
          <Route path="/google-model" element={<GoogleModelScreen />} />
          <Route path="/samsung-model" element={<SamsungModelScreen />} />
          <Route path="/customize-image" element={<CustomizeImageScreen />} />
          <Route path="/template-selection" element={<TemplateSelectionScreen />} />
          <Route path="/phone-preview" element={<PhonePreviewScreen />} />
          <Route path="/text-input" element={<TextInputScreen />} />
          <Route path="/font-selection" element={<FontSelectionScreen />} />
          <Route path="/text-color-selection" element={<TextColorSelectionScreen />} />
          <Route path="/background-color-selection" element={<BackgroundColorSelectionScreen />} />
          <Route path="/ready-to-pay" element={<ReadyToPayScreen />} />
          <Route path="/multi-order-queue" element={<MultiOrderQueueScreen />} />
          <Route path="/order-confirmed" element={<OrderConfirmedScreen />} />
          <Route path="/funny-toon" element={<FunnyToonScreen />} />
          <Route path="/funny-toon-generate" element={<FunnyToonGenerateScreen />} />
          <Route path="/ai-regenerate" element={<FunnyToonGenerateScreen />} />
          <Route path="/payment" element={<PaymentScreen />} />
          <Route path="/film-strip" element={<FilmStripScreen />} />
          <Route path="/film-strip-upload" element={<FilmStripUploadScreen />} />
          <Route path="/multi-image-upload" element={<MultiImageUploadScreen />} />
          <Route path="/retro-remix" element={<RetroRemixScreen />} />
          <Route path="/glitch" element={<GlitchScreen />} />
          <Route path="/glitch-pro-generate" element={<GlitchProGenerateScreen />} />
          <Route path="/cover-shoot" element={<CoverShootScreen />} />
          <Route path="/cover-shoot-generate" element={<CoverShootGenerateScreen />} />
          <Route path="/retro-remix-generate" element={<RetroRemixGenerateScreen />} />
          <Route path="/payment-success" element={<PaymentSuccessScreen />} />
          <Route path="/payment-cancel" element={<PaymentCancelScreen />} />
          <Route path="/vending-payment-waiting" element={<VendingPaymentWaitingScreen />} />
          <Route path="/vending-payment-success" element={<VendingPaymentSuccessScreen />} />
        </Routes>
      </div>
    </AppStateProvider>
  )
}

export default App 