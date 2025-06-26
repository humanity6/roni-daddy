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
import PhoneBackPreviewScreen from './screens/PhoneBackPreviewScreen'
import RetryScreen from './screens/RetryScreen'
import PaymentScreen from './screens/PaymentScreen'
import QueueScreen from './screens/QueueScreen'
import CompletionScreen from './screens/CompletionScreen'
import QRScreen from './screens/QRScreen'
import ReadyToPayScreen from './screens/ReadyToPayScreen'
import OrderConfirmedScreen from './screens/OrderConfirmedScreen'
import MultiOrderQueueScreen from './screens/MultiOrderQueueScreen'

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
          <Route path="/phone-back-preview" element={<PhoneBackPreviewScreen />} />
          <Route path="/retry" element={<RetryScreen />} />
          <Route path="/payment" element={<PaymentScreen />} />
          <Route path="/ready-to-pay" element={<ReadyToPayScreen />} />
          <Route path="/queue" element={<QueueScreen />} />
          <Route path="/multi-order-queue" element={<MultiOrderQueueScreen />} />
          <Route path="/order-confirmed" element={<OrderConfirmedScreen />} />
          <Route path="/completion" element={<CompletionScreen />} />
        </Routes>
      </div>
    </AppStateProvider>
  )
}

export default App 