import { Routes, Route, Navigate } from 'react-router-dom'
import { AppStateProvider } from './contexts/AppStateContext'
import WelcomeScreen from './screens/WelcomeScreen'
import PhoneBrandScreen from './screens/PhoneBrandScreen'
import IPhoneModelScreen from './screens/IPhoneModelScreen'
import GoogleModelScreen from './screens/GoogleModelScreen'
import SamsungModelScreen from './screens/SamsungModelScreen'
import TemplateSelectionScreen from './screens/TemplateSelectionScreen'
import PhonePreviewScreen from './screens/PhonePreviewScreen'
import TextInputScreen from './screens/TextInputScreen'
import FontSelectionScreen from './screens/FontSelectionScreen'
import TextColorSelectionScreen from './screens/TextColorSelectionScreen'
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
import CoverShootScreen from './screens/CoverShootScreen'
import GlitchScreen from './screens/GlitchScreen'
import FootyFanScreen from './screens/FootyFanScreen'
import FootyFanStyleScreen from './screens/FootyFanStyleScreen'
import FootyFanGenerateScreen from './screens/FootyFanGenerateScreen'

function App() {
  return (
    <AppStateProvider>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/welcome" replace />} />
          <Route path="/welcome" element={<WelcomeScreen />} />
          <Route path="/qr" element={<QRScreen />} />
          <Route path="/phone-brand" element={<PhoneBrandScreen />} />
          <Route path="/iphone-model" element={<IPhoneModelScreen />} />
          <Route path="/google-model" element={<GoogleModelScreen />} />
          <Route path="/samsung-model" element={<SamsungModelScreen />} />
          <Route path="/template-selection" element={<TemplateSelectionScreen />} />
          <Route path="/phone-preview" element={<PhonePreviewScreen />} />
          <Route path="/text-input" element={<TextInputScreen />} />
          <Route path="/font-selection" element={<FontSelectionScreen />} />
          <Route path="/text-color-selection" element={<TextColorSelectionScreen />} />
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
          <Route path="/cover-shoot" element={<CoverShootScreen />} />
          <Route path="/covershot" element={<CoverShootScreen />} />
          <Route path="/glitch" element={<GlitchScreen />} />
          <Route path="/footy-fan" element={<FootyFanScreen />} />
          <Route path="/footy-fan-style" element={<FootyFanStyleScreen />} />
          <Route path="/footy-fan-generate" element={<FootyFanGenerateScreen />} />
        </Routes>
      </div>
    </AppStateProvider>
  )
}

export default App 