import React from 'react'
// Trigger deployment - admin dashboard once again
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import Brands from './pages/Brands'
import Models from './pages/Models'
import Templates from './pages/Templates'
import Settings from './pages/Settings'
import Images from './pages/Images'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/brands" element={<Brands />} />
            <Route path="/models" element={<Models />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/images" element={<Images />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  )
}

export default App